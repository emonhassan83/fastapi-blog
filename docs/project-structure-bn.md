# প্রজেক্ট কাঠামো ও ফাইল পরিচিতি

এই নথিতে FastAPI Blog প্রজেক্টের ফোল্ডার কাঠামো, গুরুত্বপূর্ণ ফাইলগুলোর দায়িত্ব
এবং বর্তমানে কোন অংশ চালু বা placeholder—তা ব্যাখ্যা করা হয়েছে।

## ফোল্ডার কাঠামো

```text
fastapi_blog/
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── versions/
│   │   └── __init__.py
│   └── env.py
├── docs/
│   └── project-structure-bn.md
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py
│       │   └── v1.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── exceptions.py
│       │   └── security.py
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── post/
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── repository.py
│       │   │   ├── router.py
│       │   │   ├── schemas.py
│       │   │   └── service.py
│       │   └── user/
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── repository.py
│       │       ├── router.py
│       │       ├── schemas.py
│       │       └── service.py
│       └── shared/
│           ├── __init__.py
│           ├── base_schemas.py
│           └── pagination.py
├── tests/
│   ├── conftest.py
│   ├── integration/
│   │   └── __init__.py
│   └── unit/
│       ├── __init__.py
│       └── test_api.py
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── main.py
├── alembic.ini
├── pyproject.toml
├── README.md
└── uv.lock
```

`.venv/`, `__pycache__/`, `.pytest_cache/` এবং `.ruff_cache/` স্থানীয়ভাবে তৈরি
হওয়া environment/cache; এগুলো অ্যাপ্লিকেশনের source code নয়, তাই কাঠামোর tree-তে
দেখানো হয়নি।

## Root-level ফাইল

| ফাইল | কাজ |
| --- | --- |
| `pyproject.toml` | প্রজেক্টের নাম ও Python সংস্করণ, runtime/dev dependency, `uv_build`, pytest এবং Ruff কনফিগার করে। |
| `uv.lock` | `uv`-এর নির্দিষ্ট dependency version ও resolution lock করে, যাতে একই dependency set পুনরায় ইনস্টল করা যায়। |
| `.python-version` | `uv` ও developer tooling-কে প্রজেক্টের Python সংস্করণ জানায়। |
| `.env.example` | প্রয়োজনীয় environment variable-এর নমুনা; এখানে আসল database credential রাখা যাবে না। |
| `.gitignore` | virtual environment, Python bytecode ও build artifact Git থেকে বাদ দেয়। |
| `README.md` | দ্রুত শুরু, server চালানো এবং check/test চালানোর সংক্ষিপ্ত নির্দেশনা। |
| `main.py` | `uvicorn main:app` ব্যবহারকারীদের জন্য পুরোনো import path-এ compatibility entry point; আসল app এখানে তৈরি হয় না। |
| `Dockerfile` | Python image-এ dependency sync করে Uvicorn দিয়ে app চালানোর container recipe। |
| `alembic.ini` | Alembic migration config ও script directory নির্ধারণ করে। |

## `src/app/` — অ্যাপ্লিকেশনের মূল কোড

`src` layout-এ Python package রাখা হয়েছে। `app` হলো মূল application package।

### Application entry point

| ফাইল | কাজ |
| --- | --- |
| `src/app/__init__.py` | `app` Python package চিহ্নিত করে। |
| `src/app/main.py` | `create_app()` factory দিয়ে FastAPI instance বানায়, API router যুক্ত করে এবং `app` export করে। |

অ্যাপ্লিকেশন চালুর জন্য `app.main:app` হলো মূল ASGI import path।

### `src/app/api/` — HTTP API

| ফাইল | কাজ |
| --- | --- |
| `api/__init__.py` | API package চিহ্নিত করে। |
| `api/v1.py` | `/api/v1`-এর module router aggregate করে। |
| `api/deps.py` | shared FastAPI dependency রাখার জায়গা; `DatabaseSession` (Annotated DB session) এবং `get_db` এখান থেকে export করা হয়। |

`main.py`-তে `api/v1.py` router-টি `/api/v1` prefix-এ include করা হয়। Versioned
API-র প্রতিটি domain router `api/v1.py` aggregator-এ যুক্ত করতে হবে।

### `src/app/core/` — cross-cutting configuration ও infrastructure

| ফাইল | কাজ |
| --- | --- |
| `core/__init__.py` | `core` package চিহ্নিত করে। |
| `core/config.py` | `pydantic-settings`-এর `Settings` class দিয়ে `.env` থেকে প্রয়োজনীয় `APP_NAME` ও `DATABASE_URL` পড়ে; কোনো default নেই, তাই configuration অনুপস্থিত হলে app startup স্পষ্ট validation error-এ থামে। |
| `core/database.py` | SQLAlchemy declarative `Base`, PostgreSQL engine, `SessionLocal` এবং request-scoped `get_db()` session dependency সংজ্ঞা দেয়। |
| `core/security.py` | `pwdlib` (Argon2 / bcrypt) দিয়ে password hashing ও verification helper। |
| `core/exceptions.py` | application-specific exception রাখার placeholder। |

### `src/app/modules/` — domain/module-ভিত্তিক কোড

প্রতিটি domain-এর router, schema, model, service ও repository আলাদা রাখার জন্য এই
layout। `post` এবং `user` module বাস্তবায়িত।

| ফাইলের ধরন | সাধারণ দায়িত্ব |
| --- | --- |
| `router.py` | domain-এর HTTP route ও request/response flow সংজ্ঞা। |
| `schemas.py` | API input/output validation schema। |
| `models.py` | database persistence model। |
| `service.py` | domain/business rule। |
| `repository.py` | database/data source access। |

