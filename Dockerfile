FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY pyproject.toml uv.lock .

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "fastapi", "run", "verdandi/main.py", "--port", "80"]
