# Discord Issue Tracker

## About

**Discord Issue Tracker** is an issue tracker built into a Discord app. It is meant for small and young teams.

Discord is a common place for small and young teams to communicate with each other for software development. Unfortunately, most issue trackers/project managers are geared towards software developers, and are complicated for non-developers to use.

External issue trackers like Trello are simpler for non-developers, but I found that immature non-developers often forget about these external issue trackers. The motive of this project is to integrate an issue tracker into Discord, allowing you to assign users issues and query.

## Technology

-   Python
-   uv
-   discord.py
-   sqlite3
-   SQLAlchemy

## Setup

> **Note:** This is all TBD, I plan to improve DevOps later.

1. Install all dependencies

```shell
uv sync
```

2. Create an sqlite3 database named `db.sqlite3`.
3. Initialize the database with alembic.

```shell
alembic revision -m "initial"
alembic upgrade head
```

4. Run the bot.

```shell
uv run python -m discord_issues
```
