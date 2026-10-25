# FastAPI Blog

A small FastAPI application organized with a `src` layout and modular API
packages.

বাংলায় folder structure এবং প্রতিটি ফাইলের দায়িত্ব জানতে
[প্রজেক্ট কাঠামোর বিস্তারিত](docs/project-structure-bn.md) এবং
JWT Authentication-এর বিস্তারিত জানতে [অথেনটিকেশন সিস্টেমের বিস্তারিত](docs/auth-system-bn.md) দেখুন।


## Run locally

```powershell
uv sync --all-groups
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload --reload-dir src
```

`--reload-dir src` keeps Uvicorn's watcher focused on application code instead
of the project root and virtual environment. The legacy `uvicorn main:app`
import is also supported.

Set both `APP_NAME` and `DATABASE_URL` in `.env` before starting the app; neither
has a default value. Keep real database credentials out of `.env.example`.
After adding a database schema change, apply it with `uv run alembic upgrade head`
before using the updated API.
The server checks PostgreSQL connectivity during startup and logs a success
message. If the connection check fails, it logs the error and aborts startup.
Post APIs use PostgreSQL and are available under `/api/v1/posts`.

User registration API is available under `/api/v1/users/register`.
User login and profile APIs are available under `/api/v1/auth/login` and `/api/v1/auth/me`
with JWT authentication (PyJWT, configurable via `JWT_SECRET_KEY`, `JWT_ALGORITHM`,
and `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).


## Scaffold New Module

নতুন ডোমেন মডিউল (`models`, `schemas`, `repository`, `service`, `router`) এক ক্লিকে তৈরি করতে:

```powershell
uv run python scripts/create_module.py <module_name>
# উদাহরণ:
uv run python scripts/create_module.py category
uv run python scripts/create_module.py tag
```

## Checks


```powershell
uv run ruff check .
uv run pytest
```