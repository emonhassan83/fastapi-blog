# Authentication & Authorization System (JWT)

এই নথিতে FastAPI Blog প্রজেক্টের সম্পূর্ণ **Authentication & Authorization (JWT)** সিস্টেম, এর আর্কিটেকচার, এনভায়রনমেন্ট কনফিগারেশন, রিকোয়েস্ট-রেসপন্স ফ্লো, JWT Payload কাঠামো এবং কীভাবে অন্যান্য রাউট প্রোটেক্ট করতে হয়—তা বিস্তারিত ব্যাখ্যা করা হয়েছে।

---

## ১. আর্কিটেকচার ও মূল বৈশিষ্ট্য

- **Stateless Authentication:** সেশন ডাটাবেসে সেভ করার পরিবর্তে ক্রিপ্টোগ্রাফিকভাবে সাইন করা **JSON Web Token (JWT)** ব্যবহার করা হয়।
- **Password Security:** আধুনিক **Argon2** ও **bcrypt** অ্যালগরিদম ভিত্তিক `pwdlib` ব্যবহার করে পাসওয়ার্ড হ্যাশ করা হয়। প্লেইনটেক্সট পাসওয়ার্ড কখনো ডাটাবেসে সেভ হয় না এবং API রেসপন্সে কখনো পাসওয়ার্ড ফিল্ড ফেরত দেওয়া হয় না।
- **Separation of Concerns:** 
  - `modules/user`: ইউজার প্রোফাইল ও রেজিস্ট্রেশন হ্যান্ডেল করে।
  - `modules/auth`: লগইন ও প্রোফাইল ফেচিং (`/auth/me`) হ্যান্ডেল করে।
  - `core/security`: ক্রিপ্টোগ্রাফিক হ্যাশিং ও টোকেন এনকোডিং/ডিকোডিং।
  - `api/deps`: সেন্ট্রাল ডিপেন্ডেন্সি ইনজেকশন (`CurrentUser`, `get_current_user`)।

---

## ২. ফোল্ডার ও ফাইলের দায়িত্ব

```text
src/app/
├── core/
│   ├── config.py         # .env থেকে JWT কনফিগারেশন লোড করে
│   └── security.py       # Password hash ও JWT token তৈরি/ডিকোড করে
├── api/
│   ├── deps.py           # OAuth2 Bearer স্কিম ও CurrentUser ডিপেন্ডেন্সি
│   └── v1.py             # /auth ও /users রাউটার অ্যাগ্রিগেট করে
└── modules/
    ├── user/
    │   ├── models.py     # User SQLAlchemy ORM মডেল
    │   ├── schemas.py    # UserRegister, UserRead, UserResponse
    │   ├── repository.py # Database lookup (email, username, id)
    │   ├── service.py    # ডুপ্লিকেট চেক ও পাসওয়ার্ড হ্যাশিং লজিক
    │   └── router.py     # POST /api/v1/users/register
    └── auth/
        ├── schemas.py    # LoginRequest, TokenResponse
        ├── service.py    # Authenticate credentials & generate token
        └── router.py     # POST /api/v1/auth/login, GET /api/v1/auth/me
```

---

## ৩. এনভায়রনমেন্ট কনফিগারেশন (`.env`)

JWT সিস্টেম পরিচালনার জন্য `.env` ফাইলে নিচের ৩টি ভ্যারিয়েবল আবশ্যক:

| Variable | Description | উদাহরণ মান |
| --- | --- | --- |
| `JWT_SECRET_KEY` | টোকেন সাইন ও ভেরিফাই করার সিক্রেট কি (কমপক্ষে ৩২ বাইট) | `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7` |
| `JWT_ALGORITHM` | ক্রিপ্টোগ্রাফিক অ্যালগরিদম | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | টোকেনের কার্যকর মেয়াদ (মিনিট) | `60` |

> **সিকিউরিটি টিপ:** প্রোডাকশনে কখনো ডিফল্ট বা সাধারণ সিক্রেট কি ব্যবহার করবেন না। শক্তিশালী কি জেনারেট করতে পারেন:
> ```powershell
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## ৪. রিকোয়েস্ট ও রেসপন্স ফ্লো বিস্তারিত

```text
1. User Registration:
   Client  ──(POST /users/register)──>  Router ──> Service (Hash password) ──> Repository ──> DB

2. User Login:
   Client  ──(POST /auth/login)─────>  Router ──> Service (Verify password) ──> Issue JWT Token

3. Protected Route:
   Client  ──(GET /auth/me + Token)──>  Deps (Verify JWT & Expiry) ──> CurrentUser injected ──> Return Profile
```

---

### ক. ইউজার রেজিস্ট্রেশন (User Registration)

নতুন ব্যবহারকারী রেজিস্ট্রেশন করার জন্য এই এন্ডপয়েন্ট ব্যবহৃত হয়। পাসওয়ার্ড স্বয়ংক্রিয়ভাবে হ্যাশ হয়ে ডাটাবেসে সেভ হয়।

- **Endpoint:** `POST /api/v1/users/register`
- **Status Code:** `201 Created`

#### Request Body (`UserRegister`):
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "supersecretpassword"
}
```

#### Success Response (`201 Created`):
```json
{
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-10-25T15:50:00Z",
    "updated_at": "2026-10-25T15:50:00Z"
  }
}
```

#### Error Responses:
- **`400 Bad Request`** (ডুপ্লিকেট ইমেইল):
  ```json
  { "detail": "Email is already registered" }
  ```
