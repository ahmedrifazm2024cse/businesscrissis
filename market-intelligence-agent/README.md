# Business Crisis Commander - Market Intelligence Agent

Continuous monitoring of external market conditions, competitor movements, pricing changes, and demand indicators to calculate risk indices and advise executives.

## Project Structure

```
market-intelligence-agent/
├── backend/          # FastAPI Python service, CrewAI workspace
├── frontend/         # React, TS, Vite, Tailwind CSS SPA dashboard
├── sample-data/      # CSV base datasets
├── docs/             # API specifications
└── docker-compose.yml# Multi-service container definitions
```

## Tech Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Chart.js, React Router, TanStack Query
- **Backend**: FastAPI, Pydantic, Pandas, Scikit-learn, SQLite/PostgreSQL, CrewAI

## Execution Instructions

### Run via Docker Compose (Recommended)
From the root directory, simply execute:
```bash
docker-compose up --build
```
- **Frontend SPA**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

### Run Manually

#### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Initialize environment config:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies and run:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

#### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
