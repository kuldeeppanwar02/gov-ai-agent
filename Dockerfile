# Use official Playwright Python image (pre-installed with all browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries (chromium) with system deps
RUN playwright install chromium --with-deps

# Copy project files
COPY . .

# Expose port (Render injects $PORT, default to 8000 for local)
EXPOSE 8000

# Start command — uses Render's dynamic $PORT or falls back to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
