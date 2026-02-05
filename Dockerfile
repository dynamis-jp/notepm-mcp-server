FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY notepm_mcp_server ./notepm_mcp_server

# Install dependencies
RUN uv sync --frozen --no-cache

# Run the server
CMD ["uv", "run", "notepm-mcp-server"]
