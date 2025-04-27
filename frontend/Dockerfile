FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://api-gateway:8000

# Expose the port
EXPOSE 8501

# Start the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
