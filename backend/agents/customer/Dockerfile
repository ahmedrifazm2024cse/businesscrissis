FROM python:3.11-slim
WORKDIR /app
COPY Customer_Reputation/Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Customer_Reputation/Backend .
COPY packages /packages
EXPOSE 8006
CMD ["python", "main.py"]
