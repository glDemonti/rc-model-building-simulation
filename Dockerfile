# syntax=docker/dockerfile:1

From python:3.12

# Set working directory
WORKDIR /app

# Install dependencies
COPY environment.yml .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

    