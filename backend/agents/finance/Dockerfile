FROM python:3.11-slim
WORKDIR /app
COPY financialagent/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY financialagent/backend .
COPY packages /packages
EXPOSE 8002
CMD ["python", "main.py"]
