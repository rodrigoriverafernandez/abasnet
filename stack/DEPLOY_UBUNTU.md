# Guía de despliegue (Ubuntu Server)

Servidor actual: `178.104.169.111`.

## 1) Preparar servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg git ufw
```

Instalar Docker y Compose plugin:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
docker compose version
```

Firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2) Preparar proyecto con GitHub

```bash
git clone <TU_REPO_GITHUB_URL> abasnet
cd abasnet/stack
cp .env.example .env
```

Edita `.env` con secretos reales.

## 3) Levantar stack

```bash
docker compose build
docker compose up -d
docker compose ps
```

Logs:

```bash
docker compose logs -f nginx
docker compose logs -f frontend
docker compose logs -f strapi
```

## 4) SSL (cuando tengas dominio)

1. Apunta DNS del dominio al servidor.
2. Añade bloques `server` para 443 en Nginx.
3. Usa Let's Encrypt (certbot o nginx-proxy-manager).

## 5) Estrategia con varios sitios en un solo servidor

Como ahora tienes más páginas en el mismo servidor, usa `server_name` diferente por sitio y puertos internos separados en Docker.
Cuando migres a otro servicio, replica este stack y despliega con el mismo repositorio GitHub.
