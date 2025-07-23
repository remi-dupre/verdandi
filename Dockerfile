FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . .

RUN uv sync --locked

CMD ["uv", "run", "fastapi", "run", "src/verdandi/app.py", "--port", "80"]
