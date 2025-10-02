# Use official Python image
FROM python:3.12

# Install Java + curl + build tools + dependencies for requests
RUN apt-get update && \
    apt-get install -y default-jdk-headless curl build-essential libffi-dev libssl-dev python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy panel + scripts + folders into container
COPY panel.py .
COPY server.sh .
COPY bungee.sh .
COPY server/ ./server/
COPY bungee/ ./bungee/

# Install Python dependencies (Flask + requests)
RUN pip install --no-cache-dir flask requests

# Make sure scripts are executable
RUN chmod +x server.sh bungee.sh

# Expose port
EXPOSE 8080


# Run the panel
CMD ["python", "panel.py"]
