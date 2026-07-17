#!/usr/bin/env python3
"""ADR workflow tooling: scaffolding, validation, and git-hook checks.

Mechanically enforces the ADR-driven workflow (adopted as ADR-0001 in
governed repos): atomic immutable ADRs as the sole behavioural spec,
strict spec/code commit separation, and code<->ADR traceability via
inline tags. Pure stdlib; requires only python3 and git.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from fnmatch import fnmatch
from pathlib import Path

ADR_DIR = "docs/adr"
TOOL_REPO_PATH = "tools/adr/adr_tools.py"
# Paths listed here (one glob or path prefix per line, # comments) are
# skipped by the reference scan and coverage. For prose that must name a
# superseded ADR (changelogs, postmortems), which would otherwise fail the
# stale-ref check forever. Never list code here.
REFIGNORE_PATH = "tools/adr/refignore"
HOOK_MARKER = "# installed by adr_tools (adr-workflow)"

ADR_FILENAME_RE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
TITLE_RE = re.compile(r"^# ADR-(\d{4}): \S")
DATE_RE = re.compile(r"^- Date: \d{4}-\d{2}-\d{2}\s*$", re.M)
SUPERSEDES_RE = re.compile(r"^- Supersedes: (ADR-\d{4}(?:, ADR-\d{4})*)\s*$", re.M)
STATUS_LINE_RE = re.compile(r"^[-* ]*Status\s*:", re.M | re.I)
REF_RE = re.compile(r"ADR-(\d{4})")
IMPLEMENTS_RE = re.compile(r"^Implements:\s*(ADR-\d{4}(?:,\s*ADR-\d{4})*)\s*$", re.M)
EXEMPT_RE = re.compile(r"^Exempt:\s*(bugfix|refactor|chore|tests)\s*$", re.M)
REQUIRED_SECTIONS = ("## Context", "## Decision", "## Consequences")

# Directories that never contain governed code, so ADR references inside
# them are neither required nor checked.
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv",
             "venv", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
             ".air", ".claude", ".idea", ".vscode"}

# Paths that may exist in a repo without disqualifying it as greenfield.
GREENFIELD_ALLOW = ("readme", "license", ".gitignore", ".gitattributes",
                    ".editorconfig", ".github/", ".air/", ".claude/",
                    ".vscode/", "docs/adr/", "tools/adr/")


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def run(*args, check=False):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"command failed: {' '.join(args)}\n{r.stderr.strip()}")
    return r


def repo_root():
    r = run("git", "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        die("not inside a git repository")
    return Path(r.stdout.strip())


def has_head():
    return run("git", "rev-parse", "--verify", "-q", "HEAD").returncode == 0


class Adr:
    def __init__(self, name):
        self.name = name              # filename, e.g. 0007-token-refresh.md
        self.number = None            # int
        self.title = None             # from the H1, without the ADR-NNNN prefix
        self.text = ""                # full file content
        self.supersedes = []          # list of ints
        self.problems = []            # lint problems (strings)
        self.superseded_by = None     # int, computed across the set
        self.code_refs = 0            # computed by the code scan

    @property
    def id(self):
        return f"ADR-{self.number:04d}" if self.number is not None else self.name


def parse_adr(name, text):
    """Lint one ADR file's name and content; returns an Adr."""
    adr = Adr(name)
    m = ADR_FILENAME_RE.match(name)
    if not m:
        adr.problems.append(
            "filename must be NNNN-kebab-case-slug.md (nothing else lives in "
            "docs/adr/ — no README, no index; status and navigation come from "
            "`adr_tools.py status`)")
        return adr
    adr.number = int(m.group(1))

    adr.text = text
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines or not TITLE_RE.match(lines[0]):
        adr.problems.append("first line must be `# ADR-NNNN: Title`")
    else:
        if int(TITLE_RE.match(lines[0]).group(1)) != adr.number:
            adr.problems.append("title number does not match filename number")
        adr.title = lines[0].split(": ", 1)[1].strip()
    if not DATE_RE.search(text):
        adr.problems.append("missing `- Date: YYYY-MM-DD` line")
    if STATUS_LINE_RE.search(text):
        adr.problems.append(
            "remove the Status line: status is computed from supersession, "
            "never written (a written status would have to be edited later, "
            "violating immutability)")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            adr.problems.append(f"missing required section `{section}`")
    sm = SUPERSEDES_RE.search(text)
    if sm:
        adr.supersedes = [int(n) for n in REF_RE.findall(sm.group(1))]
    return adr


