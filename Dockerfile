FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked


FROM python:3.13-alpine

RUN addgroup -g 1000 app && adduser -u 1000 -G app -D app
USER app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

CMD [ \
    "uvicorn", \
    "--log-config", "src/log-config.json", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "src.verdandi.app:app" ]
