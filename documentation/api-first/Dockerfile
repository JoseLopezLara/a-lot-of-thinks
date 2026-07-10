FROM python:3.11-slim

# Set environment variables to optimize Python runtime inside Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if any are needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (volume mount will override this in development, but it's good practice for production builds)
COPY . .

# Expose FastAPI's default port
EXPOSE 8000

# Start Uvicorn development server with hot-reload enabled for code and specs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app", "--reload-dir", "routes", "--reload-dir", "openapi"]


