# ==========================================
# Multi-Stage Build: Backend TOD
# ==========================================

# Stage 1: Dependencies
FROM node:20-alpine AS deps

WORKDIR /app

# Copiar apenas package files para cache
COPY package.json package-lock.json ./

# Instalar todas dependências (incluindo tsx para runtime)
RUN npm ci --quiet

# Stage 2: Runner
FROM node:20-alpine AS runner

WORKDIR /app

# Copiar node_modules do stage anterior
COPY --from=deps /app/node_modules ./node_modules

# Copiar package files
COPY package.json package-lock.json ./

# Copiar código fonte
COPY tsconfig.json ./
COPY src ./src

# Variáveis de ambiente
ENV NODE_ENV=production
ENV PORT=4000

# Expor porta
EXPOSE 4000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:4000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Comando de start
CMD ["npm", "start"]
