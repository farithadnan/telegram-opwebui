# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables for Python best practices
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./

# Install dependencies using uv (just the dependencies, not the package itself)
RUN uv pip install --system --no-cache-dir pytelegrambotapi python-dotenv

# Create non-root user with proper home directory
RUN useradd --create-home --shell /bin/bash --home-dir /home/app app && \
    chown -R app:app /app && \
    chmod g+rw /app && \
    mkdir -p /home/app && \
    chown -R app:app /home/app

# Copy application code after setting up dependencies
COPY main.py ./

# Create necessary directories
RUN mkdir -p config logs && \
    chown -R app:app config logs

# Expose port for health checks and webhooks
EXPOSE 8080

# Switch to the app user
USER app

# Run the application
CMD ["python", "main.py"]