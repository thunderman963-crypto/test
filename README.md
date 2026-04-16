# 🚀 Django DRF User API

A production-ready REST API built with **Django 5** + **Django REST Framework** + **SimpleJWT**.  
Deployable to **Railway** in under 10 minutes.

---

## 📁 Project Structure

```
django-user-app/
├── core/                   # Django project (settings, urls, wsgi)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                  # Users app
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── .env.example            # Template — copy to .env locally
├── .gitignore
├── manage.py
├── Procfile                # Gunicorn start command
├── railway.toml            # Railway deployment config
├── requirements.txt
├── runtime.txt             # Python version for Railway
└── README.md
```

---

## 📡 API Endpoints

Base URL (local): `http://localhost:8000`  
Base URL (Railway): `https://<your-app>.up.railway.app`

### 🔓 Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Health check |
| `GET`  | `/health/` | Health check (alt) |
| `POST` | `/api/users/register/` | Register new user |
| `POST` | `/api/users/login/` | Login → get JWT tokens |
| `POST` | `/api/users/login/refresh/` | Refresh access token |

### 🔐 Protected Endpoints (Bearer Token Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST`  | `/api/users/logout/` | Logout (blacklists refresh token) |
| `GET`   | `/api/users/me/` | Get own profile |
| `PATCH` | `/api/users/me/update/` | Update own profile |
| `POST`  | `/api/users/me/change-password/` | Change password |

### 👑 Admin-Only Endpoints (role = "admin")

| Method   | Endpoint | Description |
|----------|----------|-------------|
| `GET`    | `/api/users/` | List all users (paginated) |
| `GET`    | `/api/users/<id>/` | Get specific user |
| `PATCH`  | `/api/users/<id>/` | Update specific user |
| `DELETE` | `/api/users/<id>/` | Soft-delete (deactivate) user |

---

## 📋 Request & Response Examples

### 1. Register
```http
POST /api/users/register/
Content-Type: application/json

{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "password": "SecurePass123!",
  "password2": "SecurePass123!"
}
```
**Response 201:**
```json
{
  "message": "Account created successfully.",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "bio": "",
    "avatar_url": null,
    "role": "user",
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOi...",
    "refresh": "eyJ0eXAiOi..."
  }
}
```

---

### 2. Login
```http
POST /api/users/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```
**Response 200:**
```json
{
  "access": "eyJ0eXAiOi...",
  "refresh": "eyJ0eXAiOi...",
  "user": { ...full profile... }
}
```

---

### 3. Get My Profile
```http
GET /api/users/me/
Authorization: Bearer <access_token>
```

---

### 4. Update Profile (Partial)
```http
PATCH /api/users/me/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "bio": "Software developer from NYC",
  "phone": "+19876543210"
}
```

---

### 5. Change Password
```http
POST /api/users/me/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "SecurePass123!",
  "new_password": "NewPass456!",
  "new_password2": "NewPass456!"
}
```

---

### 6. Refresh Token
```http
POST /api/users/login/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

### 7. Logout
```http
POST /api/users/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

### 8. List All Users (Admin)
```http
GET /api/users/?page=1&role=user&search=john
Authorization: Bearer <admin_access_token>
```

---

## 🛠️ Local Development Setup

```bash
# 1. Clone the repo
git clone https://github.com/<you>/<repo>.git
cd django-user-app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and set SECRET_KEY, DEBUG=True, DATABASE_URL=sqlite:///db.sqlite3

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (admin)
python manage.py createsuperuser

# 7. Run dev server
python manage.py runserver
```

---

## 🚂 Railway Deployment (Step-by-Step)

### Prerequisites
- GitHub account
- Railway account → https://railway.app

### Step 1 — Push to GitHub
```bash
cd django-user-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

### Step 2 — Create Railway Project
1. Go to https://railway.app → **New Project**
2. Choose **Deploy from GitHub repo**
3. Authorize Railway and select your repo

### Step 3 — Add PostgreSQL
1. In your Railway project → click **+ New**
2. Select **Database → PostgreSQL**
3. Railway automatically injects `DATABASE_URL` into your app ✅

### Step 4 — Set Environment Variables
In Railway → your service → **Variables** tab, add:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | (generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourdomain.up.railway.app` |
| `CORS_ALLOW_ALL_ORIGINS` | `True` (or `False` + set CORS_ALLOWED_ORIGINS) |

