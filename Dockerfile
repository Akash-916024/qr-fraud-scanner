# Use a lightweight Python image
FROM python:3.9-slim

# Install required system packages for pyzbar
RUN apt-get update && apt-get install -y libzbar0 gcc ca-certificates

# Set the working directory
WORKDIR /app

# Copy all project files to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask/Gunicorn will run on
EXPOSE 10000

# Start your Flask app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "fixed_app:app"]
