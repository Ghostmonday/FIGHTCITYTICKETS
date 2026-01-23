FROM node:20-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY frontend/. .

RUN mkdir -p data/seo

# Skip build for local development/testing
# RUN npm run build

EXPOSE 3000

ENV PORT=3000
CMD ["npx", "next", "dev", "-p", "3000"]
