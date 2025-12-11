FROM python:3.13-slim

# Do not write .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies if present. Using requirements-dev.txt is
# optional; if you have a `requirements.txt` prefer that instead.
COPY requirements-dev.txt /app/requirements-dev.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements-dev.txt || true

# Copy project files
COPY . /app

# Default entrypoint runs the CLI; users should mount or pass recipient/donor CSVs
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
