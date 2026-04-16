FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy lock metadata first to maximize layer cache
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Copy project source
COPY . .

# Ensure runtime env is aligned with source after copy
RUN uv sync --frozen --no-dev

EXPOSE 1235

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1235"]
