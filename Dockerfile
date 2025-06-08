FROM python:3.12-slim

WORKDIR /app

# Copy only the dependency configuration files first to leverage Docker's build cache
COPY pyproject.toml* ./

# Install the uv tool (which provides uv sync)
RUN pip install --no-cache-dir uv

# Synchronize dependencies as defined in pyproject.toml
RUN uv sync

# Now copy the rest of the application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Run the FastAPI application with uv's integrated uvicorn runner
CMD ["uv", "run", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]