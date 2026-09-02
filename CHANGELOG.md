# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-04

### Added
- Index every ebook in a Telegram channel into a local SQLite catalogue
- Full-text search over titles, authors, filenames, and captions (FTS5)
- Title and author extraction from shared filenames
- `channels`, `index`, `search`, `list`, `stats`, and `get` commands
- Send-to-Kindle delivery with `get --kindle`
- Configuration via `KUTUB_HOME`, `KUTUB_DOWNLOAD_DIR`, `TG_API_ID`,
  `TG_API_HASH`, and `KINDLE_SERIAL`

### Known issues
- Filenames written as `Author - Title` are parsed with the fields swapped
- The same book posted twice is catalogued twice

[1.0.0]: https://github.com/Ajarallah/kutub/releases/tag/v1.0.0
