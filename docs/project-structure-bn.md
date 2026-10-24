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
│       │   └── users/
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── repository.py
│       │       ├── router.py
│       │       ├── schemas.py
│       │       └── service.py
│       └── shared/
│           ├── __init__.py
│           ├── base_models.py
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
| `.env.example` | স্থানীয় environment variable-এর নমুনা; বর্তমানে `APP_NAME` দেখানো আছে। |
| `.gitignore` | virtual environment, Python bytecode ও build artifact Git থেকে বাদ দেয়। |
| `README.md` | দ্রুত শুরু, server চালানো এবং check/test চালানোর সংক্ষিপ্ত নির্দেশনা। |
| `main.py` | `uvicorn main:app` ব্যবহারকারীদের জন্য পুরোনো import path-এ compatibility entry point; আসল app এখানে তৈরি হয় না। |
| `Dockerfile` | Python image-এ dependency sync করে Uvicorn দিয়ে app চালানোর container recipe। |
| `alembic.ini` | Alembic migration script directory-এর অবস্থান নির্ধারণ করে। |

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
| `api/v1.py` | বর্তমানে চালু root ও post endpoint, request schema, in-memory post data এবং CRUD handler রাখে। |
| `api/deps.py` | ভবিষ্যতে shared FastAPI dependency রাখার জন্য; এখনো dependency সংজ্ঞায়িত নেই। |

বর্তমান post endpoint-গুলো সরাসরি `api/v1.py`-তে আছে। `modules/post/router.py`
এখনো এই endpoint-গুলোর router নয় এবং `main.py`-তে include করা হয়নি।

### `src/app/core/` — cross-cutting configuration ও infrastructure

| ফাইল | কাজ |
| --- | --- |
| `core/__init__.py` | `core` package চিহ্নিত করে। |
| `core/config.py` | `pydantic-settings`-এর `Settings` class দিয়ে `APP_NAME` configuration পড়ে; `.env` file থাকলে তা ব্যবহার করে। |
| `core/database.py` | database integration-এর placeholder। SQLAlchemy বা Motor engine/session এখনো সেটআপ করা হয়নি। |
| `core/security.py` | authentication/password hashing logic রাখার placeholder; এখনো implement করা হয়নি। |
| `core/exceptions.py` | application-specific exception রাখার placeholder। |

### `src/app/modules/` — domain/module-ভিত্তিক কোড

প্রতিটি domain-এর router, schema, model, service ও repository আলাদা রাখার জন্য এই
layout। বর্তমান `post` এবং `users` ফোল্ডারের ফাইলগুলো placeholder—এগুলোতে এখনো
বাস্তব domain logic নেই।

| ফাইলের ধরন | সাধারণ দায়িত্ব |
| --- | --- |
| `router.py` | domain-এর HTTP route ও request/response flow সংজ্ঞা। |
| `schemas.py` | API input/output validation schema। |
| `models.py` | database persistence model। |
| `service.py` | domain/business rule। |
| `repository.py` | database/data source access। |

#### `src/app/modules/post/`

`__init__.py`, `router.py`, `schemas.py`, `models.py`, `service.py` এবং
`repository.py`-এর scaffold আছে। এগুলো বর্তমানে placeholder; চালু post API-র
বাস্তবায়ন `src/app/api/v1.py`-তে।

#### `src/app/modules/users/`

`__init__.py`, `router.py`, `schemas.py`, `models.py`, `service.py` এবং
`repository.py`-এর scaffold আছে। Users API, model ও business logic এখনো তৈরি হয়নি।

### `src/app/shared/` — পুনর্ব্যবহারযোগ্য উপাদান

| ফাইল | কাজ |
| --- | --- |
| `shared/__init__.py` | shared package চিহ্নিত করে। |
| `shared/base_models.py` | একাধিক domain-এ ব্যবহারযোগ্য base Pydantic model রাখার placeholder। |
| `shared/pagination.py` | pagination helper রাখার placeholder। |

## `alembic/` — database migration scaffold

| ফাইল/ফোল্ডার | কাজ |
| --- | --- |
| `alembic/env.py` | migration environment-এর placeholder; metadata ও database connection configure করা হয়নি। |
| `alembic/versions/` | ভবিষ্যতের migration revision রাখার directory। |
| `alembic/versions/__init__.py` | versions directory-কে Python package হিসেবে চিহ্নিত করে; migration revision নয়। |

Database নির্বাচন ও setup না হওয়ায় Alembic এখনো কার্যকর migration চালায় না।

## `tests/` — পরীক্ষা

| ফাইল/ফোল্ডার | কাজ |
| --- | --- |
| `tests/conftest.py` | pytest fixture হিসেবে FastAPI `TestClient` তৈরি করে। |
| `tests/unit/test_api.py` | root response এবং seed post list-এর জন্য unit/API test। |
| `tests/unit/` | unit test রাখে। |
| `tests/integration/` | ভবিষ্যতের integration test-এর directory; বর্তমানে test নেই। |

## `.github/workflows/` — CI

`ci.yml` GitHub Actions workflow-তে Python setup, `uv sync --locked --all-groups`,
Ruff check এবং pytest চালানো হয়।

## বর্তমানে চালু post API

ডেটা এখন process memory-তে রাখা হয়; database-এ persist হয় না। Server restart হলে
তৈরি/পরিবর্তিত post হারিয়ে যাবে।

| Method | Path | কাজ |
| --- | --- | --- |
| `GET` | `/` | স্বাগত বার্তা দেয়; OpenAPI schema-তে দেখানো হয় না। |
| `POST` | `/posts` | নতুন post তৈরি করে। |
| `GET` | `/posts` | সব post ফেরত দেয়। |
| `GET` | `/posts/{id}` | ID দিয়ে একটি post ফেরত দেয়। |
| `PUT` | `/posts/{id}` | ID দিয়ে post update করে। |
| `DELETE` | `/posts/{id}` | ID দিয়ে post মুছে দেয়। |

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
