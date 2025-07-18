# Start with a standard Python base image
FROM python:3.12-slim

# Set build argument to control git installation
ARG INSTALL_GIT=false

# Conditionally install git only if needed
RUN if [ "$INSTALL_GIT" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends git && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Set the working directory inside the container
WORKDIR /code

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN --mount=type=ssh \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The command to run your app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:server"]