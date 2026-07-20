# Coexisting with spec-driven planning tools

Tools like OpenSpec keep a living current-behaviour spec organized by
capability, plus per-change planning folders (proposal, design, tasks) whose
deltas merge into it when the change ships. The ADR workflow makes the
opposite bet: the decision log is the committed spec, the current view is
generated on demand (`adr_tools.py spec`), and hooks plus `validate` enforce
code-to-decision traceability that planning tools don't attempt.

The two can coexist. Planning artifacts are working material for a change in
flight; the ADR is the record of the decision once made. In a repo carrying
both:

- Commit planning files as chores (`Exempt: chore`); they are not spec.
- List the planning directory in `tools/adr/refignore` if its files must
  name superseded ADRs, so the stale-reference scan skips them.
- Never let a planning document stand in for a missing ADR. A proposal that
  shipped without its decision being recorded is unspecified behaviour.
