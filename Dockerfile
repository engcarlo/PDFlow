# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install system dependencies once at the start
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Evita .pyc e garante logs sem buffer (útil para acompanhar o container)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user early for better layer caching
RUN useradd --create-home --no-log-init -u 1001 appuser

WORKDIR /app

# Copy only requirements for optimal layer caching
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies with pip cache optimization
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py"]
