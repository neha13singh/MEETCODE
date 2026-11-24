# 💻 MeetCode - Frontend Technical & File-by-File Working Guide

This document presents a comprehensive, technical explanation of every single file within the MeetCode Frontend directory (`frontend/`).

---

## 📄 Directory Overview: `frontend/`

The frontend is built with **Next.js 14 (App Router)** in **TypeScript**, styled using **Tailwind CSS**, and features an integrated **Monaco Code Editor** (`@monaco-editor/react`) for real-time code editing.

---

## 1️⃣ Configuration & Build System (`frontend/`)

### 🔹 `frontend/package.json`
- **Purpose**: Defines dependencies, scripts, and package versions.
- **Key Dependencies**:
  - `next`: Next.js 14 React framework.
  - `@monaco-editor/react`: Visual Studio Code editor wrapper for React.
  - `axios`: Promise-based HTTP client for API communications.
  - `lucide-react`: Modern icon library used throughout the UI.
  - `canvas-confetti` & `@types/canvas-confetti`: Confetti particle animations on winning matches.
  - `jwt-decode`: Client-side JWT token decoding.
  - `tailwindcss`, `postcss`, `autoprefixer`: CSS styling pipeline.

### 🔹 `frontend/tsconfig.json`
- **Purpose**: TypeScript configuration options.
- **Key Settings**: Sets path aliases (`@/*` mapping to `./src/*`), enables strict type checking, and configures Next.js JSX transformation options.