def check_adr_set(adrs):
    """Cross-file consistency checks. Returns a list of error strings."""
    errors = []
    for a in adrs:
        for p in a.problems:
            errors.append(f"{ADR_DIR}/{a.name}: {p}")

    numbered = [a for a in adrs if a.number is not None]
    by_num = {}
    for a in numbered:
        if a.number in by_num:
            errors.append(f"duplicate ADR number {a.id} "
                          f"({by_num[a.number].name} and {a.name})")
        by_num[a.number] = a
    if numbered:
        nums = sorted(by_num)
        expected = list(range(1, max(nums) + 1))
        missing = sorted(set(expected) - set(nums))
        if nums[0] != 1 or missing:
            errors.append(
                f"ADR numbering must be contiguous from 0001; missing: "
                f"{', '.join(f'{n:04d}' for n in missing) or '0001'}")

    superseders = {}  # target number -> superseding Adr
    for a in numbered:
        for t in a.supersedes:
            if t == a.number:
                errors.append(f"{a.id} supersedes itself")
                continue
            if t not in by_num:
                errors.append(f"{a.id} supersedes ADR-{t:04d}, which does not exist")
                continue
            if t > a.number:
                errors.append(f"{a.id} supersedes the later ADR-{t:04d}; "
                              "supersession only points backwards")
                continue
            if t in superseders:
                errors.append(
                    f"ADR-{t:04d} is superseded twice ({superseders[t].id} and "
                    f"{a.id}); supersede the live successor instead")
                continue
            superseders[t] = a
            by_num[t].superseded_by = a.number
    return errors


def load_adrs_worktree(root):
    adr_dir = root / ADR_DIR
    adrs = []
    if adr_dir.is_dir():
        for p in sorted(adr_dir.iterdir()):
            if p.is_file():
                adrs.append(parse_adr(p.name, p.read_text(encoding="utf-8",
                                                          errors="replace")))
    return adrs


def load_adrs_index():
    """Load the ADR set as it will exist after the pending commit (git index)."""
    r = run("git", "ls-files", "--", ADR_DIR)
    adrs = []
    for path in r.stdout.splitlines():
        blob = run("git", "show", f":{path}")
        if blob.returncode == 0:
            adrs.append(parse_adr(Path(path).name, blob.stdout))
    return adrs


def is_spec_path(path):
    return path.startswith(ADR_DIR + "/")


def load_refignore(root):
    p = root / REFIGNORE_PATH
    if not p.is_file():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")]


def ref_ignored(relpath, patterns):
    return any(fnmatch(relpath, pat)
               or relpath.startswith(pat.rstrip("/") + "/")
               for pat in patterns)


TEST_DIRS = {"test", "tests", "spec", "specs", "__tests__"}


def is_test_path(relpath):
    """Heuristic over common test layouts and naming conventions.

    Only feeds the informational test-coverage report in `coverage`, so a
    miss under-reports there and nothing else.
    """
    parts = relpath.split("/")
    if any(p.lower() in TEST_DIRS for p in parts[:-1]):
        return True
    name = parts[-1]
    stem = name.split(".", 1)[0]
    return (stem.startswith("test_") or stem.endswith(("_test", "Test", "_spec"))
            or ".test." in name or ".spec." in name)


