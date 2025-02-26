# Use the official Python image as a base
FROM python:3.10-slim

# Set environment variable
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Command to run the application
CMD ["python3", "-m", "src.main", "--path", "/app"]