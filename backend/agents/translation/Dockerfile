FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Create directory for models
RUN mkdir -p /app/models

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/models

# Model download commented out for faster build
# Will download on first use instead
# RUN python -c "from transformers import MarianMTModel, MarianTokenizer; \
#     for pair in ['en-es', 'en-fr', 'en-de']: \
#         src, tgt = pair.split('-'); \
#         model_name = f'Helsinki-NLP/opus-mt-{src}-{tgt}'; \
#         print(f'Downloading {model_name}...'); \
#         tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir='/app/models'); \
#         model = MarianMTModel.from_pretrained(model_name, cache_dir='/app/models'); \
#         print(f'Done downloading {model_name}')"

# Expose the port
EXPOSE 8002

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
