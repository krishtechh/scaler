FROM python:3.11-slim

# Label for Hugging Face Spaces discovery
LABEL org.opencontainers.image.description="LLM Safeguard Environment — OpenEnv compliant"

WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies using pyproject.toml (multi-mode setup)
COPY requirements-prod.txt ./requirements-prod.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# Copy the rest of the project
COPY . /app

# Perform an editable install of the environment itself
RUN pip install --no-cache-dir -e .

# HF Spaces maps external port 7860
EXPOSE 7860

# Use the established entrypoint from pyproject.toml
CMD ["server"]
