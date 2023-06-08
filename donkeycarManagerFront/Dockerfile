# Donkeycar front build
FROM node:18 as build-stage
COPY package*.json ./
RUN npm install       
COPY . .
WORKDIR ./donkeycarManagerFront
RUN  npm install @vue/cli-service --save-dev
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage ./donkeycarManagerFront/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]