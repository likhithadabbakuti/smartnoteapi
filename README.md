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

## Database Modes

- Default local mode: SQLite file `db.sqlite3` (no extra config needed).
- MySQL mode: set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` in `.env`.
- Mock DB mode (in-memory SQLite): set `USE_MOCK_DB=true` in `.env`.

## Authentication Flow

1. Register a user: `POST /api/auth/register/`
2. Login to get tokens: `POST /api/auth/login/`
3. Refresh access token: `POST /api/auth/refresh/`
4. Send access token in headers:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

### Notes

- `GET /api/notes/`
- `POST /api/notes/`
- `GET /api/notes/{id}/`
- `PUT /api/notes/{id}/`
- `PATCH /api/notes/{id}/`
- `DELETE /api/notes/{id}/`
- `PATCH /api/notes/{id}/favorite/` (toggle favorite status)

Supported query params:

- `search=...` (searches in `title`, `content`)
- `ordering=created_at` or `ordering=-created_at`
- `is_favorite=true|false`
- `tags=<tag_id>`

### Tags

- `GET /api/tags/`
- `POST /api/tags/`
- `GET /api/tags/{id}/`
- `PUT /api/tags/{id}/`
- `PATCH /api/tags/{id}/`
- `DELETE /api/tags/{id}/`

## Example Requests

Use Postman and create requests like below.

1. Register user
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/register/`
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
- URL: `http://127.0.0.1:8000/api/auth/login/`
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
- URL: `http://127.0.0.1:8000/api/auth/refresh/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "refresh": "<refresh_token>"
}
```

4. Create a tag
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/tags/`
- Headers:
  `Authorization: Bearer <access_token>`
  `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "name": "work"
}
```

5. Create a note with tags
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/notes/`
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

6. Search and order notes
- Method: `GET`
- URL example: `http://127.0.0.1:8000/api/notes/?search=plan&ordering=-created_at`
- Headers: `Authorization: Bearer <access_token>`

