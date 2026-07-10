# 🔐 JWT Authentication API (FastAPI + PostgreSQL)

A REST API built with FastAPI demonstrating secure user authentication using JWT access tokens, refresh token rotation, refresh token reuse detection, and token family revocation.

This project was built to explore modern backend architecture, authentication security patterns, database design, token lifecycle management, and integration testing using Python.

**Last updated:** 10-07-2026

---

# ✨ Features

- User registration and authentication
- JWT-based access tokens (short-lived)
- JWT refresh tokens for SPA applications
- Refresh token rotation
- Refresh token reuse detection
- Token family revocation after detected reuse
- Refresh tokens stored as SHA-256 hashes
- Unique refresh token identity using JWT `jti`
- Refresh token replacement tracking using `replaced_by_jti`
- Refresh token parent tracking using `parent_jti`
- Logout single session
- Logout all sessions
- Expired and revoked refresh token cleanup
- Admin refresh token purge endpoint
- Protected API routes
- PostgreSQL database integration (Neon)
- Database migrations with Alembic
- Swagger / OpenAPI documentation
- Layered backend architecture
- Manual JWT validation tests
- Manual authentication integration tests
- Vue 3 frontend authentication testing client

---

# 🧰 Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL (Neon)
- SQLAlchemy
- Alembic
- PyJWT
- Pydantic
- Requests
- Vue 3

---

# 🏗️ Project Architecture

The project follows a layered architecture to separate responsibilities:

- routes
  - API endpoints
  - HTTP request handling

- services
  - Authentication logic
  - Token lifecycle management
  - Business rules

- models
  - SQLAlchemy database models

- schemas
  - Pydantic request and response validation

- security
  - Password hashing
  - JWT creation and validation

- db
  - Database configuration
  - Database sessions

- tests
  - Manual JWT tests
  - Manual integration tests

The architecture is intentionally kept simple and focused on secure authentication flows.

---

# 🔐 Authentication Flow

The system uses JWT authentication with refresh token rotation and refresh token reuse detection.

## Login Flow

1. User logs in using username and password.

2. Server validates credentials.

3. Server creates:

- Access token
- Refresh token

4. Refresh token information is stored in PostgreSQL:

- SHA-256 token hash
- JWT `jti`
- Expiration time
- Token relationship information

5. Client receives:

- Access token
- Refresh token

---

# 🔄 Refresh Token Rotation

When the access token expires:

Client sends:

POST `/refresh-token-spa`

The server validates:

- JWT signature
- Token type
- JWT expiration
- Database token record
- Revocation status

If the refresh token is valid:

1. A new access token is created.
2. A new refresh token is created.
3. The old refresh token is revoked.
4. The old token stores the replacement token reference.
5. The new token stores the parent token reference.

Example:

Refresh Token A

↓

Refresh request

↓

Refresh Token A

- revoked_at = timestamp
- replaced_by_jti = Token B

Refresh Token B

- revoked_at = NULL
- parent_jti = Token A

This creates a traceable refresh token chain.

---

# 🛡️ Refresh Token Reuse Detection

Project 2 introduces refresh token reuse detection.

The system detects when a previously rotated refresh token is used again.

Example:

1. User logs in.
2. Server creates Refresh Token A.
3. User refreshes successfully.
4. Server creates Refresh Token B.
5. Refresh Token A is revoked.
6. Someone tries to use Refresh Token A again.

The server detects:

- Token exists in database
- Token is already revoked
- Token has been replaced

The request is rejected:

401 Unauthorized

The system then revokes active refresh tokens belonging to the token family/user to prevent continued misuse.

Example:

Token A

- revoked

Token B

- revoked after reuse detection

This protects against replay attacks using stolen refresh tokens.

---

# ⚙️ Setup Instructions

## 1. Clone Repository

git clone <your-repository-url>

cd <your-project-folder>

---

## 2. Create Virtual Environment

python -m venv .venv

Activate:

Windows PowerShell:

.venv\Scripts\activate

