# Start with a standard Python base image
FROM python:3.12-slim

ENV NUMBA_CACHE_DIR=/tmp
# Install git (required for pip install from git repositories)
# This is needed for both local development and HF Spaces
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory inside the container
WORKDIR /code

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The command to run your app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:server"]