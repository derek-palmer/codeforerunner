# syntax=docker/dockerfile:1.7

FROM python:3.13-slim

ARG BUILD_UID=1000
ARG BUILD_GID=1000
ARG INSTALL_DEV_DEPS=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md LICENSE.md ./
COPY src ./src

RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        uv sync --frozen --dev; \
    else \
        uv sync --frozen; \
    fi

# Create non-root user and HOME directory with appropriate permissions
RUN groupadd -g ${BUILD_GID} forerunner && \
    useradd -u ${BUILD_UID} -g ${BUILD_GID} -s /bin/bash -m forerunner && \
    mkdir -p /tmp/codeforerunner && \
    chmod 1777 /tmp/codeforerunner && \
    chown -R forerunner:forerunner /app

USER forerunner

ENTRYPOINT ["forerunner"]
CMD ["--help"]