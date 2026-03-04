# Etapa de construcción
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Etapa de producción (servidor Nginx para archivos estáticos)
FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Configuración personalizada de Nginx si es necesario (para SPA routing)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
