# LoanRisk AI Protocol - Enterprise Containerization
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=backend.app:app
ENV ENV=production
ENV HOME=/home/appuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libgirepository1.0-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn python-dotenv

# Create necessary directories and set permissions (Using -m to create home dir)
RUN groupadd -r appuser && useradd -m -r -g appuser appuser
RUN mkdir -p backend/database backend/model/models logs
RUN chown -R appuser:appuser /app

# Copy project files
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Expose port

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/ || exit 1

# Set home directory for appuser explicitly
ENV HOME=/home/appuser

# Create directories and fix permissions
RUN mkdir -p /app /home/appuser/.gunicorn && \
    chown -R appuser:appuser /app /home/appuser

WORKDIR /app
USER appuser

EXPOSE 8000

# Use /dev/shm for worker temp to avoid permission issues and improve performance
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120", "--worker-tmp-dir", "/dev/shm", "backend.app:app"]