---

## 3. Install Dependencies

pip install -r requirements.txt

---

## 4. Configure Environment Variables

Create a `.env` file:

DATABASE_URL=your_postgres_connection

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=2

REFRESH_TOKEN_EXPIRE_MINUTES=5

---

## 5. Run Database Migration

Create database tables:

alembic upgrade head

---

# 🛠️ Creating New Migrations

After changing SQLAlchemy models:

Create migration:

alembic revision --autogenerate -m "describe your change"

Apply migration:

alembic upgrade head

---

# 🌐 Vue 3 Frontend

A companion Vue 3 frontend is available:

https://github.com/persteenolsen/vue-fastapi-jwt-reuse-detection-auth-client

Features:

- Login flow
- Access token handling
- Refresh token handling
- Protected routes
- Authentication testing

---

# 🧪 Manual Tests

The project contains two manual test suites.

---

# JWT Validation Tests

Tests JWT creation and validation without API calls.

Run:

python -m tests.test_auth_manual

Tests:

- Valid access token
- Wrong token type rejection
- Refresh token type validation
- Expired token rejection
- Invalid signature rejection

---

# Integration Authentication Tests

Tests the complete authentication lifecycle.

Run:

python -m tests.test_integration_auth

Tests:

- Login flow
- Refresh token rotation
- Old refresh token rejection
- Refresh token reuse detection
- Token family revocation
- Logout flow
- Refresh after logout rejection
- Cleanup endpoint

---

# 📊 Example Integration Test Flow

FASTAPI AUTH INTEGRATION TESTS

REFRESH TOKEN ROTATION FLOW

- Login successful
- First refresh successful
- Reuse detected
- Token family revoked


REFRESH TOKEN REUSE DETECTION

- Refresh token rotated
- Refresh token reuse detected
- Active refresh token revoked


LOGOUT FLOW

- Login successful
- Logout successful


REVOKED TOKEN

- Revoked refresh token rejected


TOKEN CLEANUP

- Cleanup executed successfully

---

# 📡 API Endpoints

## Public

POST `/token`

Login endpoint.

Returns:

- Access token
- Token type


POST `/tokens-spa`

SPA login endpoint.

Returns:

- Access token
- Refresh token
- Username


POST `/refresh-token-spa`

Refresh tokens.

Features:

- JWT validation
- Database validation
- Refresh token rotation
- Reuse detection
- Token family revocation


POST `/register`

Create user.

---

## Protected

GET `/users/me`

Returns current authenticated user.


GET `/protected-route`

Protected authentication test endpoint.


GET `/get-all-users`

Returns users.

---

## Admin

POST `/cleanup-tokens`

Removes expired and old revoked refresh tokens.


POST `/admin/purge-refresh-tokens`

Deletes all refresh tokens.

---

# 🛡️ Security Notes

- Passwords are securely hashed
- Access tokens are short-lived
- Refresh tokens are rotated after successful refresh
- Old refresh tokens cannot be reused
- Refresh token reuse is detected
- Refresh tokens are stored as SHA-256 hashes
- JWT identity is tracked using `jti`
- Token replacement relationships are stored
- Token parent relationships are stored
- Database validation is performed during refresh operations

---

# 🚀 Future Improvements

- Move refresh tokens to HttpOnly secure cookies
- Add refresh token reuse detection alerts
- Add rate limiting
- Add pytest-based automated suite
- Add CI/CD pipeline
- Add Redis session tracking
- Add multi-device session management
- Add dedicated refresh token family identifiers

---

# 🎯 Learning Goals

- JWT authentication
- Refresh token rotation
- Refresh token reuse detection
- Secure token lifecycle management
- FastAPI backend architecture
- PostgreSQL database design
- Alembic migrations
- Vue 3 frontend integration
- Authentication testing strategies
- Real-world security patterns

---

# 👨‍💻 Author

Built by Per Olsen

Backend-focused portfolio project exploring authentication systems, secure token handling, and scalable API design.