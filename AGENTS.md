# AGENTS.md

Guidance for coding agents (Claude Code, Cursor) working in this repository.

## Orientation

The Smartspace SDK: the `smartspace-ai` Python package (`smartspace/`) for writing blocks, plus the
`smartspace` CLI. Smartspace-ai-api consumes it as a git dependency on this repo's `develop` branch
(pinned by its `poetry.lock`), so a merge to `develop` reaches ai-api on its next lock update.

## Build and test (what CI runs on a PR)

```bash
poetry install --no-interaction
poetry build
poetry run pytest
```

## Branch and release strategy

- PRs target `develop`; `pr-checks.yml` runs on PRs into `develop` and `main`.
- A push to `main` publishes the package to PyPI at the `version` in `pyproject.toml` and tags a
  GitHub release (`release.yml`). Bump the version in the PR that will be released.

## Design repo: briefs and decisions

Briefs, decisions (`ADR-NNNN`) and the brief, PR-plan and PR templates for every SmartSpace repo
live in the design repo, [Smartspace-ai/smartspace-v2-design](https://github.com/Smartspace-ai/smartspace-v2-design).
Clone it if it is not checked out; never assume a sibling path.

- Before non-trivial work, check its `briefs/` for a brief covering the work and its README's
  decision index for decisions touching this repo. Cite a decision as `ADR-NNNN` at the code it
  constrains; never restate it here.
- A decision made while working gets captured there (say "ADR this" in a Claude Code session in
  the design repo).
- PR plans follow its `templates/pr-plan.md` and are not committed (`.claude/plans/` is
  gitignored). PR descriptions follow its `templates/pull-request.md`.

## Out-of-scope findings

For anything noticed that is outside the current change, ask: what concretely goes wrong if this
never happens?

- **Nothing concrete:** drop it.
- **A user, an API caller or stored data gets a wrong result today:** it is a bug. Raise it for a
  bug ticket; never fold the fix into the current PR.
- **A named cost** (maintainability, a test gap, a class of future bug): list it in the PR
  description's *Not in this PR* table with its consequence. A person files it on Monday; agents
  never file it themselves.
