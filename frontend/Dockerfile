FROM node:20-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY frontend/. .

RUN mkdir -p data/seo

RUN npm run build --no-eslint

EXPOSE 3000

CMD ["npm", "run", "start", "--", "-p", "${PORT:-3000}"]
