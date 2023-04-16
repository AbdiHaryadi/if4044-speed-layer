FROM rappdw/docker-java-python:openjdk1.8.0_171-python3.6.6

RUN apt-get update && apt-get install

RUN apt-get install -y \
  libpq5 \
  libpq-dev \
  gcc \
  && apt-get clean

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install pyspark==2.4.7
RUN /opt/venv/bin/pip install psycopg2

RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-8-assembly_2.11/2.4.7/spark-streaming-kafka-0-8-assembly_2.11-2.4.7.jar --output spark-streaming-kafka-0-8-assembly_2.11-2.4.7.jar

ADD main.py .
CMD ["/opt/venv/bin/python", "./main.py"]