def scan_text_for_refs(text):
    refs = []
    for i, line in enumerate(text.splitlines(), 1):
        refs.extend((int(n), i) for n in REF_RE.findall(line))
    return refs


def scan_code_refs(root, adrs):
    """Walk the worktree (excluding docs/adr) collecting ADR-NNNN references.

    Returns error strings for references to nonexistent or superseded ADRs
    and increments each ADR's code_refs count.
    """
    by_num = {a.number: a for a in adrs if a.number is not None}
    errors = []
    ignore = load_refignore(root)
    adr_abs = (root / ADR_DIR).resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if Path(dirpath).resolve() == adr_abs:
            dirnames[:] = []
            continue
        for fn in filenames:
            fp = Path(dirpath) / fn
            relpath = os.path.relpath(fp, root).replace("\\", "/")
            if ref_ignored(relpath, ignore):
                continue
            try:
                if fp.stat().st_size > 1_000_000:
                    continue
                text = fp.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            errors.extend(check_ref_targets(relpath, scan_text_for_refs(text),
                                            by_num))
    return errors


def check_ref_targets(relpath, refs, by_num):
    errors = []
    for num, lineno in refs:
        target = by_num.get(num)
        if target is None:
            errors.append(f"{relpath}:{lineno}: references ADR-{num:04d}, "
                          "which does not exist")
        elif target.superseded_by is not None:
            errors.append(
                f"{relpath}:{lineno}: references superseded ADR-{num:04d}; "
                f"this code is stale — bring it in line with "
                f"ADR-{target.superseded_by:04d} and update the tag")
        else:
            target.code_refs += 1
    return errors


def audit_history():
    """Re-check the hook-enforced commit rules across committed history.

    Hooks are per-clone and easy to skip, so a clone without them can land
    ungoverned commits that nothing else would ever surface; this audit is
    what CI runs to backstop them. Audits from the first ADR commit onward,
    which leaves pre-adoption history in onboarded repos alone.
    """
    first = run("git", "log", "--reverse", "--format=%H", "--", ADR_DIR)
    if not first.stdout.split():
        return []
    adoption = first.stdout.split()[0]
    fmt = "--format=%x1e%H%x1f%B%x1f"
    out = run("git", "log", "-1", fmt, "--name-only", adoption).stdout
    out += run("git", "log", "--no-merges", fmt, "--name-only",
               f"{adoption}..HEAD").stdout
    errors = []
    for chunk in out.split("\x1e"):
        if chunk.count("\x1f") < 2:
            continue
        sha, body, files_blob = chunk.split("\x1f", 2)
        sha = sha.strip()
        subject = body.strip().splitlines()[0] if body.strip() else ""
        if subject.startswith(("fixup!", "squash!", "Revert")):
            continue
        files = [f for f in files_blob.splitlines() if f.strip()]
        spec = [f for f in files if is_spec_path(f)]
        code = [f for f in files if not is_spec_path(f)]
        if spec and code:
            errors.append(
                f"commit {sha[:12]} ({subject[:60]}) mixes spec and code; "
                "the hooks were bypassed or not installed when it was made")
        elif code and not (IMPLEMENTS_RE.search(body)
                           or EXEMPT_RE.search(body)):
            errors.append(
                f"commit {sha[:12]} ({subject[:60]}) is a code commit with "
                "no Implements:/Exempt: trailer; the hooks were bypassed or "
                "not installed when it was made")
    return errors


