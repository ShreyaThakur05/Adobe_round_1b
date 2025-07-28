# --- Stage 1: The "Builder" ---
# This stage installs dependencies into a virtual environment to keep the final image clean
FROM --platform=linux/amd64 python:3.12-slim as builder

WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv

# Copy and install requirements into the virtual environment
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt


# --- Stage 2: The "Final" Image ---
# This stage creates the final, lean image for submission
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Copy the clean virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy your application's source code and offline models
COPY src/ src/
COPY models/ models/

# Set the PATH to use the Python from our virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# [cite_start]Define the base command that will always run [cite: 69]
ENTRYPOINT ["python", "-m"]

# Define the default module to run (Round 1B). This can be overridden.
CMD ["src.round1b.main"]