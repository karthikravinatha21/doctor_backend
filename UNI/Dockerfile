# Use Python runtime from Amazon ECR Public Gallery to avoid Docker Hub rate limits
FROM public.ecr.aws/docker/library/python:3.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
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
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    shared-mime-info \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirement.txt /app/

# Create a virtual environment and activate it
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install the required packages
RUN pip install -r requirement.txt
RUN pip install gunicorn

# Copy the rest of the application code into the container
COPY . /app/

# Final stage to copy only necessary files
FROM public.ecr.aws/docker/library/python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH="/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder
COPY --from=builder /venv /venv

# Set the working directory in the container
WORKDIR /app

# Create a directory for static files
RUN mkdir -p /app/staticfiles

# Copy the application code from the builder, excluding the entrypoint script
COPY --from=builder /app /app

# Copy the entrypoint script and set permissions
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
# Convert potential CRLF to LF and ensure script is executable
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh && \
    chown root:root /app/docker-entrypoint.sh

# Expose the port the application will run on
EXPOSE 8000

# Use the entrypoint script to run the application
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
