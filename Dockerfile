FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN echo "=== BUILD CONTEXT ROOT ===" && ls -la /app
RUN test -d /app/mentor_mind || (echo "FATAL: mentor_mind folder NOT in build context!" && exit 1)
RUN test -f /app/mentor_mind/__init__.py || (echo "FATAL: mentor_mind/__init__.py MISSING!" && exit 1)
RUN test -f /app/mentor_mind/api/main.py || (echo "FATAL: mentor_mind/api/main.py MISSING!" && exit 1)
RUN echo "=== VERIFIED STRUCTURE ===" && find /app/mentor_mind -maxdepth 1 -type d

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]
