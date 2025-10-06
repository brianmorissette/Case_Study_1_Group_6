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
else
    echo "Product not responding (status: $STATUS)"
    chmod 700 automated_deployment.sh
    ~/automated_deployment.sh
fi