def cmd_validate(args):
    root = repo_root()
    adrs = load_adrs_worktree(root)
    errors = check_adr_set(adrs)
    warnings = []

    if has_head():
        errors.extend(audit_history())
        # Immutability audit: an ADR file must never be modified or deleted
        # after the commit that introduced it.
        for a in adrs:
            r = run("git", "log", "--diff-filter=MDR", "--format=%h", "--",
                    f"{ADR_DIR}/{a.name}")
            shas = r.stdout.split()
            if shas:
                errors.append(
                    f"{ADR_DIR}/{a.name}: git history shows post-commit "
                    f"mutation in {', '.join(shas)}; ADRs are immutable — "
                    "supersede instead of editing")
        r = run("git", "diff", "HEAD", "--name-status", "--", ADR_DIR)
        for line in r.stdout.splitlines():
            status, _, path = line.partition("\t")
            if status.rstrip("0123456789") in ("M", "D", "R"):
                errors.append(f"{path}: uncommitted modification/deletion of a "
                              "committed ADR; revert it and supersede instead")

    errors.extend(scan_code_refs(root, adrs))
    for a in adrs:
        if a.number is not None and a.superseded_by is None and a.code_refs == 0:
            warnings.append(
                f"{a.id} is live but no code references it; either it is not "
                "yet implemented or it is a process decision (fine)")

    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"warning: {w}")
    if not errors:
        live = sum(1 for a in adrs if a.number and a.superseded_by is None)
        print(f"ok: {len(adrs)} ADRs ({live} live), no errors")
    return 1 if errors else 0


def staged_changes():
    """Returns [(status, path)] for the pending commit; renames yield both paths."""
    r = run("git", "diff", "--cached", "--name-status")
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        status = parts[0].rstrip("0123456789")
        for p in parts[1:]:
            out.append((status, p))
    return out


def cmd_check_staged(args):
    changes = staged_changes()
    if not changes:
        return 0
    errors = []

    spec = [(s, p) for s, p in changes if is_spec_path(p)]
    code = [(s, p) for s, p in changes if not is_spec_path(p)]
    if spec and code:
        errors.append(
            "mixed commit: a commit must be either a spec commit (only "
            f"{ADR_DIR}/) or a code commit (no {ADR_DIR}/), never both. "
            "Commit the ADRs first, then the code.\n"
            + "".join(f"    spec: {p}\n" for _, p in spec)
            + "".join(f"    code: {p}\n" for _, p in code))

    for status, path in spec:
        if status != "A":
            errors.append(
                f"{path}: staged change has status {status}; committed ADRs "
                "are immutable and append-only — write a superseding ADR "
                "instead of modifying or deleting")

    # Consistency of the post-commit ADR set (the git index).
    adrs = load_adrs_index()
    errors.extend(check_adr_set(adrs))
    by_num = {a.number: a for a in adrs if a.number is not None}

    # Staged code must not reference nonexistent or superseded ADRs.
    ignore = load_refignore(repo_root())
    for status, path in code:
        if status == "D" or ref_ignored(path, ignore):
            continue
        blob = run("git", "show", f":{path}")
        if blob.returncode != 0:
            continue
        try:
            text = blob.stdout
        except Exception:
            continue
        errors.extend(check_ref_targets(path, scan_text_for_refs(text), by_num))

    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        print("\ncommit rejected by adr_tools check-staged", file=sys.stderr)
    return 1 if errors else 0


