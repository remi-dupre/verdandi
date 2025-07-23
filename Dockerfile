FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY pyproject.toml uv.lock .

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "fastapi", "run", "src/verdandi/app.py", "--port", "80"]
