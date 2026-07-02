FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Poora build context copy karo
COPY . /app

# ── HARD VERIFICATION: Agar mentor_mind nahi mila, BUILD FAIL HOGA ──
# Yeh guess nahi hai — agar yeh line fail hoti hai, matlab
# proof mil gaya ki build context mein mentor_mind hai hi nahi
RUN test -d /app/mentor_mind || (echo "FATAL: mentor_mind folder NOT in build context!" && exit 1)
RUN test -f /app/mentor_mind/__init__.py || (echo "FATAL: mentor_mind/__init__.py MISSING!" && exit 1)
RUN test -f /app/mentor_mind/api/main.py || (echo "FATAL: mentor_mind/api/main.py MISSING!" && exit 1)

# Proof ke liye structure print karo build logs mein
RUN echo "=== VERIFIED STRUCTURE ===" && \
    find /app/mentor_mind -maxdepth 1 -type d && \
    echo "=== main.py EXISTS ===" && \
    ls -la /app/mentor_mind/api/main.py

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]
