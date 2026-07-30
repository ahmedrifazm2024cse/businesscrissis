FROM python:3.11-slim
WORKDIR /app
COPY cyberagent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cyberagent/backend .
COPY packages /packages
EXPOSE 8004
CMD ["python", "main.py"]
