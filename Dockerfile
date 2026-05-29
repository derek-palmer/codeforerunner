FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build
COPY . .

# Install the wheel into an isolated venv so only it (no build toolchain or
# source tree) is carried into the runtime stage.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir .

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

# /workspace is a mount point: `forerunner` runs against the caller's repo
# (Path.cwd()), bind-mounted here. Source is not baked in.
WORKDIR /workspace

ENTRYPOINT ["forerunner"]
