
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
<<<<<<< HEAD
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

# stage 2
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app /app.py .
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 5001
=======

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

# Stage 2: Lightweight runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed Python packages
COPY --from=builder /install /usr/local/

# Copy application files
COPY --from=builder /app /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

>>>>>>> 1a94156283e7b6d8980539b8e77e982cc490472b
CMD ["python", "app.py"]
