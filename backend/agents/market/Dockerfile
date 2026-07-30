FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY market-intelligence-agent/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY market-intelligence-agent/backend .
COPY packages /packages
EXPOSE 8001
CMD ["python", "main.py"]
