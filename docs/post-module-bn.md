# Post Module: ফাইলগুলোর কাজ ও request flow

এই নথিতে `src/app/modules/post/`-এর পাঁচটি ফাইল—`models.py`, `schemas.py`,
`repository.py`, `service.py` এবং `router.py`—কীভাবে একসঙ্গে কাজ করে তা
ব্যাখ্যা করা হয়েছে।

## ফোল্ডার কাঠামো

```text
src/app/
├── api/
│   └── v1.py                 # সব module router একত্র করে
├── core/
│   └── database.py           # SQLAlchemy engine, Base ও get_db session dependency
└── modules/
    └── post/
        ├── __init__.py
        ├── models.py         # PostgreSQL table-এর ORM model
        ├── schemas.py        # API input/output validation
        ├── repository.py     # SQL query ও database write
        ├── service.py        # Post-এর application/business operation
        └── router.py         # HTTP endpoint ও status/response handling
```

## কোন ফাইল কী করে

### `models.py` — database table-এর রূপ

`PostRecord` হলো SQLAlchemy ORM model। এর `__tablename__ = "posts"` বলে
PostgreSQL-এ model-টি `posts` table-কে নির্দেশ করে।

| Python field | Database type | অর্থ |
| --- | --- | --- |
| `id` | `Integer`, primary key | প্রতিটি post-এর unique ID; database ID তৈরি করে। |
| `title` | সর্বোচ্চ 255 অক্ষরের `String` | Post-এর শিরোনাম; `nullable=False`, তাই ফাঁকা/NULL রাখা যায় না। |
| `content` | `Text` | Post-এর মূল লেখা; `nullable=False`। |
| `published` | `Boolean` | Post প্রকাশিত কি না; নতুন record-এর ORM default `True`। |
| `rating` | nullable `Integer` | ঐচ্ছিক rating; `None`/NULL হতে পারে। |
| `created_at` | timezone-aware `DateTime` | Post তৈরির UTC সময়; তৈরি হওয়ার সময় স্বয়ংক্রিয়ভাবে সেট হয়। |
| `updated_at` | timezone-aware `DateTime` | সর্বশেষ update-এর UTC সময়; তৈরি ও প্রতিটি ORM update-এ স্বয়ংক্রিয়ভাবে সেট হয়। |

Model class `Base` থেকে উত্তরাধিকার নেয়। `Base` সংজ্ঞায়িত আছে
`src/app/core/database.py`-তে। Server startup-এ `Base.metadata.create_all()`
চালানো হয়; ফলে পরিচিত model-এর table না থাকলে তা তৈরি হয়। এটি schema migration-এর
বিকল্প নয়—production schema পরিবর্তনে Alembic migration ব্যবহার করা উচিত।

### `schemas.py` — API data validation ও output shape

Pydantic schema HTTP request-এর data যাচাই করে এবং response-কে নির্দিষ্ট shape-এ
রূপ দেয়।

- `PostCreate`: `POST` request-এর body। `title` ও `content` আবশ্যক;
  `published` বাদ দিলে `True`, আর `rating` বাদ দিলে `None` হয়।
- `PostUpdate`: `PUT` request-এর body। বর্তমান schema-তে `title` ও `content`
  আবশ্যক, তাই এটি সম্পূর্ণ update; partial update নয়।
- `PostRead`: API response-এর জন্য। এতে database-উৎপন্ন `id`-সহ post field থাকে।
  `created_at` ও `updated_at`-ও response-এ থাকে। `ConfigDict(from_attributes=True)`
  থাকার কারণে SQLAlchemy model object থেকে schema তৈরি করা যায়।

### `repository.py` — database access

`PostRepository` SQLAlchemy `Session` পায় এবং `PostRecord`-এর query/write করে।
HTTP status বা response message এখানে ঠিক করা হয় না।

- `create()`: schema-র `model_dump()` থেকে `PostRecord` বানায়, session-এ যোগ
  করে, `commit()` দিয়ে database-এ সংরক্ষণ করে, `refresh()` দিয়ে database-উৎপন্ন
  মান (যেমন `id`) আবার পড়ে।
- `get_all()`: `select(PostRecord)` চালিয়ে সব post ফেরত দেয়।
- `get_by_id()`: primary key দিয়ে একটি post খোঁজে; না পেলে `None`।
- `update()`: দেওয়া schema-র field-গুলো ORM object-এ বসিয়ে commit ও refresh করে।
  Model-এর `onupdate`-এর কারণে `updated_at` স্বয়ংক্রিয়ভাবে নতুন সময় পায়।
- `delete()`: session থেকে record মুছে commit করে।

নির্বাচিত `create()` flow-এর অর্থ:

```python
post = PostRecord(**post_data.model_dump())
self.session.add(post)
self.session.commit()
self.session.refresh(post)
return post
```

1. `model_dump()` validated `PostCreate`-কে Python dictionary-তে বদলায়।
2. `PostRecord(**...)` dictionary-র key/value দিয়ে ORM object তৈরি করে।
3. `add()` object-টিকে বর্তমান session-এ যোগ করে; তখনও database transaction
   commit হয়নি।
4. `commit()` transaction স্থায়ীভাবে database-এ লেখে।
5. `refresh()` database থেকে তৈরি/পরিবর্তিত field আবার object-এ আনে।
6. ORM object service-এ, তারপর router-এ ফেরত যায়।

### `service.py` — operation orchestration

