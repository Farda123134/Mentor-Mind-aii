FROM python:3.11-slim

# Working directory set karo
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Requirements pehle copy karo (Docker layer caching ke liye)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── CRITICAL: Poora project copy karo /app mein ──
COPY . /app

# ── PYTHONPATH explicitly set karo ──
# Yeh Python ko batata hai /app mein dhundo imports ke liye
COPY . .

ENV PYTHONPATH=/app:$PYTHONPATH
ENV PORT=8000


EXPOSE 8000

CMD ["python", "start.py"]
