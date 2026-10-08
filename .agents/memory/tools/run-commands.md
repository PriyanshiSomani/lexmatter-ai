# Tool Runbook: Commands & Execution

## 1. Full-Stack Docker Deployment
* **Start all services (PostgreSQL pgvector, Backend, Frontend):**
  ```powershell
  docker compose up -d
  ```
* **Rebuild containers after backend/frontend updates:**
  ```powershell
  docker compose up --build -d
  ```
* **View container logs:**
  ```powershell
  docker compose logs -f
  ```
* **Stop services & wipe database volume:**
  ```powershell
  docker compose down -v
  ```

## 2. Local Backend (FastAPI)
* **Start local development server:**
  ```powershell
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```
* **Apply database migrations:**
  ```powershell
  cd backend
  alembic upgrade head
  ```
* **Swagger API Documentation:** Open `http://localhost:8000/docs` in your browser.

## 3. Local Frontend (Next.js 14)
* **Start dev server:**
  ```powershell
  cd frontend
  npm run dev
  ```
  App opens at `http://localhost:3000`.
* **Build & Typecheck:**
  ```powershell
  cd frontend
  npm run build
  ```

## 4. Test Suite Execution (Pytest)
* **Run all 35 test suites:**
  ```powershell
  pytest backend/tests
  ```
* **Run specific test file with verbose output:**
  ```powershell
  pytest backend/tests/test_workflow_checkpointer.py -v -s
  ```