#### `src/app/modules/post/`

`models.py`-এ `posts` table-এর SQLAlchemy `PostRecord` model (এর মধ্যে
`created_at` ও `updated_at` timestamp-ও আছে); `schemas.py`-এ request/response schema;
`repository.py`-তে database query ও transaction;
`service.py`-তে business operation; এবং `router.py`-তে HTTP route আছে। Post-এর
সব CRUD behavior এই module-এ রাখা হয়েছে।

এই পাঁচটি ফাইলের দায়িত্ব ও request flow-এর বিস্তারিত জানতে
[Post module documentation](./post-module-bn.md) দেখুন।

#### `src/app/modules/user/`

`models.py`-এ `users` table-এর SQLAlchemy `User` model; `schemas.py`-এ `UserRegister` ও
`UserResponse` validation schema; `repository.py`-তে database access; `service.py`-তে
duplicate email/username check ও password hashing; এবং `router.py`-তে `/api/v1/users/register`
registration endpoint রয়েছে।


### `src/app/shared/` — পুনর্ব্যবহারযোগ্য উপাদান

| ফাইল | কাজ |
| --- | --- |
| `shared/__init__.py` | shared package চিহ্নিত করে। |
| `shared/base_schemas.py` | একাধিক domain-এ ব্যবহারযোগ্য base Pydantic schema রাখার placeholder। |
| `shared/pagination.py` | pagination helper (`PaginationParams`, `PaginationMeta`, `PaginatedResponse`)। |

## `alembic/` — database migration scaffold

| ফাইল/ফোল্ডার | কাজ |
| --- | --- |
| `alembic/env.py` | `.env`-এর `DATABASE_URL` ও SQLAlchemy metadata ব্যবহার করে migration চালায়। |
| `alembic/versions/` | versioned database migration revision রাখে। |
| `alembic/versions/20261024_1500_add_post_timestamps.py` | পুরোনো `posts` table-এ timestamp column যোগ করে। |
| `alembic/versions/__init__.py` | versions directory-কে Python package হিসেবে চিহ্নিত করে; migration revision নয়। |

Use `uv run alembic upgrade head` to apply pending database migrations.


## `tests/` — পরীক্ষা

| ফাইল/ফোল্ডার | কাজ |
| --- | --- |
| `tests/conftest.py` | pytest fixture হিসেবে FastAPI `TestClient` তৈরি করে। |
| `tests/unit/test_api.py` | root এবং versioned post CRUD API-র unit test। |
| `tests/unit/` | unit test রাখে। |
| `tests/integration/` | ভবিষ্যতের integration test-এর directory; বর্তমানে test নেই। |

## `.github/workflows/` — CI

`ci.yml` GitHub Actions workflow-তে Python setup, `uv sync --locked --all-groups`,
Ruff check এবং pytest চালানো হয়।

## বর্তমানে চালু post API

Post-এর সব CRUD endpoint PostgreSQL-এর `posts` table ব্যবহার করে। Route module,
schema, service, repository এবং SQLAlchemy model—সব post-সংক্রান্ত code
`src/app/modules/post/`-এ রাখা হয়েছে। `src/app/api/v1.py` শুধু module router
aggregate করে; `main.py` API router-টি `/api/v1` prefix-এ mount করে।

| Method | Path | কাজ |
| --- | --- | --- |
| `POST` | `/api/v1/posts` | নতুন post তৈরি করে। |
| `GET` | `/api/v1/posts` | সব post ফেরত দেয়। |
| `GET` | `/api/v1/posts/{post_id}` | ID দিয়ে একটি post ফেরত দেয়। |
| `PUT` | `/api/v1/posts/{post_id}` | ID দিয়ে post update করে। |
| `DELETE` | `/api/v1/posts/{post_id}` | ID দিয়ে post মুছে দেয়। |

Root welcome endpoint `GET /`-এ আছে এবং OpenAPI schema-তে দেখানো হয় না।

## PostgreSQL সংযোগ কনফিগার

1. PostgreSQL চালু করে `fastapi_blog` নামে database তৈরি করুন।
2. `.env.example`-কে `.env` নামে কপি করুন।
3. `.env`-এর `DATABASE_URL`-এ আপনার database user/password/host/port/database দিন এবং `APP_NAME` সেট করুন।
   Format: `postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE`
4. Dependency sync করুন এবং app চালান:

```powershell
uv sync --all-groups
uv run uvicorn app.main:app --reload --reload-dir src
```

Server startup-এ `SELECT 1` চালিয়ে connection check করে এবং সফল হলে log-এ
success message দেয়। `posts` table না থাকলে SQLAlchemy model থেকে table তৈরি হয়।
Connection ব্যর্থ হলে error log করে startup বন্ধ করে দেয় (fail-fast); database
ছাড়া server চালু থাকে না। Post route-এ `get_db` dependency দিয়ে database session
নিয়ে service/repository layer-এ query করা হয়।

## Local development

PowerShell-এ repository root থেকে:

```powershell
uv sync --all-groups
uv run uvicorn app.main:app --reload --reload-dir src
```

`--reload-dir src` দিলে Uvicorn-এর file watcher শুধু application source পর্যবেক্ষণ
করে; `.venv`-এর dependency file পরিবর্তনে reload/error log এড়ানো যায়।

API documentation দেখতে server চালু রেখে `/docs` খুলুন। Test ও lint চালাতে:

```powershell
uv run pytest
uv run ruff check .
```
