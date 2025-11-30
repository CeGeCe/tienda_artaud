#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Recolectar archivos estáticos (CSS/JS)
# --no-input: No preguntar "¿Estás seguro?"
# --clear: Borra la carpeta de destino y fuerza la copia desde cero
python manage.py collectstatic --no-input --clear

# Aplicar migraciones a la base de datos de la nube
python manage.py migrate