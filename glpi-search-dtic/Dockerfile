FROM node:20-slim

WORKDIR /app

# Copy package.json and lockfile
COPY glpi-search-dtic/package.json glpi-search-dtic/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY glpi-search-dtic ./

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
