FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config git \
    portaudio19-dev libsndfile1-dev \
 && rm -rf /var/lib/apt/lists/*

# Change the working directory to the `app` directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD ./voice_assistant voice_assistant
ADD ./pyproject.toml pyproject.toml
ADD ./uv.lock uv.lock
ADD ./README.md README.md

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 libsndfile1 libasound2 ffmpeg \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 app
WORKDIR /app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

USER app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python", "-m", "voice_assistant.main"]