`PostService` repository ব্যবহার করে post-সংক্রান্ত operation প্রকাশ করে।
বর্তমানে এটি business rule-এর স্তর, যদিও নিয়মগুলো সরল:

- create ও list সরাসরি repository operation ডাকে;
- get একটি record বা `None` ফেরায়;
- update আগে record আছে কি না দেখে; না থাকলে `None`;
- delete record পেলে মুছে `True`, না পেলে `False` ফেরায়।

এভাবে router-কে database query এবং persistence-এর বিস্তারিত জানতে হয় না।
ভবিষ্যতে permission, visibility বা domain rule যোগ করলে সেগুলো service-এ রাখা যায়।

### `router.py` — HTTP route

`router.py`-তে FastAPI endpoint-গুলো আছে। `DatabaseSession` হলো
`Annotated[Session, Depends(get_db)]`; FastAPI request-এর জন্য database session
নিয়ে endpoint-এ inject করে।

| Method | Route suffix | কাজ | সাফল্যের status |
| --- | --- | --- | --- |
| `POST` | `/` | Post তৈরি | `201 Created` |
| `GET` | `/` | সব post পড়া | `200 OK` |
| `GET` | `/{post_id}` | নির্দিষ্ট post পড়া | `200 OK` |
| `PUT` | `/{post_id}` | সম্পূর্ণ post update | `200 OK` |
| `DELETE` | `/{post_id}` | Post মুছে ফেলা | `204 No Content` |

Route suffix-গুলো `""` বা `"/{post_id}"`; module prefix aggregator-এ যোগ হয়।
Post না পাওয়া গেলে `404 Not Found` এবং বোধগম্য detail ফেরত আসে। Read endpoint-গুলো
`PostRead` দিয়ে ORM object-কে response dictionary-তে রূপান্তর করে।

## পুরো request-এর চলার পথ

```text
HTTP request
    ↓
main.py: /api/v1 prefix
    ↓
api/v1.py: /posts prefix
    ↓
modules/post/router.py: validate request + get_db session
    ↓
modules/post/service.py: operation পরিচালনা
    ↓
modules/post/repository.py: SQLAlchemy query / commit
    ↓
modules/post/models.py: posts table mapping
    ↓
PostgreSQL
```

Response ফেরার সময় database result repository থেকে service হয়ে router-এ আসে।
Router সেটিকে `PostRead` schema-তে রূপান্তর করে HTTP response পাঠায়।

## পূর্ণ API URL

`main.py` `/api/v1` prefix-এ `api/v1.py`-কে mount করে; `api/v1.py` `/posts`
prefix-এ Post router যুক্ত করে। তাই:

| Method | পূর্ণ URL | কাজ |
| --- | --- | --- |
| `POST` | `http://127.0.0.1:8000/api/v1/posts` | Post তৈরি |
| `GET` | `http://127.0.0.1:8000/api/v1/posts` | সব post |
| `GET` | `http://127.0.0.1:8000/api/v1/posts/1` | ID `1`-এর post |
| `PUT` | `http://127.0.0.1:8000/api/v1/posts/1` | ID `1`-এর post update |
| `DELETE` | `http://127.0.0.1:8000/api/v1/posts/1` | ID `1` মুছে ফেলা |

API request/response দেখতে server চালু করে `/docs` খুলুন।

## উদাহরণ: post তৈরি

`POST /api/v1/posts`-এ JSON body:

```json
{
  "title": "আমার পোস্ট",
  "content": "এটি পোস্টের লেখা।",
  "published": true,
  "rating": 5,
  "created_at": "2026-10-24T00:00:00Z",
  "updated_at": "2026-10-24T00:00:00Z"
}
```

প্রথমে `PostCreate` body যাচাই করে। তারপর router `PostService` ডাকে, service
`PostRepository`-তে পাঠায়, repository `PostRecord` তৈরি করে database-এ commit করে।
শেষে router `PostRead` response ফেরায়, যেমন:

```json
{
  "message": "Post created successfully",
  "data": {
    "id": 1,
    "title": "আমার পোস্ট",
    "content": "এটি পোস্টের লেখা।",
    "published": true,
    "rating": 5
  }
}
```

বাস্তব `id` database তৈরি করে; উদাহরণের `1` কেবল নমুনা।

## গুরুত্বপূর্ণ বর্তমান সীমা

- `PUT` বর্তমানে full update; schema-তে সব প্রয়োজনীয় field পাঠাতে হবে।
- Database error repository-তে সফল response হিসেবে ধরা হয় না; exception উপরে
  propagate করে server error হয়।
- Connection ও credentials `.env`-এর `DATABASE_URL` থেকে আসে; `GET /posts`-এর
  response দেখতে database-এ record থাকতে হবে।
- Model-এর field পরিবর্তন করলে `create_all()` পুরোনো table-এর column update করে
  না; schema পরিবর্তনে migration প্রয়োজন। `created_at`/`updated_at` যোগ করার
  আগে তৈরি database-এ নিচের Alembic migration চালান:

```powershell
uv run alembic upgrade head
```

Migration পুরোনো row-গুলোতেও `CURRENT_TIMESTAMP` বসিয়ে দুইটি column যোগ করবে।
প্রথমবার নতুন database তৈরি করলে আগে app একবার চালান, যাতে `posts` table তৈরি
হয়; তারপর app থামিয়ে migration command চালান। Migration শেষ হলে app আবার চালান।
Migration rollback করতে `uv run alembic downgrade base` ব্যবহার করা যায়—এতে
timestamp column ও সেগুলোর data মুছে যাবে।
