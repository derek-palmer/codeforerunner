# syntax=docker/dockerfile:1.7

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md LICENSE.md ./
COPY src ./src

RUN uv sync --frozen --dev

ENTRYPOINT ["forerunner"]
CMD ["--help"]