def cmd_check_msg(args):
    msg = Path(args.msgfile).read_text(encoding="utf-8", errors="replace")
    body = "\n".join(l for l in msg.splitlines() if not l.startswith("#"))
    first = body.strip().splitlines()[0] if body.strip() else ""
    if first.startswith(("Merge", "fixup!", "squash!", "Revert")):
        return 0
    changes = staged_changes()
    if not changes or all(is_spec_path(p) for _, p in changes):
        return 0  # spec commits need no trailer; the ADRs are the authority

    imp = IMPLEMENTS_RE.search(body)
    exempt = EXEMPT_RE.search(body)
    if not imp and not exempt:
        print(
            "ERROR: code commit is missing its authority trailer.\n"
            "Every code commit must declare why it is allowed to change "
            "behaviour-adjacent files:\n"
            "  Implements: ADR-NNNN[, ADR-NNNN]   (implements specified behaviour)\n"
            "  Exempt: bugfix|refactor|chore|tests (no specified-behaviour change)\n"
            "bugfix = restoring conformance with a live ADR (cite it in the "
            "body); refactor = behaviour-preserving; chore = tooling/deps/"
            "formatting; tests = verifying already-specified behaviour.",
            file=sys.stderr)
        return 1
    adrs = load_adrs_index()
    check_adr_set(adrs)  # populates superseded_by
    by_num = {a.number: a for a in adrs if a.number is not None}
    if exempt and exempt.group(1) == "bugfix":
        # A bugfix claims the code violated some live ADR; requiring the
        # citation keeps bugfix from being the easy path around the spec
        # loop. It cannot verify the judgment, only force the claim.
        cited = [int(n) for n in REF_RE.findall(body)]
        if not any(by_num.get(n) and by_num[n].superseded_by is None
                   for n in cited):
            print(
                "ERROR: Exempt: bugfix must cite the violated live ADR in "
                "the message body (the ADR the code is being brought back "
                "in line with; in an onboarded repo, the baseline ADR). If "
                "no live ADR is violated, this is not a bugfix — it is a "
                "spec change, refactor, chore, or tests.", file=sys.stderr)
            return 1
    if imp:
        for num in (int(n) for n in REF_RE.findall(imp.group(1))):
            a = by_num.get(num)
            if a is None:
                print(f"ERROR: trailer implements ADR-{num:04d}, which does not "
                      "exist; commit the spec first — spec always lands before "
                      "code", file=sys.stderr)
                return 1
            if a.superseded_by is not None:
                print(f"ERROR: trailer implements superseded ADR-{num:04d}; "
                      f"implement its successor ADR-{a.superseded_by:04d} "
                      "instead", file=sys.stderr)
                return 1
    return 0


def cmd_status(args):
    root = repo_root()
    adrs = load_adrs_worktree(root)
    errors = check_adr_set(adrs)
    scan_code_refs(root, adrs)
    for a in sorted((a for a in adrs if a.number is not None),
                    key=lambda a: a.number):
        title = a.name[5:-3].replace("-", " ")
        state = ("LIVE" if a.superseded_by is None
                 else f"superseded by ADR-{a.superseded_by:04d}")
        print(f"{a.id}  {state:<28} refs:{a.code_refs:<3} {title}")
    if errors:
        print(f"\n{len(errors)} consistency error(s); run `validate` for details")
        return 1
    return 0


