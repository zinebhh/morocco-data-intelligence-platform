FROM bitnami/spark:3.5

USER root

# Installer Python et pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les packages Python
RUN pip3 install --no-cache-dir \
    minio==7.2.7 \
    psycopg2-binary==2.9.9 \
    pandas==2.2.2 \
    requests==2.32.3

# Créer le dossier des jobs
RUN mkdir -p /opt/spark/jobs && chmod 777 /opt/spark/jobs

USER 1001
WORKDIR /opt/spark