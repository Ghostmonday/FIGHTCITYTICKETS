FROM node:20-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY package.json package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY . .

RUN mkdir -p data/seo

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
