# if4044-speed-layer

How to run:
1. Run `docker compose build` at project root.
2. Run `docker compose up kafka`.
3. Wait until Zookeeper starts running.
4. Run `docker exec -d kafka /opt/kafka_2.11-0.8.2.1/bin/kafka-topics.sh --create --zookeeper kafka:2181 --replication-factor 1 --partitions 1 --topic social_media` to create `social_media` topic.
5. Run `docker compose up database`.
6. Check database in `database` container by running `psql postgres://username:secret@localhost:5432/database` in it
7. Run `docker compose up spark-streaming`.
8. Run `docker compose up streaming-app`.
9. Run `docker compose up speed_layer_api`.
