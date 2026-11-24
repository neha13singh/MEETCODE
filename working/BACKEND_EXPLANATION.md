# ⚙️ MeetCode - Backend Technical & File-by-File Working Guide

This document presents a comprehensive, technical explanation of every single file within the MeetCode Backend directory (`backend/`).

---

## 📄 Directory Overview: `backend/`

The backend is built using **FastAPI**, an asynchronous Python framework. It uses **SQLAlchemy 2.0 (Async)** with **`asyncpg`** to connect to PostgreSQL, **Redis** for matchmaking and caching, and **Docker Python SDK** to execute user code in isolated containers.

---

## 1️⃣ Core Application Layer (`backend/app/core/`)

### 🔹 `backend/app/core/config.py`
- **Purpose**: Defines application settings, environment variable parsing, database URL construction, and CORS security rules using Pydantic Settings.
- **Key Mechanics**:
  - `PROJECT_NAME`: Title of the FastAPI application (`"MeetCode"`).
  - `API_V1_STR`: API route prefix (`"/api/v1"`).
  - `SECRET_KEY` & `ALGORITHM`: Used by PyJWT to sign and verify JSON Web Tokens (`HS256`).
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration duration (default 8 days).
  - `BACKEND_CORS_ORIGINS`: Pydantic validator `assemble_cors_origins` splits comma-separated strings or lists into valid HTTP URLs to allow frontend cross-origin requests.
  - `SQLALCHEMY_DATABASE_URI`: Pydantic validator `assemble_db_connection` dynamically constructs an async PostgreSQL connection string (`postgresql+asyncpg://user:password@host:port/dbname`). It cleans out incompatible query flags like `sslmode` or `channel_binding` for `asyncpg` compliance.
- **Technologies**: `pydantic-settings`, `Pydantic BaseSettings`, `urllib.parse`.

### 🔹 `backend/app/core/logging.py`
- **Purpose**: Configures structured logging across the application.
- **Key Mechanics**: Sets up `logging.basicConfig` with explicit formatters (`%(asctime)s - %(name)s - %(levelname)s - %(message)s`) and log levels (INFO/DEBUG) so that terminal and Docker logs output clean diagnostic details.

---

## 2️⃣ Database Layer (`backend/app/db/`)

### 🔹 `backend/app/db/base_class.py`
- **Purpose**: Standardized Declarative Base class for all ORM entities.
- **Key Mechanics**: Defines `Base(DeclarativeBase)`. Inherited by all database models. Uses `__tablename__` resolution or auto-generation.

### 🔹 `backend/app/db/base.py`
- **Purpose**: Centralized export file for Alembic database migration discovery.
- **Key Mechanics**: Imports `Base` from `base_class.py` and all SQLAlchemy models (`User`, `Question`, `TestCase`, `CodeTemplate`, `Match`, `MatchParticipant`, `Submission`). Ensures Alembic detects all tables when generating automatic migrations.

### 🔹 `backend/app/db/session.py`
- **Purpose**: Manages asynchronous database connection pools and session creation.
- **Key Mechanics**:
  - `create_async_engine`: Initializes SQLAlchemy's `AsyncEngine` with `echo=False` and connection pool settings.
  - `AsyncSessionLocal`: `async_sessionmaker` bound to the engine with `expire_on_commit=False`.
  - `get_db()`: Async generator function yielded via FastAPI's `Depends(get_db)` to supply an isolated database session per request and guarantee automatic closure upon request completion.

---

## 3️⃣ ORM Database Models (`backend/app/models/`)

### 🔹 `backend/app/models/user.py`
- **Entity**: `User` table (`users`).
- **Fields**:
  - `id`: UUID Primary Key (`uuid.uuid4`).
  - `username`: Unique indexed string (max 50 chars).
  - `email`: Unique indexed string (max 255 chars).
  - `password_hash`: Bcrypt hashed password string.
  - `elo_rating`: Integer (defaults to `1200`).
  - `total_matches`, `wins`: Track user performance metrics.
  - `created_at`, `updated_at`: Timezone-aware UTC timestamps.

