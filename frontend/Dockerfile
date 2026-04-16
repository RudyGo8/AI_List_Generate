FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=http://localhost:1235
ARG VITE_ACCESS_KEY=test_key
ARG VITE_ACCESS_SECRET=test_secret
ARG VITE_AI_SCENE=default

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_ACCESS_KEY=$VITE_ACCESS_KEY
ENV VITE_ACCESS_SECRET=$VITE_ACCESS_SECRET
ENV VITE_AI_SCENE=$VITE_AI_SCENE

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
