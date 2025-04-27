FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .
COPY ./common /app/common

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]