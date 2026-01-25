FROM node:20-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY frontend/. .

RUN mkdir -p data/seo

RUN npm run build --no-eslint

# Install curl for healthcheck (wget not available in alpine)
RUN apk add --no-cache curl

EXPOSE 3000

ENV PORT=3000

# Healthcheck for frontend
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Run as non-root user for security
USER node

CMD ["npm", "run", "start", "--", "-p", "3000"]