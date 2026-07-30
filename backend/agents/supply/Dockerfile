FROM python:3.11-slim
WORKDIR /app
COPY supllyagent/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY supllyagent/backend .
COPY packages /packages
EXPOSE 8005
CMD ["python", "main.py"]
