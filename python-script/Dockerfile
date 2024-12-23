# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /root/python-script
COPY . /app

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for the file path
ENV FILE_PATH=/app/app.py

# Command to run the Python script
CMD ["python", "/app/app.py"]
