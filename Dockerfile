# Use the official Python image
FROM python:3.10-slim

# Install build dependencies for psycopg2 (and other dependencies that require compilation)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run FastAPI app using Uvicorn
# Since 'main.py' is inside the 'app' folder, we need to update the path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
