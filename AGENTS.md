# Agent guidance

This is a monorepo of agent skills, published as a Claude Code plugin
marketplace. Each skill lives in `skills/<name>/` and is listed as a plugin in
`.claude-plugin/marketplace.json`.

## Commit messages

Use scoped commits (see `skills/scoped-commits/SKILL.md`, which this repo both
ships and follows): subject is `scope: description`, imperative, lowercase
after the colon, no type prefixes. Scopes used here are path-style:
`skills/<name>:` for a skill, plus `marketplace:`, `docs:`, and `meta:`.
Message text follows the skill's house style: plain ASCII, no emoji, no em
dashes, no filler, bodies as short why-focused paragraphs.

## Adding or changing a skill

1. Put the skill at `skills/<name>/SKILL.md`. The frontmatter `name` must
   match the directory name. Every skill ships `evals/evals.json` with 2-4
   realistic prompts and gradeable assertions; copy the format from an
   existing skill. Add `references/` and `scripts/` as needed.
   Frontmatter must be strict YAML: double-quote the `description` value,
   since useful descriptions usually contain a colon and space, which breaks
   plain scalars. Claude Code parses them anyway; the skills.sh CLI silently
   drops the skill.
2. Add a plugin entry to `.claude-plugin/marketplace.json` following the
   existing pattern: `source: "./"`, `strict: false`, and a `skills` array
   pointing at `./skills/<name>`.
3. Add a row to the skills table in `README.md`.
4. Run `claude plugin validate .` and `python3 scripts/check_skills.py`
   (needs PyYAML) and make sure both pass before committing. CI runs the same
   checks plus a skills.sh discovery test, and lints PR commit subjects for
   the scoped format.

Skill text conventions: the description carries only the triggering (what
the skill does and when to use it) and stays under roughly 600 characters.
Descriptions load into every session before any skill fires, so detail
belongs in the body, which loads only after the skill triggers; do not
summarize the body's rules in the description. Add a short pairing note
only where a sibling skill competes for the same trigger and the model
needs help routing, as a terse parenthetical gloss; one direction is
enough. Bodies run roughly 100-250 lines, open by naming the failure mode
the skill exists to correct, and give each rule with its reason, with
concrete before/after examples over abstract restatements.

## Prose style

Skill text, README copy, and reference docs follow the checklist in
`skills/humanize/SKILL.md`: no AI tropes, no inflated vocabulary, specifics
over adjectives. A skill about removing slop cannot be written in it.

## Repo-local skills

`.claude/skills/` contains symlinks to `skills/scoped-commits` and
`skills/humanize` so both apply automatically when working in this repo.
