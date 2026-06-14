# Knowledge Base Runtime Directory

This directory is the local file database used by the crawler.

Runtime subdirectories are intentionally ignored by Git:

- `by_source/`: canonical article JSON by source and date.
- `by_time/`: time-based view.
- `by_topic/`: topic-based view.
- `index/`: URL, deduplication, and search indexes.
- `metadata/`: crawl history and daily reports.
- `exports/`: static report data, markdown exports, and built frontend assets.

Use `tests/fixtures/` for committed sample data.
