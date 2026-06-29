# FlightOps AI — containerized multi-agent system
# Build:  docker build -t flightops-ai .
# Run:    docker run --rm flightops-ai                       # mock mode (offline)
# Live:   docker run --rm -e ANTHROPIC_API_KEY=sk-... flightops-ai
# Evals:  docker run --rm flightops-ai python -m evals.run_evals

FROM python:3.12-slim

# Don't write .pyc, unbuffered logs (better for container stdout)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Run as a non-root user (security best practice)
RUN useradd --create-home appuser
USER appuser

# Default command runs the demo; override to run evals
CMD ["python", "main.py"]
