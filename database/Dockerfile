FROM postgres:9
ENV POSTGRES_PASSWORD=secret
ENV POSTGRES_USER=username
ENV POSTGRES_DB=database
COPY init.sql /docker-entrypoint-initdb.d/init.sql