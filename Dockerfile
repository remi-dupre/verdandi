FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . .

RUN uv sync --locked

CMD ["uv", "run", "fastapi", "run", "verdandi/main.py", "--port", "80"]
