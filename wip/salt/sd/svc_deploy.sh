#!/bin/sh

PORT=$1

echo "disable frontend ${PORT}-in" | socat unix-connect:/var/run/haproxy/admin.sock stdio

echo "Starting foreground service on port $PORT..."
python -m SimpleHTTPServer ${PORT}