- **`400 Bad Request`** (ডুপ্লিকেট ইউজারনেম):
  ```json
  { "detail": "Username is already taken" }
  ```
- **`422 Unprocessable Entity`** (অবৈধ ইমেইল বা ৬ অক্ষরের কম পাসওয়ার্ড):
  ```json
  { "detail": [{ "msg": "value is not a valid email address", ... }] }
  ```

---

### খ. ইউজার লগইন ও টোকেন গ্রহণ (User Login)

রেজিস্টার্ড ইমেইল ও পাসওয়ার্ড প্রদান করে ব্যবহারকারী একটি সাইন করা Bearer টোকেন পায়।

- **Endpoint:** `POST /api/v1/auth/login`
- **Status Code:** `200 OK`

#### Request Body (`LoginRequest`):
```json
{
  "email": "john@example.com",
  "password": "supersecretpassword"
}
```

#### Success Response (`200 OK` - `TokenResponse`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcl9pZCI6MSwiZW1haWwiOiJqb2huQGV4YW1wbGUuY29tIiwiaWF0IjoxNzI5ODY0MDAwLCJleHAiOjE3Mjk4Njc2MDB9.abcdef...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Error Response:
- **`401 Unauthorized`** (ভুল ইমেইল বা পাসওয়ার্ড):
  ```json
  { "detail": "Incorrect email or password" }
  ```

---

### গ. JWT Token-এর ভেতরের Payload কাঠামো

প্রাপ্ত `access_token`-টি ডিকোড করলে ভেতরে নিচের ক্লাইমস (claims) পাওয়া যায়:

```json
{
  "sub": "1",
  "user_id": 1,
  "email": "john@example.com",
  "iat": 1729864000,
  "exp": 1729867600
}
```

#### প্রতিটি ফিল্ডের অর্থ:
- **`sub` (Subject):** স্ট্যান্ডার্ড JWT ক্লেইম, যা ব্যবহারকারীর ইউনিক আইডেন্টিফায়ার নির্দেশ করে (এখানে `str(user.id)`)।
- **`user_id` (Integer):** সরাসরি ব্যবহারকারীর ইন্টিজার প্রাইমারি কি ID।
- **`email` (String):** লগইনকৃত ইউজারের ভ্যালিড ইমেইল এড্রেস।
- **`iat` (Issued At):** টোকেন ইস্যু করার সময় (Unix timestamp)।
- **`exp` (Expiration Time):** টোকেনের মেয়াদোত্তীর্ণ হওয়ার সময় (Unix timestamp = `iat + JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)।

---

### ঘ. প্রোটেক্টেড রাউট: কারেন্ট ইউজার ফেচিং (Protected Route: Get Me)

অথেনটিকেটেড ইউজার তার নিজস্ব তথ্য ফেচ করতে পারে। এখানে Bearer টোকেন ভ্যালিডেশন প্রক্রিয়া পরীক্ষা করা হয়।

- **Endpoint:** `GET /api/v1/auth/me`
- **Header:** `Authorization: Bearer <access_token>`
- **Status Code:** `200 OK`

#### Success Response (`200 OK`):
```json
{
  "message": "Current user profile retrieved successfully",
  "data": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-10-25T15:50:00Z",
    "updated_at": "2026-10-25T15:50:00Z"
  }
}
```

#### টোকেন ভেরিফিকেশন এররসমূহ:
1. **টোকেনের মেয়াদ শেষ হয়ে গেলে (Expired Token):**
   - Status: `401 Unauthorized`
   ```json
   { "detail": "Token has expired" }
   ```
2. **টোকেন টেম্পারড/ভুল হলে (Invalid Token):**
   - Status: `401 Unauthorized`
   ```json
   { "detail": "Could not validate credentials" }
   ```
3. **টোকেন না পাঠালে (Missing Token):**
   - Status: `401 Unauthorized`
   ```json
   { "detail": "Not authenticated" }
   ```
4. **ইউজার ডাটাবেস থেকে মুছে ফেলা হলে:**
   - Status: `401 Unauthorized`
   ```json
   { "detail": "User not found" }
   ```

---

## ৫. অন্যান্য রাউটে অথেনটিকেশন কীভাবে প্রয়োগ করবেন?

প্রজেক্টের যেকোনো রাউটে অথেনটিকেশন আবশ্যক করতে [`app.api.deps.CurrentUser`](file:///d:/Projects/fastapi/fastapi-blog/src/app/api/deps.py) ডিপেন্ডেন্সি ব্যবহার করতে হবে।

### উদাহরণ (যেমন: পোস্ট তৈরি করার এন্ডপয়েন্ট):

```python
from fastapi import APIRouter, status
from app.api.deps import CurrentUser, DatabaseSession
from app.modules.post.schemas import PostCreate, PostResponse

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    db: DatabaseSession,
    current_user: CurrentUser,  # <--- শুধুমাত্র টোকেনধারী অথেনটিকেটেড ইউজার এক্সেস পাবে
) -> PostResponse:
    # current_user.id এবং current_user.email সরাসরি এখানে ব্যবহারযোগ্য
    print(f"Post created by user: {current_user.email} (ID: {current_user.id})")
    ...
```

---

## ৬. টেস্ট চালানো

অথেনটিকেশন সংক্রান্ত সমস্ত ইউনিট টেস্ট (Registration, Token Generation, Expired Token, Duplicate Prevention, Invalid Input) চালাতে:

```powershell
uv run pytest
```

সবগুলো টেস্ট (২২টি) স্বয়ংক্রিয়ভাবে পাস করবে।
