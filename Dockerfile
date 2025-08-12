# Use Python 3.11 slim image
FROM python:3.11-slim

# Install git & uv package manager
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY main.py ./

# Install dependencies using uv (just the dependencies, not the package itself)
RUN uv pip install --system --no-cache-dir pytelegrambotapi python-dotenv

# Create directory for config and logs
RUN mkdir -p config logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (if needed for webhooks)
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]