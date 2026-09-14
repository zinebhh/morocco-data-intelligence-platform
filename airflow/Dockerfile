FROM apache/airflow:2.10.0-python3.10

USER root

# Installer Java
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurer Java
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$PATH:$JAVA_HOME/bin

USER airflow

# Installer Python packages
RUN pip install --no-cache-dir \
    pandas \
    requests \
    minio \
    psycopg2-binary \
    beautifulsoup4 \
    lxml \
    elasticsearch \
    pyspark==3.5.0