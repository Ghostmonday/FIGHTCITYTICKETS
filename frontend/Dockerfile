FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm install --legacy-peer-deps

# Copy application files
COPY frontend ./

# Build the application for production
RUN npm run build

EXPOSE 3000

# Use production start command
CMD ["npm", "run", "start"]
