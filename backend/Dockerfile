FROM pytorch/pytorch:2.2.2-cpu

WORKDIR /app

RUN python -m pip install --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for Google Cloud credentials
RUN mkdir -p /app/secrets

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
