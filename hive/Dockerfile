FROM apache/hive:3.1.3

USER root

# Copier les configurations
COPY conf/core-site.xml /opt/hive/conf/
COPY conf/hive-site.xml /opt/hive/conf/

# Copier les JARs
COPY lib/*.jar /opt/hive/lib/

USER hive