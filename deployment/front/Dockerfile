FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration production && \
    if [ -d dist/pls-generator/browser ]; then \
      mv dist/pls-generator/browser dist/build; \
    else \
      mv dist/pls-generator dist/build; \
    fi

FROM nginx:1.25-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/build /usr/share/nginx/html

EXPOSE 80
