#!/bin/sh
echo "Waiting 1 second before activation..."
sleep 1
echo "PATH before activation: $PATH"
echo "Activating virtualenv..."
. /zenohvenv/bin/activate
echo "PATH after activation: $PATH"
echo "Launching acelerometro.py..."
exec python /distrimuse/acelerometro.py
