FROM python:3.11-slim
WORKDIR /app
COPY legalcomplainaceagent/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY legalcomplainaceagent/backend .
COPY packages /packages
EXPOSE 8003
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8003"]
