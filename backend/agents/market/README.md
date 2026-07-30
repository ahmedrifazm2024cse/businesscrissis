# Market Intelligence Agent Backend

FastAPI Python service designed to analyze competitor indices, news alerts, and demand changes, and invoke CrewAI agents for executive crisis summaries.

## Getting Started

### Prerequisites
- Python 3.10+
- Virtual Environment tool (`venv`)

### Installation & Run

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment variables file and configure key values:
   ```bash
   cp .env.example .env
   ```
5. Start the server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`. You can access automated Swagger documentation at `http://localhost:8000/docs`.
