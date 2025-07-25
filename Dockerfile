FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . .

RUN uv sync --locked

CMD [ \
    "uv", "run", "uvicorn", \
    "--log-config", "src/log-config.json", \
    "--host", "0.0.0.0", \
    "--port", "80", \
    "src.verdandi.app:app" ]
