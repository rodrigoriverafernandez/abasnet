# Arquitectura base: Next.js + Strapi + PostgreSQL + Nginx

## Estructura

- `frontend/`: app Next.js
- `strapi/`: CMS Strapi
- `nginx/`: reverse proxy
- `docker-compose.yml`: orquestación
- `.env.example`: variables de entorno
- `DEPLOY_UBUNTU.md`: despliegue en Ubuntu

## Inicio rápido

```bash
cd stack
cp .env.example .env
# inicializa frontend y strapi en sus carpetas
# ajusta nginx/conf.d/default.conf si cambias dominio

docker compose up -d --build
```
