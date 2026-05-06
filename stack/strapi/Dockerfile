FROM node:22-alpine
WORKDIR /opt/app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 1337
CMD ["npm","run","start"]
