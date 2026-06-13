# AGENTS.md

This file provides guidance to AI agents working in this repository.
`pytest-jubilant` is a pytest plugin that adds fixtures, markers, and CLI
options for [Jubilant](https://github.com/canonical/jubilant)-based charm
integration tests. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the design
philosophy; this file collects the commands and conventions.

## Tooling

Dependencies and tools are managed with [`uv`](https://docs.astral.sh/uv/);
tasks run through `tox` with the `tox-uv` plugin:

```bash
uv tool install tox --with tox-uv
```

## Lint, format, test

```bash
tox -e format       # apply ruff formatting and autofixes
tox -e lint         # ruff format --check, ruff check, pyright (must pass before pushing)
tox -e unit         # unit tests under tests/unit with coverage
tox -e integration  # integration tests under tests/integration
```

Run `tox -e format`, `tox -e lint`, and `tox -e unit` locally before pushing.
All three of `lint`, `unit`, and `integration` are required in CI.

The integration tests need packed test charms; pack them and set the
`*CHARM_PATH` environment variables they reference before running locally.

## Conventions

- **Python floor is 3.8** (set by jubilant) — keep code compatible.
- **Commits / PR titles:** [Conventional Commits](https://www.conventionalcommits.org/);
  no scopes. Types: `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`,
  `revert`, `test`. The PR title becomes the squashed commit message.