### Step 5 — Deploy
Railway auto-deploys on every `git push` to `main`.  
The `railway.toml` runs `migrate` + `collectstatic` before starting Gunicorn.

### Step 6 — Create Superuser on Railway
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway run python manage.py createsuperuser
```

### Step 7 — Access Your App
- API: `https://yourdomain.up.railway.app/api/users/`
- Admin: `https://yourdomain.up.railway.app/admin/`

---

## ⚠️ Common Mistakes to Avoid (Freshers Guide)

### ❌ Mistake 1 — Committing `.env` or `SECRET_KEY`
- Always add `.env` to `.gitignore`
- Rotate your key immediately if accidentally pushed
- Use `python-decouple` to read from environment variables

### ❌ Mistake 2 — `DEBUG=True` in Production
- Always set `DEBUG=False` in Railway variables
- `DEBUG=True` leaks stack traces and disables security features

### ❌ Mistake 3 — Not running `migrate` on deploy
- Never skip migrations — Railway's `railway.toml` runs it automatically
- Don't commit `db.sqlite3` to git — it will be reset on every deploy

### ❌ Mistake 4 — Forgetting `collectstatic`
- WhiteNoise serves static files in production but needs them collected
- `railway.toml` runs `collectstatic --no-input` before starting

### ❌ Mistake 5 — Using SQLite in Production
- Railway's filesystem is ephemeral — SQLite data disappears on redeploy
- Always attach a PostgreSQL plugin on Railway

### ❌ Mistake 6 — Wrong `ALLOWED_HOSTS`
- Set your Railway domain in `ALLOWED_HOSTS` or you'll get a 400 Bad Request
- Using `*` is fine for testing, use specific domains in production

### ❌ Mistake 7 — Hardcoding the PORT
- Railway assigns a dynamic `$PORT` — always use `--bind 0.0.0.0:$PORT` in Gunicorn
- Never hardcode `:8000` in your Procfile

### ❌ Mistake 8 — Not using a custom User model from the start
- Always define `AUTH_USER_MODEL` before the first migration
- Changing it later requires deleting all migrations and the database

### ❌ Mistake 9 — Storing passwords in plain text
- Always use `user.set_password()` — never assign `user.password = "..."` directly

### ❌ Mistake 10 — No CORS headers
- Your frontend will get blocked without `django-cors-headers`
- `CorsMiddleware` must be the **first** middleware in the list

---

## 🔐 Security Checklist for Production

- [x] `SECRET_KEY` from environment variable (never hardcoded)
- [x] `DEBUG=False`
- [x] Specific `ALLOWED_HOSTS`
- [x] Password hashing via Django's `set_password()`
- [x] JWT refresh token blacklisting on logout
- [x] API throttling (100/day anon, 1000/day user)
- [x] CORS configured
- [x] WhiteNoise for static files (no nginx needed)
- [x] PostgreSQL (not SQLite)
- [x] Soft-delete instead of hard-delete for users

---

## 🧪 Testing with Postman / Thunder Client

Import this base URL: `https://yourdomain.up.railway.app`

**Auth flow:**
1. `POST /api/users/register/` → copy `tokens.access`
2. Set header `Authorization: Bearer <access>` for all protected routes
3. When access expires → `POST /api/users/login/refresh/` with your refresh token

---

## 📦 Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Django | 5.0.4 | Web framework |
| djangorestframework | 3.15.1 | REST API |
| djangorestframework-simplejwt | 5.3.1 | JWT auth |
| django-cors-headers | 4.3.1 | CORS |
| dj-database-url | 2.1.0 | Parse DATABASE_URL |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| python-decouple | 3.8 | Env vars |
| gunicorn | 22.0.0 | Production WSGI server |
| whitenoise | 6.6.0 | Static files |
| Pillow | 10.3.0 | Avatar image handling |
