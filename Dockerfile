FROM python:3.11-slim

WORKDIR /app

# System dependencies (psycopg2, bcrypt, chromadb ke liye zaroori)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]
