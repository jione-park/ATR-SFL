ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY docker/requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.lock.txt

CMD ["bash"]