### 🔹 `backend/app/models/question.py`
- **Entities**: `Question`, `TestCase`, `CodeTemplate` tables.
- **Fields & Relationships**:
  - `Question`: Represents a coding problem. Stores `title`, `slug`, `description` (Markdown), `difficulty` (`easy`, `medium`, `hard`), `avg_solve_time`, `acceptance_rate`, `constraints`, `tags` (JSON), and `examples` (JSON).
  - `TestCase`: Belongs to `Question` via foreign key (`question_id`). Stores `input` string, `expected_output` string, `is_hidden` (boolean for submission verification), `is_sample` (boolean for practice display), and `execution_order`.
  - `CodeTemplate`: Belongs to `Question`. Stores language-specific starter boilerplate code (`language`, `template_code`, `starter_code`) for Python, C++, and Java.

### 🔹 `backend/app/models/match.py`
- **Entities**: `Match`, `MatchParticipant` tables (`matches`, `match_participants`).
- **Fields & Relationships**:
  - `Match`: Represents a 1v1 competitive match or solo practice session. Stores `question_id`, `mode` (`practice`, `competitive`, `private`), `difficulty`, `max_time` (seconds), `status` (`waiting`, `active`, `completed`, `timeout`), `started_at`, `completed_at`, and `winner_id` (foreign key to `User`).
  - `MatchParticipant`: Joins `User` to `Match`. Stores participant-specific runtime metrics: `solution_code`, `language`, `execution_time` (ms), `memory_used` (KB), `test_cases_passed`, `total_test_cases`, `result` (`win`, `lose`, `timeout`, `practice_complete`).

### 🔹 `backend/app/models/submission.py`
- **Entity**: `Submission` table (`submissions`).
- **Fields**: Tracks every code execution submission by a user. Stores `user_id`, `question_id`, `match_id` (optional), `code`, `language`, `status` (`Accepted`, `Wrong Answer`, `Runtime Error`, `Compile Error`), `execution_time`, `memory_used`, `passed_test_cases`, and `total_test_cases`.

---

## 4️⃣ Pydantic Data Schemas (`backend/app/schemas/`)

- **`schemas/user.py`**: Defines input validation for registration (`UserCreate`), login, and response structures (`UserResponse`, `UserInDB`).
- **`schemas/question.py`**: Defines payload schemas for creating and displaying questions (`QuestionBase`, `QuestionCreate`, `QuestionDetail`, `TestCaseSchema`).
- **`schemas/match.py`**: Defines requests and responses for initiating matches, private room creation (`PrivateMatchCreate`), joining private rooms (`PrivateMatchJoin`), and match summaries.
- **`schemas/submission.py`**: Validates code submission requests (`SubmissionCreate`: `code`, `language`, `question_id`, `match_id`) and formats execution result responses (`SubmissionResponse`).

---

## 5️⃣ Service Layer (`backend/app/services/`)

### 🔹 `backend/app/services/auth_service.py`
- **Purpose**: Cryptographic password management and JWT token generation.
- **Key Mechanics**:
  - `CryptContext`: Uses `passlib.context.CryptContext` with `bcrypt` scheme.
  - `verify_password(plain, hashed)`: Checks password validity.
  - `get_password_hash(password)`: Generates salted bcrypt hash.
  - `create_access_token(data, expires_delta)`: Encodes JWT with subject (`sub`), issued timestamp (`iat`), and expiration (`exp`) signed by `settings.SECRET_KEY`.

### 🔹 `backend/app/services/execution_service.py`
- **Purpose**: Docker container orchestration for safe code execution.
- **Key Mechanics**: Communicates with Docker daemon to launch isolated container runners (`meetcode-python`, `meetcode-cpp`, `meetcode-java`). Restricts CPU (50%), RAM (128MB), disables network access, and runs under non-root user `coderunner`. Inject payload into container using custom tar stream (`_create_tar_stream`). Detailed breakdown in [EXECUTION_ENGINE.md](./EXECUTION_ENGINE.md).

### 🔹 `backend/app/services/matchmaking_service.py`
- **Purpose**: Redis-backed player matchmaking and private match lobby management.
- **Key Mechanics**:
  - `add_to_queue(user_id, difficulty)`: Adds user to Redis Sorted Set (`matchmaking:queue:{difficulty}`) with current timestamp as score.
  - `check_queue(difficulty, db)`: Uses Redis `zpopmin` to atomically pop the 2 oldest waiting players. If 2 players exist, selects a random question from PostgreSQL and initializes an active `Match` record.
  - `create_private_match(db, user_id, difficulty)`: Generates a random 6-character alphanumeric room code, stores it in Redis (`private_match:{code}`) with a 600s (10 min) TTL, and creates a `Match` in `waiting` state.
  - `join_private_match(db, user_id, code)`: Retrieves match ID from Redis key, adds player 2, sets match status to `active`, and invalidates the room code.

