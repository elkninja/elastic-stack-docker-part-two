#!/usr/bin/env bash

# use path of this example as working directory; enables starting this script from anywhere
cd "$(dirname "$0")"

if [ "$1" = "poc" ]; then
    echo "Starting Uvicorn server in poc mode..."
    # we also use a single worker in poc mode so socket.io connections are always handled by the same worker
    uvicorn main:app --workers 1 --log-level info --port 8000 --host 0.0.0.0
elif [ "$1" = "dev" ]; then
    echo "Starting Uvicorn server in development mode..."
    # reload implies workers = 1
    uvicorn main:app --reload --log-level debug --port 8000 --host 0.0.0.0
else
    echo "Invalid parameter. Use 'poc' or 'dev'."
    exit 1
fi
