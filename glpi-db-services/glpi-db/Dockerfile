FROM postgres:15-alpine

# Instalar dependências de build e runtime para o pgvector (Matching Postgres LLVM 19)
RUN apk add --no-cache git build-base clang19 llvm19 \
    && cd /tmp \
    && git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector \
    && apk del git build-base clang19 llvm19

# O script de inicialização padrão do postgres já cuida do resto
