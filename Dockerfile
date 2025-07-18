# Start with a standard Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# The command to run your app
# It tells Gunicorn to listen on port 7860 (the HF default)
# and serve the 'server' object from your 'app.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:server"]