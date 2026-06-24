FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

WORKDIR /app

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]