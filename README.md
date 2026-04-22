# Smart Note API

A Django REST API for user-authenticated note and tag management with JWT-based authentication.

## Features

- User registration and JWT login/refresh
- CRUD operations for notes and tags
- Per-user access control (users can only access their own data)
- Note search, filtering, and ordering
- Mark/unmark notes as favorite

## Tech Stack

- Python 3.13
- Django 6
- Django REST Framework
- django-filter
- djangorestframework-simplejwt
- SQLite (default)

## Setup

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py migrate
```

5. Run the server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Testing and Coverage

Run tests:

```bash
python manage.py test
```

Run tests with coverage and show percentage:

```bash
coverage run manage.py test
coverage report
```

Generate HTML coverage report:

```bash
coverage html
```

Open `htmlcov/index.html` in your browser to view the detailed report.

## Database Modes

- Default local mode: SQLite file `db.sqlite3` (no extra config needed).
- MySQL mode: set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` in `.env`.
- Mock DB mode (in-memory SQLite): set `USE_MOCK_DB=true` in `.env`.

## Authentication Flow

1. Register a user: `POST /api/v1/auth/register/`
2. Login to get tokens: `POST /api/v1/auth/login/`
3. Refresh access token: `POST /api/v1/auth/refresh/`
4. Get current user profile: `GET /api/v1/auth/me/`
5. Send access token in headers:

```http
Authorization: Bearer <access_token>
```

Registration role behavior:
- Default role is `user`.
- To create a `staff` user, pass `"role": "staff"` and `"staff_registration_key": "<key>"`.
- Configure the key in environment as `STAFF_REGISTRATION_KEY`.

### staff_registration_key Guide

What it is:
- `staff_registration_key` is a private secret you create.
- Django does not generate it automatically.
- It is checked only when someone tries to register with `role = "staff"`.

When to use it:
- Use it only for creating trusted `staff` accounts.
- Do not use it for normal user signup.

How to create it (PowerShell):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

How to configure it:
1. Copy the generated secret.
2. Add it to `.env`:

```env
STAFF_REGISTRATION_KEY=your_generated_secret_here
```

3. Restart the Django server.

How to call register API:
- Normal user (no role provided, defaults to `user`):

```json
{
  "username": "alice",
  "password": "StrongPass123!"
}
```

- Staff user (requires valid key):

```json
{
  "username": "bob",
  "password": "StrongPass123!",
  "role": "staff",
  "staff_registration_key": "your_generated_secret_here"
}
```

Expected behavior:
- If `role` is missing, account is created with `is_staff = false`.
- If `role = "staff"` and key is valid, account is created with `is_staff = true`.
- If key is missing or invalid, registration fails with validation error.

Security notes:
- Keep this key private and never expose it in client-side code.
- Rotate it immediately if it is leaked.

## API Endpoints

### Auth

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `GET /api/v1/auth/me/`

Compatibility alias:
- `GET /api/auth/me/` also maps to the same profile endpoint.

### Notes

- `GET /api/v1/notes/`
- `POST /api/v1/notes/`
- `GET /api/v1/notes/{id}/`
- `PUT /api/v1/notes/{id}/`
- `PATCH /api/v1/notes/{id}/`
- `DELETE /api/v1/notes/{id}/`
- `PATCH /api/v1/notes/{id}/favorite/` (toggle favorite status)

Supported query params:

- `search=...` (searches in `title`, `content`)
- `ordering=created_at` or `ordering=-created_at`
- `is_favorite=true|false`
- `tags=<tag_id>`

### Tags

- `GET /api/v1/tags/`
- `POST /api/v1/tags/`
- `GET /api/v1/tags/{id}/`
- `PUT /api/v1/tags/{id}/`
- `PATCH /api/v1/tags/{id}/`
- `DELETE /api/v1/tags/{id}/`

## Example Requests

Use Postman and create requests like below.

1. Register user
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/auth/register/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "username": "alice",
  "password": "secret123"
}
```

2. Login (get access and refresh token)
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/auth/login/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "username": "alice",
  "password": "secret123"
}
```

3. Refresh access token
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/auth/refresh/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "refresh": "<refresh_token>"
}
```

4. Get current user profile
- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/auth/me/`
- Headers: `Authorization: Bearer <access_token>`
- Example response:

```json
{
  "id": 1,
  "username": "alice",
  "role": "user",
  "is_staff": false
}
```

5. Create a tag
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/tags/`
- Headers:
  `Authorization: Bearer <access_token>`
  `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "name": "work"
}
```

6. Create a note with tags
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/notes/`
- Headers:
  `Authorization: Bearer <access_token>`
  `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "title": "Plan",
  "content": "Sprint tasks",
  "tag_ids": [1]
}
```

7. Search and order notes
- Method: `GET`
- URL example: `http://127.0.0.1:8000/api/v1/notes/?search=plan&ordering=-created_at`
- Headers: `Authorization: Bearer <access_token>`

