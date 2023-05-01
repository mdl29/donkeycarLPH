# Donkeycar front build
FROM node:lts-alpine as build-stage
COPY package*.json ./
RUN npm install --legacy-peer-deps         
COPY . .
RUN npm run build

# étape de production
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]