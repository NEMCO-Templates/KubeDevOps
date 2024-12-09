# Use the official Python image as the base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port that the Django app runs on (8000)
EXPOSE 8000

# Copy Prometheus configuration file
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "studyPlat.wsgi:application"]
