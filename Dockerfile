# Rebuilt from the image history of stoo14/titanic-survival-api (built Sep 30, 2026)
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model artifacts
COPY app.py .
COPY models/ models/

# Expose port
EXPOSE 8000

# Health check
# python:3.11-slim does not ship curl, so the original `curl -f` check could
# never pass. Python's standard library does the same request with no extra install.
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=5)" || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
