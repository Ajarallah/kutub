# Contributing

Thanks for taking a look.

## Setup

```bash
git clone https://github.com/Ajarallah/kutub.git
cd kutub
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
ruff check .
pytest -q
```

Both run in CI against Python 3.9, 3.11, and 3.13.

## Guidelines

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`
- New behaviour needs a test. `tests/test_naming.py` is the easiest place to start.
- Keep modules focused: `naming` parses, `catalogue` stores, `telegram` fetches,
  `kindle` delivers, `cli` wires them together.
- Never commit anything from `~/.kutub` — the session file grants access to a
  real Telegram account.

## Reporting bugs

Open an issue with the version, your Python version, and the output. Strip
`api_id`, `api_hash`, and phone numbers first.
