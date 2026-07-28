# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install uv && uv sync --no-dev

COPY . .

ENV DASHBOARD_BACKEND_HOST=0.0.0.0
ENV DASHBOARD_BACKEND_PORT=8001

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

CMD ["uv", "run", "python", "-m", "app.server"]
