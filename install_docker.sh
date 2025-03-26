#!/bin/bash
# Script para instalar Docker en sistemas basados en Debian/Raspbian (arm64)
# Ejecuta este script con sudo: sudo ./install_docker.sh

set -e

echo "Actualizando repositorios..."
sudo apt-get update

echo "Instalando paquetes necesarios..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

echo "Obteniendo información del sistema..."
. /etc/os-release

# Si el ID es raspbian, usamos ese valor, sino usamos el valor obtenido
if [ "$ID" = "raspbian" ]; then
    DISTRO="raspbian"
else
    DISTRO=$ID
fi

echo "Configurando repositorio para Docker ($DISTRO) en arquitectura $(dpkg --print-architecture)..."

echo "Agregando la clave GPG oficial de Docker..."
curl -fsSL "https://download.docker.com/linux/${DISTRO}/gpg" | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "Agregando el repositorio de Docker..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/${DISTRO} $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Actualizando repositorios con el nuevo repositorio de Docker..."
sudo apt-get update

echo "Instalando Docker Engine, CLI y containerd..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "Habilitando y arrancando el servicio de Docker..."
sudo systemctl enable docker
sudo systemctl start docker

echo "Docker se instaló correctamente. Versión instalada:"
docker --version
