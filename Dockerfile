FROM python:3.12-slim

# Change the timezone to UTC+8
RUN ln -sf /usr/share/zoneinfo/Asia/Singapore /etc/localtime

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y cron && apt-get clean

# Set working directory
WORKDIR /app

# Copy all files to the /app directory
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose port
# EXPOSE 5000

# Set the working directory for application source code
WORKDIR /app/src

# Ensure the workspace directory exists
RUN mkdir -p /app/src/workspace

# Make scripts executable
RUN chmod +x /app/entrypoint.sh

# Run the server using Uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]
