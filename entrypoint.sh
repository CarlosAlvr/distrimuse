#!/bin/sh
# Activa el entorno virtual
/zenohvenv/bin/activate
# Ejecuta el script; usamos exec para reemplazar el proceso shell
exec python /distrimuse/acelerometro.py
