# 🏁 MeetCode - Setup & Execution Guide

This document contains step-by-step instructions for running the **MeetCode** collaborative platform.

---

## 🐳 Running Python & Redis in Docker Compose (with Individual DB and Frontend)

This setup runs the **Python Backend** and **Redis** inside Docker containers, while using an **individual/remote PostgreSQL database** (such as Neon PostgreSQL) and running the **React Frontend** locally.

### 1. Pre-build Ephemeral Execution Containers
Before running the main services, you **must** build the specific execution environments that run the user's Python, C++, and Java code:

```bash
# Run these from the project root folder:

# 1. Python Execution Image
docker build -t meetcode-python -f backend/execution/Dockerfile.python backend/execution

# 2. C++ Execution Image
docker build -t meetcode-cpp -f backend/execution/Dockerfile.cpp backend

# 3. Java Execution Image
docker build -t meetcode-java -f backend/execution/Dockerfile.java backend
```

### 2. Configure & Start Services
The `docker-compose.yml` file is configured to run the backend and Redis. The backend is configured to connect to your PostgreSQL database. You can customize the connection string by setting the `SQLALCHEMY_DATABASE_URI` environment variable, or it will default to your configured database details.

Start the containers:
```bash
docker compose up -d --build
```

### 3. Initialize & Seed Database
Wait a few seconds for the backend to start up, then run the database migrations and data seeds:
```bash
# Create all tables & schema
docker compose exec backend python init_db.py

# Seed 30 initial interview questions
docker compose exec backend python seed_questions.py

# (Optional) Register mock test users and output authentication tokens
docker compose exec backend python create_test_users.py
```

### 4. Run Frontend Locally (Individual Setup)
Since the frontend is not run in Docker:
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at [http://localhost:3000](http://localhost:3000).

### 5. Accessing Application Logs & APIs
*   **Backend FastAPI Server**: [http://localhost:8000](http://localhost:8000)
*   **Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Backend Logs**: `./logs/backend/meetcode.log`

---

## 🧠 Running Backend in Docker & Other Services Locally

Use this setup if you want to run the **FastAPI Backend** and the **Python Sandbox** inside Docker, but run your **Database, Redis, and React Frontend** locally on your host machine.

### 1. Build the Python Sandbox Image
Run this from the project root folder:
```bash
docker build -t meetcode-python -f backend/execution/Dockerfile.python backend/execution
```

### 2. Start the Backend Container
Run the backend-only compose file:
```bash
docker compose -f docker-compose.backend-only.yml up -d --build
```
> [!NOTE]
> The backend container is configured to connect to the database and Redis on the host machine using `host.docker.internal`.
> It also mounts the host's `/var/run/docker.sock` so it can spawn the `meetcode-python` sandbox container on your local machine.

### 3. Initialize & Seed Database
Ensure your local PostgreSQL database (`meetcode_dev`) is running, then run:
```bash
docker compose -f docker-compose.backend-only.yml exec backend python init_db.py
docker compose -f docker-compose.backend-only.yml exec backend python seed_questions.py
```

### 4. Run the React Frontend (Locally)
1. Ensure Node.js is installed locally on your machine.
2. Navigate to `frontend/`, install dependencies, and run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🔧 Running Locally (Full Manual Setup)

Follow these instructions to run the frontend, backend, database, and Redis locally on your host machine, using Docker **only** for the Python execution sandbox.

### Prerequisites
- **Docker** running on your host machine (required for code execution sandbox)
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** running locally (default: port `5432` with database `meetcode_dev` and user `meetcode`)
- **Redis** running locally (default: port `6379`)

---

### 1. Build the Python Sandbox Image (Docker)
Before running the backend, you must build the Python container image that the backend will spawn to execute code:
```bash
docker build -t meetcode-python -f backend/execution/Dockerfile.python backend/execution
```

---

### 2. Run the Backend
1. **Configure Environment Variables**:
   We have created a [backend/.env](file:///d:/Projects/Meetcode/MEETCODE/backend/.env) file. Open it and modify the values (database host, username, password, Redis host) to match your local services.

2. **Navigate and Set Up Virtual Environment**:
   ```bash
   cd backend
   ```
   ```bash
   # Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux:
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database and Seed Questions**:
   ```bash
   python init_db.py
   python seed_questions.py
   ```

5. **Start FastAPI Server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The backend will start at `http://localhost:8000`.

---

### 3. Run the Frontend (React)
1. **Navigate and Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Next.js Client**:
   ```bash
   npm run dev
   ```
   The frontend will start at `http://localhost:3000`. It will read configuration from [frontend/.env.local](file:///d:/Projects/Meetcode/MEETCODE/frontend/.env.local) to connect to your backend.

