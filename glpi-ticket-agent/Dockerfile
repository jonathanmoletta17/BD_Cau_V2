# Stage 1: Build/Setup Backend (Frontend REMOVED)
FROM node:20-alpine as backend
WORKDIR /app

# Install Backend Dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy Backend Source
COPY . .

# Environment
ENV NODE_ENV=production
ENV PORT=8000



# Expose Port
EXPOSE 8000

# Start Command (Using tsx directly as defined in package.json start script)
CMD ["npm", "start"]
