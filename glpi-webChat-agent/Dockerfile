# ==========================================
# Multi-Stage Build: Frontend WebChat
# ==========================================

# Stage 1: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm ci --quiet

# Copiar código fonte
COPY . .

# Build argument para API URL
ARG VITE_API_URL=http://localhost:4000
ENV VITE_API_URL=$VITE_API_URL

# Build da aplicação React
RUN npm run build

# Stage 2: Nginx Server
FROM nginx:alpine AS runner

# Copiar build do frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Nginx roda em foreground
CMD ["nginx", "-g", "daemon off;"]
