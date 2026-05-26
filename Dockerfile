FROM dhi.io/python:3.13

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY . /workspace

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -e .

ENTRYPOINT ["forerunner"]
