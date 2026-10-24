# FastAPI Blog

A small FastAPI application organized with a `src` layout and modular API
packages.

বাংলায় folder structure এবং প্রতিটি ফাইলের দায়িত্ব জানতে
[প্রজেক্ট কাঠামোর বিস্তারিত](docs/project-structure-bn.md) দেখুন।

## Run locally

```powershell
uv sync --all-groups
uv run uvicorn app.main:app --reload --reload-dir src
```

`--reload-dir src` keeps Uvicorn's watcher focused on application code instead
of the project root and virtual environment. The legacy `uvicorn main:app`
import is also supported.

The existing post endpoints are available at `/posts` and `/posts/{id}`.
The users and orders packages are structural placeholders; persistence,
migrations, and authentication have not been configured yet.

## Checks

```powershell
uv run ruff check .
uv run pytest
```