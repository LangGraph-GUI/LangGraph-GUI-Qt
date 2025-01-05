#!/bin/bash

# Start cron in the background
service cron start

# Add a cron job to restart uvicorn every day at 00:00:00
echo "0 0 * * * root pkill -f uvicorn && cd /app/src && uvicorn server:app --host 0.0.0.0 --port 5000 --workers 6 >> /var/log/uvicorn-restart.log 2>&1" > /etc/cron.d/uvicorn-restart

# Make sure the cron job file has proper permissions
chmod 0644 /etc/cron.d/uvicorn-restart

# Start the Uvicorn server
exec uvicorn server:app --host 0.0.0.0 --port 5000 --workers 6