def decision_section(text):
    m = re.search(r"^## Decision\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return ""
    # Template scaffolding (the restatement reminder) is not spec content.
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()


def cmd_spec(args):
    """Render the live spec as one document, on demand.

    A committed summary would be a second spec that can drift; a view
    generated from the live set cannot. Supersession-with-restatement is
    what makes concatenation sufficient: every live Decision section is
    complete on its own.
    """
    root = repo_root()
    adrs = load_adrs_worktree(root)
    errors = check_adr_set(adrs)
    live = sorted((a for a in adrs if a.number is not None
                   and a.superseded_by is None), key=lambda a: a.number)
    print("# Live specification\n")
    print(f"The Decision section of every live ADR ({len(live)} live of "
          f"{len(adrs)} total), in number order. Generated view; the files "
          f"in {ADR_DIR}/ are the authority. Do not commit this output.")
    for a in live:
        print(f"\n## {a.id}: {a.title or a.name}\n")
        print(decision_section(a.text) or "(empty Decision section)")
    if errors:
        print(f"\n{len(errors)} consistency error(s); run `validate` for "
              "details", file=sys.stderr)
        return 1
    return 0


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled"


def cmd_new(args):
    root = repo_root()
    adrs = load_adrs_worktree(root)
    nums = [a.number for a in adrs if a.number is not None]
    n = max(nums, default=0) + 1
    path = root / ADR_DIR / f"{n:04d}-{slugify(args.title)}.md"
    supersedes = ""
    restate = ""
    if args.supersedes:
        ids = ", ".join(f"ADR-{int(x):04d}"
                        for x in re.findall(r"\d+", args.supersedes))
        supersedes = f"- Supersedes: {ids}\n"
        restate = ("\n<!-- Supersession is total: restate every decision from "
                   "the superseded ADR(s) that still stands, so this ADR is "
                   "complete on its own. -->\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# ADR-{n:04d}: {args.title}\n\n"
        f"- Date: {date.today().isoformat()}\n"
        f"{supersedes}\n"
        f"## Context\n\n\n## Decision\n{restate}\n\n## Consequences\n\n",
        encoding="utf-8")
    print(f"created {path.relative_to(root)}")
    print("commit it alone (spec commit: only docs/adr/ files) once accepted")
    return 0


def install_hooks(root):
    hooks_dir = root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for name, cmd in (("pre-commit", f'exec python3 "{TOOL_REPO_PATH}" check-staged'),
                      ("commit-msg", f'exec python3 "{TOOL_REPO_PATH}" check-msg "$1"')):
        hook = hooks_dir / name
        if hook.exists() and HOOK_MARKER not in hook.read_text(errors="replace"):
            backup = hook.with_suffix(".bak")
            shutil.move(hook, backup)
            print(f"existing {name} hook moved to {backup.name}")
        hook.write_text(f"#!/bin/sh\n{HOOK_MARKER}\n{cmd}\n", encoding="utf-8")
        hook.chmod(0o755)
        print(f"installed .git/hooks/{name}")


def cmd_install_hooks(args):
    root = repo_root()
    if not (root / TOOL_REPO_PATH).exists():
        die(f"{TOOL_REPO_PATH} not found; run `init` first or copy the tool there")
    install_hooks(root)
    return 0


ADR_0001 = """\
# ADR-0001: Adopt ADR-driven development

- Date: {today}

## Context

This repository is agent-first: any agent or human must be able to determine
what the system is supposed to do by reading its Architecture Decision
Records, without reading the code. That guarantee only holds if every
behaviour is specified before it is implemented, and if the record of
decisions can be trusted never to have been rewritten.

## Decision

Adopt the ADR-driven workflow for this repository:

1. ADRs under `docs/adr/` are the sole specification of behaviour. The live
   specification is the set of ADRs that no other ADR supersedes.
2. Each ADR is atomic (one independently supersedable decision) and immutable
   once committed. ADR files are never modified or deleted.
3. Changing a decision means writing a new ADR with a `Supersedes:` line.
   Supersession is total: the new ADR restates any decisions from the old one
   that still stand, so it is complete on its own.
4. An ADR's status is computed from supersession references, never written
   into the file.
5. Code implementing a decision carries an inline `ADR-NNNN` tag in a comment
   at the implementing unit, and a test verifying a decision carries the same
   tag. Comments explain why behaviour exists (including the ADR reference),
   never what the code does.
6. No code may implement behaviour that no live ADR specifies.
7. Every commit is either a spec commit (touching only `docs/adr/`) or a code
   commit (touching nothing in `docs/adr/`), never both. Spec commits land
   before the code commits that implement them.
8. Code commits carry a trailer declaring their authority: either
   `Implements: ADR-NNNN` or `Exempt: bugfix|refactor|chore|tests`.
9. The tooling at `tools/adr/adr_tools.py` and the git hooks it installs
   enforce these rules mechanically.

## Consequences

Every behaviour is traceable to a decision and every decision to its context.
Specifying before implementing adds a step to every behavioural change; in
exchange, the specification can never drift from the code, and superseding an
ADR mechanically surfaces every piece of code that must migrate.
"""


# Assembled at runtime so this file carries no scannable reference to the
# baseline: graduation supersedes it, and a literal id here would then fail
# validate as a stale code ref in every graduated repo. (Literal ADR-0001
# refs stay: the tooling implements the adoption decision, and superseding
# that decision SHOULD flag this file for migration.)
BASELINE_ID = "ADR-" + "0002"

BASELINE_ADR = """\
# {bid}: Accept pre-adoption behaviour as the provisional baseline

- Date: {today}

## Context

This repository adopted ADR-driven development (ADR-0001) with an existing
codebase. Its behaviour predates the ADR set, and the original rationale for
most of its decisions is unrecorded. Specifying everything before adopting
would take unbounded effort, and ADRs reverse-engineered in bulk would need
invented context, making the record untrustworthy from day one.

## Decision

All behaviour present in the code at commit {sha} is provisionally accepted.
For any given behaviour, the code at that commit is its specification until
a live ADR specifies that behaviour explicitly; from then on the ADR takes
precedence. New ADRs carve behaviour out of this baseline; they do not carry
a `Supersedes:` line pointing at it. Until this ADR is superseded, it
qualifies ADR-0001: the ADR set remains the root authority, but for
grandfathered behaviour it delegates to the code snapshot named above.

Changing grandfathered behaviour requires an ADR first, like any other spec
change. Restoring grandfathered code to its evident intent (a crash, an
off-by-one) is a bugfix citing this ADR in the commit body; a fix that
chooses between plausible behaviours is a spec change.

This ADR is superseded only when the live ADR set specifies the system's
behaviour completely and nothing remains grandfathered.

## Consequences

The repository guarantee is: every behaviour is either explicitly specified
by a live ADR or visibly grandfathered at commit {sha}, and grandfathered
behaviour cannot change without becoming specified. The record never lies,
but it admits what it does not know yet. Coverage grows along the code paths
that change; `adr_tools.py coverage` reports progress toward superseding
this ADR.
"""


def cmd_init(args):
    root = repo_root()
    baseline_sha = None
    if args.existing:
        if not has_head():
            die("--existing needs committed history; for an empty repo run "
                "plain `init`")
        baseline_sha = run("git", "rev-parse", "HEAD").stdout.strip()
        # Untracked files are fine (the tooling copy itself is one); only
        # tracked modifications mean behaviour differs from the pinned SHA.
        if run("git", "status", "--porcelain", "-uno").stdout.strip():
            print("warning: tracked files have uncommitted changes; the "
                  "baseline covers committed state only, so commit or stash "
                  "first if those changes carry behaviour")
    elif not args.force:
        tracked = run("git", "ls-files").stdout.splitlines()
        offending = [p for p in tracked
                     if not p.lower().startswith(GREENFIELD_ALLOW)]
        if offending:
            die("this repository already has committed files. Run `init "
                "--existing` to onboard it: pre-adoption behaviour is "
                "grandfathered under a baseline ADR and extracted into real "
                "ADRs as code changes. (`--force` skips this check and "
                "grandfathers nothing.) First offenders:\n  "
                + "\n  ".join(offending[:10]))

    (root / ADR_DIR).mkdir(parents=True, exist_ok=True)
    tool_dst = root / TOOL_REPO_PATH
    tool_dst.parent.mkdir(parents=True, exist_ok=True)
    if Path(__file__).resolve() != tool_dst.resolve():
        shutil.copyfile(__file__, tool_dst)
        print(f"copied tooling to {TOOL_REPO_PATH}")

    if not any((root / ADR_DIR).glob("*.md")):
        adr1 = root / ADR_DIR / "0001-adopt-adr-driven-development.md"
        adr1.write_text(ADR_0001.format(today=date.today().isoformat()),
                        encoding="utf-8")
        print(f"created {ADR_DIR}/{adr1.name}")
        if baseline_sha:
            adr2 = (root / ADR_DIR /
                    "0002-accept-pre-adoption-behaviour-as-baseline.md")
            adr2.write_text(
                BASELINE_ADR.format(bid=BASELINE_ID,
                                    today=date.today().isoformat(),
                                    sha=baseline_sha),
                encoding="utf-8")
            print(f"created {ADR_DIR}/{adr2.name} (baseline: {baseline_sha[:12]})")
    install_hooks(root)
    if baseline_sha:
        print(f"""
next steps (review first, then two commits, in this order):
  1. review ADR-0001 and the {BASELINE_ID} baseline with the user, then
     spec commit:  git add docs/adr && git commit -m "spec: adopt ADR-driven development with baseline"
  2. code commit:  git add tools && git commit -m "code: add workflow tooling" \\
                   -m "Implements: ADR-0001" """)
    else:
        print("""
next steps (two commits, in this order):
  1. spec commit:  git add docs/adr && git commit -m "spec: adopt ADR-driven development"
  2. code commit:  git add tools && git commit -m "code: add workflow tooling" \\
                   -m "Implements: ADR-0001" """)
    return 0


def cmd_coverage(args):
    """Report which tracked files carry ADR tags, and which live ADRs
    have no tagged test.

    Informational only, never an error: in an onboarded repo, untagged
    files are usually grandfathered under the baseline ADR, and a failing
    ratchet would just be the rejected specify-everything-up-front plan
    in disguise. Same for tests: some decisions are unobservable, and a
    hard test-per-ADR rule would only breed tautology tests.
    """
    root = repo_root()
    tracked = run("git", "-C", str(root), "ls-files").stdout.splitlines()
    ignore = load_refignore(root)
    tagged, untagged = [], []
    test_tagged = set()  # ADR numbers referenced from test files
    for relpath in tracked:
        if is_spec_path(relpath) or ref_ignored(relpath, ignore) \
                or any(part in SKIP_DIRS for part in relpath.split("/")):
            continue
        fp = root / relpath
        try:
            if not fp.is_file() or fp.stat().st_size > 1_000_000:
                continue
            text = fp.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        refs = REF_RE.findall(text)
        (tagged if refs else untagged).append(relpath)
        if refs and is_test_path(relpath):
            test_tagged.update(int(n) for n in refs)
    total = len(tagged) + len(untagged)
    if not total:
        print("no scannable tracked files")
        return 0
    print(f"{len(tagged)} of {total} scanned files carry ADR tags")
    if untagged:
        print("\nuntagged (grandfathered under the baseline ADR, or non-code):")
        for p in untagged:
            print(f"  {p}")

    adrs = load_adrs_worktree(root)
    check_adr_set(adrs)  # populates superseded_by
    live = sorted((a for a in adrs if a.number is not None
                   and a.superseded_by is None), key=lambda a: a.number)
    if live:
        untested = [a for a in live if a.number not in test_tagged]
        print(f"\n{len(live) - len(untested)} of {len(live)} live ADRs have "
              "a tagged test")
        if untested:
            print("no tagged test (fine for unobservable decisions — process, "
                  "tooling, structure):")
            for a in untested:
                print(f"  {a.id}  {a.name[5:-3].replace('-', ' ')}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--force", action="store_true")
    p.add_argument("--existing", action="store_true",
                   help="onboard an existing codebase: grandfather current "
                        "behaviour under a baseline ADR")
    p = sub.add_parser("new")
    p.add_argument("title")
    p.add_argument("--supersedes", help="comma-separated ADR numbers")
    sub.add_parser("validate")
    sub.add_parser("status")
    sub.add_parser("spec")
    sub.add_parser("coverage")
    sub.add_parser("check-staged")
    sub.add_parser("check-msg").add_argument("msgfile")
    sub.add_parser("install-hooks")
    args = ap.parse_args()
    fn = {"init": cmd_init, "new": cmd_new, "validate": cmd_validate,
          "status": cmd_status, "spec": cmd_spec, "coverage": cmd_coverage,
          "check-staged": cmd_check_staged, "check-msg": cmd_check_msg,
          "install-hooks": cmd_install_hooks}[args.cmd]
    sys.exit(fn(args))


if __name__ == "__main__":
    main()
