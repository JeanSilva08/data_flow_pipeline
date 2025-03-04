# Use the official Python image as a base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1  # Prevent Python from writing .pyc files

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*  # Clean up apt cache

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Expose any necessary ports (if your app listens on a port)
# EXPOSE 8000  # Example for a web app

# Command to run the application
CMD ["python3", "-m", "src.main"]