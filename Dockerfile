# Base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install pymongo

# Expose necessary ports
EXPOSE 3000 5000

# Start application
CMD ["python", "task.py"]
