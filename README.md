# scoped-commits-skill

An [agent skill](https://agentskills.io) that teaches coding agents to write
commit messages in the [Scoped Commits](https://scopedcommits.com) style:

```
<scope>: <description>

[optional body]

[optional trailer(s)]
```

The subsystem comes first, the way Linux, FreeBSD, Git, Go, and nixpkgs write
their history — no `feat:`/`fix:`/`chore:` type prefixes.

```
net/http/cookiejar: add godoc links
i2c: virtio: mark device ready before registering the adapter
xwayland: 24.1.11 -> 24.1.12
```

## What the skill does

When an agent is about to commit, the skill activates if any of these hold:

- the repository's existing log already uses scope-first subjects,
- it is the first commit in a brand-new repository, or
- the project's `AGENTS.md`, `CLAUDE.md`, or `CONTRIBUTING` file calls for
  scoped commits.

It then guides the agent through choosing a scope from the changed paths and
existing history, writing an imperative description, and using bodies and
trailers appropriately. `references/rationale.md` carries the full
justification (with upstream sources) for when the agent needs to explain or
defend the convention.

## Installation

**Claude Code** — copy the skill into your user or project skills directory:

```sh
git clone https://github.com/gbauman/scoped-commits-skill
cp -r scoped-commits-skill/skills/scoped-commits ~/.claude/skills/
# or, per-project: cp -r scoped-commits-skill/skills/scoped-commits .claude/skills/
```

**Other agents** — any agent that supports the [Agent Skills
format](https://agentskills.io) can use the `skills/scoped-commits/` directory
as-is.

## Repository layout

```
skills/
└── scoped-commits/
    ├── SKILL.md               # the skill itself
    ├── references/
    │   └── rationale.md       # why scope-first, with upstream sources
    └── evals/
        └── evals.json         # test prompts for skill evaluation
```

## License

MIT — see [LICENSE](LICENSE). Scoped Commits is a standard by
[Nevarro](https://nevarro.space); this repository is an independent skill
implementation.