### 🔹 `backend/app/services/websocket_manager.py`
- **Purpose**: Manages active WebSocket connections and match-level broadcast groups.
- **Key Mechanics**:
  - `active_connections`: In-memory map of `user_id -> WebSocket`.
  - `match_connections`: In-memory map of `match_id -> List[user_id]`.
  - `user_to_match`: Mapping of connected user IDs to active match IDs.
  - `send_personal_message(message, user_id)`: Dispatches JSON frame to specific client socket.
  - `broadcast_match_event(match_id, event_type, data)`: Sends event frames to all participants in a given match.

---

## 6️⃣ API Endpoints (`backend/app/api/`)

### 🔹 `backend/app/api/deps.py`
- **Purpose**: FastAPI Dependency Injection providers.
- **Key Mechanics**:
  - `get_current_user`: Extracts JWT from `Authorization: Bearer <token>` header, decodes payload, retrieves user from PostgreSQL, and rejects invalid/expired requests with HTTP 401.

### 🔹 `backend/app/api/auth.py`
- **Endpoints**:
  - `POST /api/v1/auth/register`: Hashes password, creates new `User`, returns JWT access token.
  - `POST /api/v1/auth/login`: Verifies credentials via `auth_service`, returns JWT token.
  - `GET /api/v1/auth/me`: Returns details of authenticated user.

### 🔹 `backend/app/api/questions.py`
- **Endpoints**:
  - `GET /api/v1/questions/`: Lists available coding questions (supports filtering by difficulty/tags).
  - `GET /api/v1/questions/{id}`: Returns complete question statement, sample test cases, and language starter templates.

### 🔹 `backend/app/api/matches.py`
- **Endpoints**:
  - `GET /api/v1/matches/{id}`: Fetches match details, question text, participants, and time remaining.
  - `POST /api/v1/matches/`: Creates a match manually or initiates solo practice.

### 🔹 `backend/app/api/submissions.py`
- **Endpoints**:
  - `POST /api/v1/submissions/run`: Runs code against sample test cases via `ExecutionService` without saving to DB.
  - `POST /api/v1/submissions/submit`: Runs code against ALL test cases (including hidden ones). Persists a `Submission` entity. If in a 1v1 match and all test cases pass, marks user as winner, finishes match, updates Elo ratings, and broadcasts `match:completed` via WebSockets.

### 🔹 `backend/app/api/users.py`
- **Endpoints**:
  - `GET /api/v1/users/profile`: Retrieves profile details, total wins, losses, win rate, and match history.

### 🔹 `backend/app/api/websocket.py`
- **Endpoint**: `/ws?token=<JWT>`
- **Purpose**: Real-time duplex socket server. Handles:
  - `queue:join` & `queue:leave`: Matchmaking queue controls + 60-second timeout handler (`handle_queue_timeout`) which auto-converts waiting users to solo practice.
  - `match:join`: Connects client to match event channel.
  - `match:create_private` & `match:join_private`: Private room lifecycle.
  - `WebSocketDisconnect`: Detects player dropouts during active competitive matches and automatically issues a forfeit win to the remaining opponent.

---

## 7️⃣ Root Backend Utilities & Scripts

- **`backend/app/main.py`**: The FastAPI application entry point. Enables CORS middleware, attaches logging setup, includes API routers (`auth`, `users`, `questions`, `submissions`, `matches`, `websocket`), and exposes `/`.
- **`backend/seed_questions.py`**: Populates the database with real coding questions (e.g., Two Sum, Reverse Linked List, Valid Parentheses), sample test cases, hidden verification test cases, and starter templates for Python, C++, and Java.
- **`backend/init_db.py`**: Initializes database tables asynchronously.
- **`backend/create_test_users.py`**: Creates initial mock users for development testing.
- **`backend/list_users.py`**: Command-line helper to view registered database users.
- **`backend/verify_invite.py`**: Internal diagnostic script for verifying user invite codes and match tokens.

---

## 8️⃣ Database Migrations (`backend/alembic/`)

- **`backend/alembic/env.py`**: Configures Alembic's migration engine to run asynchronously using `asyncpg`. Reads `target_metadata` from `app.db.base`.
- **`backend/alembic/script.py.mako`**: Template file for generating Python migration revisions.
- **`backend/alembic/versions/0d3fa0005f34_init.py`**: Initial schema migration creating `users`, `questions`, `test_cases`, `code_templates`, `matches`, `match_participants`, and `submissions` tables.
