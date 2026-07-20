# 🚀 MeetCode - Collaborative Coding Platform

Welcome to **MeetCode**, a next-generation coding interview and collaboration platform. MeetCode provides a seamless environment for developers to solve problems, run code in multiple languages, and simulate real-world technical interviews.

![MeetCode Dashboard](path/to/dashboard-image.png)
*(Replace with actual screenshot)*

## ✨ Key Features

- **Multi-Language Support**: Execute Python, C++, and Java code securely in isolated environments.
- **Real-time Collaboration**: (Planned) Code together with peers.
- **Question Bank**: A library of coding challenges to practice.
- **Secure Execution**: Code execution is sandboxed using Docker containers.
- **Modern UI**: Built with Next.js and Tailwind CSS for a premium user experience.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, Tailwind CSS, Monaco Editor
- **Backend**: FastAPI (Python), PostgreSQL, Redis
- **Infra**: Docker, Docker Compose

---

## 🐳 Docker Services & Architecture

MeetCode uses a microservices architecture orchestrated by Docker Compose. Here is a breakdown of each container and its role:

### 1. Frontend (`meetcode-frontend`)
- **Technology**: Next.js (React)
- **Port**: 3000
- **Functionality**: Serves the user interface, handles client-side routing, and communicates with the backend API.
- **Why Docker?**: Ensures consistent Node.js environment and dependencies across development and production.

### 2. Backend (`meetcode-backend`)
- **Technology**: FastAPI (Python)
- **Port**: 8000
- **Functionality**: The core logic engine. It manages users, handles code submissions, and arranges the execution of code in isolated containers.
- **Why Docker?**: Packages Python dependencies and system tools required to manage the execution containers.

### 3. Database (`meetcode-db`)
- **Technology**: PostgreSQL 15 (Alpine)
- **Port**: 5432
- **Functionality**: Persists all application data including user profiles, problem statements, and submission history.
- **Why Docker?**: Provides a production-grade database without needing local installation.

### 4. Cache (`meetcode-redis`)
- **Technology**: Redis 7 (Alpine)
- **Port**: 6379
- **Functionality**: Used for caching frequent queries and managing task queues for asynchronous code execution.
- **Why Docker?**: Fast, in-memory data store that is easily spinnable.

### 5. Execution Containers (Ephemeral)
- **Images**: `meetcode-python`, `meetcode-cpp`, `meetcode-java`
- **Functionality**: These are lightweight, short-lived containers spun up on-demand by the Backend to execute user code safely.
- **Security**: Ensures that user code runs in a sandboxed environment with no network access, preventing malicious actions.

---

## 🏁 Getting Started

You can run MeetCode in two ways: using **Docker (Recommended)** or **Manual Setup**.

### Option 1: Docker (Fastest) 🐳

The easiest way to get up and running.

1.  **Prerequisites**: Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/meetcode.git
    cd meetcode
    ```
3.  **Start Services**:
    ```bash
    docker-compose up -d --build
    ```
    This command will start the Frontend, Backend, Database, and Redis.

4.  **Access the App**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Manual Setup 🔧

If you prefer to run services individually for development.

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload
```

> **Note**: For code execution to work manually, you still need to build the execution images:
> ```bash
> cd backend/execution
> docker build -t meetcode-python .
> ```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Access at [http://localhost:3000](http://localhost:3000).

---

## 📸 Screenshots & Walkthrough

### Code Editor
![Code Editor](path/to/editor-image.png)

### Profile Page
![User Profile](path/to/profile-image.png)

---

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---
