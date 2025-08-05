FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .

# Expose ports
EXPOSE 5000 8501

# Default command (will be overridden in docker-compose)
CMD ["python", "app.py"]