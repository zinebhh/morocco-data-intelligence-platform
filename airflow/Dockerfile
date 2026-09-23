FROM apache/airflow:2.10.0-python3.10

USER root

RUN apt-get update && apt-get install -y \
    default-jre-headless \
    gcc \
    g++ \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$PATH:$JAVA_HOME/bin

USER airflow

# 1. Installer PyTorch CPU-only
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu

# 2. Installer le reste EN UTILISANT LES CONTRAINTES
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    pandas \
    numpy \
    requests \
    minio \
    psycopg2-binary \
    beautifulsoup4 \
    lxml \
    elasticsearch \
    pyspark==3.5.0 \
    scikit-learn \
    matplotlib \
    seaborn \
    joblib \
    xgboost \
    nltk \
    spacy \
    gensim \
    sentence-transformers==2.2.2 \
    transformers==4.35.0