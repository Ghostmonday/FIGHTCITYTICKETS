FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY frontend ./

RUN mkdir -p data/seo

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
