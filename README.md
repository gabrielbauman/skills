# skills

[Agent skills](https://agentskills.io) written by Gabriel Bauman and Claude.
Each skill lives in its own directory under `skills/` and can be installed
independently.

## Skills

| Skill | Description |
| --- | --- |
| [adr-workflow](skills/adr-workflow/) | ADR-driven development: atomic, immutable Architecture Decision Records as the sole behavioural spec, strict spec/code commit separation, inline ADR tags in code, and git-hook enforcement tooling (bundled in [scripts/](skills/adr-workflow/scripts/)). |
| [atomic-commits](skills/atomic-commits/) | Decide what each git commit should contain: one self-contained, reviewable change per commit. Covers splitting a mixed working tree into an ordered series with `git add -p`, when a split is artificial, and keeping discovered fixes out of feature commits. Pairs with scoped-commits, which covers the message. |
| [humanize](skills/humanize/) | Write prose that reads like a person wrote it, and strip AI tells from existing text: em-dash addiction, negative parallelism, inflated vocabulary, bold-first bullets, manufactured drama. Compact checklist by default, full trope catalog on demand. |
| [scoped-commits](skills/scoped-commits/) | Write commit messages in the [Scoped Commits](https://scopedcommits.com) style: `scope: description`, the way Linux, Go, Git, FreeBSD, and nixpkgs write their history. Includes a concise, plain-ASCII house style for the message text (no emoji, no em dashes, no filler). |

## Installation

**Claude Code (plugin marketplace)** — this repo is a plugin marketplace, so
each skill installs as a plugin and stays updateable:

```
/plugin marketplace add gabrielbauman/skills
/plugin install scoped-commits@gabrielbauman
```

**Claude Code (manual copy)** — copy a skill into your user or project skills
directory:

```sh
git clone https://github.com/gabrielbauman/skills
cp -r skills/skills/scoped-commits ~/.claude/skills/
# or, per-project: cp -r skills/skills/scoped-commits .claude/skills/
```

**Codex, Cursor, Gemini CLI, and other agents** — install with the
[skills.sh](https://skills.sh) CLI, which places skills in the right directory
for whichever agent it detects:

```sh
npx skills add gabrielbauman/skills
```

Or copy a `skills/<name>/` directory anywhere the [Agent Skills
format](https://agentskills.io) is supported.

## Repository layout

```
skills/
└── <skill-name>/
    ├── SKILL.md               # the skill itself
    ├── references/            # docs the skill loads on demand
    ├── scripts/               # executable tooling bundled with the skill
    └── evals/                 # test prompts and fixtures for skill evaluation
```

## License

MIT — see [LICENSE](LICENSE).
