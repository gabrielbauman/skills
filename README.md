# skills

[Agent skills](https://agentskills.io) written by Gabriel Bauman and Claude.
Each skill lives in its own directory under `skills/` and can be installed
independently.

## Skills

| Skill | Description |
| --- | --- |
| [scoped-commits](skills/scoped-commits/) | Write commit messages in the [Scoped Commits](https://scopedcommits.com) style: `scope: description`, the way Linux, Go, Git, FreeBSD, and nixpkgs write their history. Includes a concise, plain-ASCII house style for the message text (no emoji, no em dashes, no filler). |

## Installation

**Claude Code** — copy a skill into your user or project skills directory:

```sh
git clone https://github.com/gabrielbauman/skills
cp -r skills/skills/scoped-commits ~/.claude/skills/
# or, per-project: cp -r skills/skills/scoped-commits .claude/skills/
```

**Other agents** — any agent that supports the [Agent Skills
format](https://agentskills.io) can use a `skills/<name>/` directory as-is.

## Repository layout

```
skills/
└── <skill-name>/
    ├── SKILL.md               # the skill itself
    ├── references/            # docs the skill loads on demand
    └── evals/                 # test prompts for skill evaluation
```

## License

MIT — see [LICENSE](LICENSE).
