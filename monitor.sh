#! /bin/bash

STATUS_FILE="status.txt"

URL="http://paffenroth-23.dyn.wpi.edu:8006"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $URL)

# initialize if file doesn't exist
if [ ! -f "$STATE_FILE" ]; then
  echo 0 > "$STATE_FILE"
fi

if [ "$STATUS" -eq 200]; then
    echo "Product up and running"
    if [$(cat "$STATUS_FILE") -eq 0]; then
        ./automated_deployment.sh
        echo 1 > "$STATE_FILE"
else
    echo "Product not responding (status: $STATUS)"
    echo 0 > "$STATE_FILE"
fi