#!/bin/sh
# Para depurar, imprimamos algunas variables
echo "PATH before activation: $PATH"
echo "Activating virtualenv..."
. /zenohvenv/bin/activate
echo "PATH after activation: $PATH"
echo "Launching acelerometro.py..."
exec python /distrimuse/acelerometro.py
