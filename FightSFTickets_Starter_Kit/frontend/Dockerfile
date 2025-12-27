FROM node:20-alpine

# Create non-root user for security
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm install --legacy-peer-deps

# Copy application files
COPY frontend ./

# Copy SEO data files (create directory first, copy if exists)
RUN mkdir -p data/seo
COPY data/seo/ ./data/seo/ || echo "SEO data files not found, will be empty"

# Build the application for production
RUN npm run build

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 3000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Use production start command
CMD ["npm", "run", "start"]
