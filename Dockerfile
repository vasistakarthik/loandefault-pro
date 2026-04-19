# Use Python 3.10 slim for a smaller footprint and stability
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000
ENV HOME=/home/appuser

# Install system dependencies (including Cairo for PDF generation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create application user and setup home
RUN groupadd -r appuser && useradd -r -g appuser -d $HOME -m appuser

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Fix permissions for the entire app and home directory
RUN chown -R appuser:appuser /app $HOME && \
    chmod -R 755 /app

# Switch to non-root user for security
USER appuser

# Expose the application port
EXPOSE 8000

# Health check to ensure the container is running optimally
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1

# Start gunicorn with memory-optimized settings for Render (512MB RAM)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120", "--worker-tmp-dir", "/dev/shm", "backend.app:app"]