### 🔹 `frontend/next.config.ts`
- **Purpose**: Next.js custom configuration. Configures React Strict Mode and environment variable mappings (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`).

### 🔹 `frontend/Dockerfile` & `.env.local`
- **`Dockerfile`**: Multi-stage build (deps, builder, runner) optimizing production Node.js execution size and startup performance.
- **`.env.local`**: Configures client-side environment variables:
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
  ```

---

## 2️⃣ Core Pages & Routing (`frontend/src/app/`)

### 🔹 `frontend/src/app/layout.tsx`
- **Purpose**: Root layout component wrapping all pages.
- **Key Mechanics**: Configures Google Font (`Inter`), injects global styles (`globals.css`), wraps application inside `<AuthProvider>` to provide global authentication state, and renders the top navigation bar `<Navbar />`.

### 🔹 `frontend/src/app/page.tsx`
- **Purpose**: Platform landing home page (`/`).
- **Key Mechanics**:
  - Hero banner with dynamic call-to-action buttons ("Find 1v1 Match", "Solo Practice").
  - Live statistics display (active users, total matches played, questions available).
  - Feature grid highlighting real-time collaboration, sandboxed code execution, and Elo leaderboard rating.

### 🔹 `frontend/src/app/(auth)/login/page.tsx`
- **Purpose**: User login page (`/login`).
- **Key Mechanics**: Handles form submission for user credentials (`username`/`password`). Calls `/api/v1/auth/login` via `apiClient`, extracts returned JWT access token, invokes `login(token)` from `AuthContext`, and redirects user to home page.

### 🔹 `frontend/src/app/(auth)/register/page.tsx`
- **Purpose**: User registration page (`/register`).
- **Key Mechanics**: Collects `username`, `email`, and `password`. Sends payload to `/api/v1/auth/register`. On success, automatically logs the user in and redirects to home.

### 🔹 `frontend/src/app/matchmaking/page.tsx`
- **Purpose**: Matchmaking hub page (`/matchmaking`).
- **Key Mechanics**:
  - **Difficulty Selection Cards**: Easy, Medium, Hard.
  - **1v1 Matchmaking Queue**: Connects to WebSocket endpoint (`ws://localhost:8000/ws?token=...`). Sends `queue:join` event. Displays animated modal counting search time. Listens for `match:found` or `match:practice` events to redirect to the code editor.
  - **Private Room Creator**: Sends `match:create_private` event over WebSocket. Receives a 6-character room code to share with friends.
  - **Private Room Joiner**: Modal allowing entry of a 6-character code. Sends `match:join_private` event over WebSocket.

### 🔹 `frontend/src/app/editor/[matchId]/page.tsx`
- **Purpose**: The core IDE and coding arena page (`/editor/[matchId]`).
- **Key Mechanics**:
  - **Monaco Code Editor**: Configures language (Python, C++, Java), editor theme (`vs-dark`), font size, autocomplete options, and code change tracking.
  - **Split Panel UI**: Left panel displays question statement, constraints, examples, sample test cases (`TestCasesList`), and submission history (`SubmissionsList`). Right panel hosts Monaco editor, language selector, and execution control toolbar ("Run Code", "Submit Solution").
  - **Real-Time WebSocket Sync**: Connects to `/ws` with `matchId`. Listens for `match:completed` events (opponent submission or forfeit).
  - **Match Countdown Timer**: Renders remaining match time. Auto-submits or triggers timeout modal when time reaches 0.
  - **Winning Modal & Confetti**: When a submission passes all test cases or opponent forfeits, triggers `canvas-confetti` fireworks overlay and displays victory statistics.

### 🔹 `frontend/src/app/practice/page.tsx`
- **Purpose**: Solo problem catalog (`/practice`).
- **Key Mechanics**: Fetches questions list from `/api/v1/questions/`. Supports filtering by difficulty and search terms. Clicking a question initiates a solo practice match.

### 🔹 `frontend/src/app/profile/page.tsx`
- **Purpose**: User profile & analytics dashboard (`/profile`).
- **Key Mechanics**: Calls `/api/v1/users/profile`. Displays Elo rating score badge, win/loss stats, win rate percentage progress bars, and recent match submission logs.

---

## 3️⃣ Reusable UI Components (`frontend/src/components/`)

### 🔹 `frontend/src/components/Navbar.tsx`
- **Purpose**: Top navigation header bar.
- **Key Mechanics**: Displays logo, main navigation links (Practice, Matchmaking, Leaderboard), user login/register buttons (or user avatar & logout menu when authenticated), and Elo rating badge.

### 🔹 `frontend/src/components/LoginModal.tsx`
- **Purpose**: Quick login dialog popup usable from anywhere in the application without navigating away.

### 🔹 `frontend/src/components/MainLayout.tsx`
- **Purpose**: Wrapper layout providing consistent margins, background gradients, and container width constraints.

### 🔹 `frontend/src/components/TestCasesList.tsx`
- **Purpose**: Interactive tabbed component inside the code editor showing test case inputs, expected outputs, actual outputs, execution time, and stdout/stderr logs.

### 🔹 `frontend/src/components/SubmissionsList.tsx`
- **Purpose**: History log panel inside the editor showing previous solution submission attempts, timestamp, status (`Accepted`/`Wrong Answer`), and runtime metrics.

### 🔹 Components in `frontend/src/components/ui/`:
- **`badge.tsx`**: Difficulty badges (Green for Easy, Yellow for Medium, Red for Hard).
- **`button.tsx`**: Styled action buttons with primary, secondary, danger, and outline variants.
- **`card.tsx`**: Glassmorphic container cards with headers, content, and footer slots.

---

## 4️⃣ Application Context & Utilities (`frontend/src/lib/` & `context/`)

### 🔹 `frontend/src/context/AuthContext.tsx`
- **Purpose**: Global authentication React Context.
- **Key Mechanics**:
  - Checks `localStorage.getItem('token')` on app load.
  - `fetchUser()`: Calls `/api/v1/auth/me` to hydrate user profile.
  - `login(token)`: Persists JWT token in local storage, fetches user profile, redirects home.
  - `logout()`: Removes token, resets state to `null`, redirects to home page.
  - Provides `useAuth()` custom hook to any component.

### 🔹 `frontend/src/lib/api/client.ts`
- **Purpose**: Axios HTTP client configuration.
- **Key Mechanics**: Configures `baseURL` (`process.env.NEXT_PUBLIC_API_URL`). Attaches request interceptor that reads JWT token from `localStorage` and injects `Authorization: Bearer <token>` header into every outgoing request.

### 🔹 `frontend/src/lib/api/matches.ts`, `questions.ts`, `submissions.ts`
- Modulized helper modules wrapping Axios endpoints for match fetching, question listing, code execution (`runCode`), and code submission (`submitSolution`).

### 🔹 `frontend/src/lib/logger.ts` & `utils.ts`
- **`logger.ts`**: Client-side logging utility with level filtering (info, warn, error).
- **`utils.ts`**: CSS class merger function (`cn`) wrapping `clsx` and `tailwind-merge`.
