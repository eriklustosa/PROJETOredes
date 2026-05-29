# Usando a imagem base do Ubuntu exigida
FROM ubuntu:latest

# Evita interações travando a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instalando Python e as ferramentas de rede (iproute2 contém o 'tc')
RUN apt-get update && apt-get install -y \
    python3 \
    iproute2 \
    tcpdump \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app