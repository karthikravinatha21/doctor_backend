# Stage 1: Builder
FROM public.ecr.aws/docker/library/python:3.10-slim AS builder

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    git \
    wget \
    curl \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf-2.0-dev \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    shared-mime-info \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirement.txt .
RUN python -m venv /venv && \
    pip install --no-cache-dir -r requirement.txt && \
    pip install --no-cache-dir gunicorn

# Copy app code
COPY . .

# Stage 2: Runtime
FROM public.ecr.aws/docker/library/python:3.10-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libxml2 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment and app code from builder
COPY --from=builder /venv /venv
COPY --from=builder /app /app

# Static files directory
RUN mkdir -p /app/staticfiles

# Entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh && \
    chown root:root /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Start app
# Start app with Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn -b 0.0.0.0:8000 KALAKSHETRA.wsgi:application"]

