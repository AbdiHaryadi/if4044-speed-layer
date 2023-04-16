import subprocess

subprocess.call(['pip', 'install', 'psycopg2'])

from psycopg2 import connect
from pyspark import SparkContext, SparkConf
conf = (
    SparkConf()
        .set("spark.jars", "spark-streaming-kafka-0-8-assembly_2.11-2.4.7.jar")
)
sc = SparkContext(conf=conf)

import datetime
import json
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

print("Running ...")

properties_db = {
	"database": "database",
	"user": "username",
	"password": "secret",
	"host": "database",
	"port": "5432",
	"table": "socmed_aggs_socmedaggs"
}

KAFKA_TOPIC = "social_media"
BOOTSTRAP_SERVER = "kafka:9092"

stream_period_seconds = 5
ssc = StreamingContext(sc, stream_period_seconds)
ssc.checkpoint("./checkpoint")
lines = KafkaUtils.createDirectStream(ssc, [KAFKA_TOPIC], {
    "metadata.broker.list": BOOTSTRAP_SERVER
})

TIMEZONE = datetime.timezone(datetime.timedelta(hours=7)) # WIB

def parse_data_flat_map(key_value):
    json_string = key_value[1]
    try:
        payload = json.loads(json_string)
        
        social_media = payload.get("crawler_target", {}).get("specific_resource_type", "")
        if social_media != "":
            return [(social_media, payload)]
        else:
            print("---")
            print("Warning: unidentified social media ignored")
            print(json_string)
            print("---")
            return []
    
    except json.JSONDecodeError:
        print("---")
        print("Warning: broken JSON ignored")
        print(json_string)
        print("---")
        return []
    
def facebook_extract_map(payload):
    if "created_time" not in payload:
        return None
    elif "from" not in payload:
        return None
    elif "id" not in payload["from"]:
        return None
    else:
        timestamp_pattern = "%Y-%m-%dT%H:%M:%S%z" # e.g.: 2023-04-04T17:09:23+0000
        return {
            "timestamp": datetime.datetime.strptime(payload["created_time"], timestamp_pattern).astimezone(TIMEZONE).replace(tzinfo=None),
            "user_id": payload["from"]["id"]
        }

def instagram_extract_map(payload):
    if "created_time" not in payload:
        return None
    elif "user" not in payload:
        return None
    elif "id" not in payload["user"]:
        return None
    else:
        return {
            "timestamp": datetime.datetime.fromtimestamp(int(payload["created_time"])).astimezone(TIMEZONE).replace(tzinfo=None),
            "user_id": payload["user"]["id"]
        }

def twitter_extract_map(payload):
    if "created_at" not in payload:
        return None
    elif "user_id" not in payload:
        return None
    else:
        timestamp_pattern = "%a %b %d %H:%M:%S %z %Y" # e.g.: Sat Nov 10 16:09:22 +0000 2012
        return {
            "timestamp": datetime.datetime.strptime(payload["created_at"], timestamp_pattern).astimezone(TIMEZONE).replace(tzinfo=None),
            "user_id": payload["user_id"]
        }
    
def youtube_extract_map(payload):
    if "snippet" not in payload:
        return None
    elif "publishedAt" not in payload["snippet"]:
        return None
    elif "channelId" not in payload["snippet"]:
        return None
    else:
        
        timestamp_pattern = "%Y-%m-%dT%H:%M:%SZ" # e.g.: 2023-04-04T17:09:24Z
        return {
            "timestamp": datetime.datetime.strptime(payload["snippet"]["publishedAt"], timestamp_pattern).astimezone(TIMEZONE).replace(tzinfo=None),
            "user_id": payload["snippet"]["channelId"]
        }
    
def print_malformed_data_warning(social_media, payload):
    print("---")
    print(f"Warning: ignoring malformed data from {social_media}")
    print(payload)
    print("---")
    
def extract_flat_map(key_value):
    social_media, payload = key_value
    if social_media == "facebook":
        extract_result = facebook_extract_map(payload)
        if extract_result is None:
            print_malformed_data_warning(social_media, payload)
            return []
            
        extract_result['social_media'] = social_media
        return [(social_media, extract_result)]
    
    elif social_media == "instagram":
        extract_result = instagram_extract_map(payload)
        if extract_result is None:
            print_malformed_data_warning(social_media, payload)
            return []
            
        extract_result['social_media'] = social_media
        return [(social_media, extract_result)]
    
    elif social_media == "twitter":
        extract_result = twitter_extract_map(payload)
        if extract_result is None:
            print_malformed_data_warning(social_media, payload)
            return []
            
        extract_result['social_media'] = social_media
        return [(social_media, extract_result)]
    
    elif social_media == "youtube":
        extract_result = youtube_extract_map(payload)
        if extract_result is None:
            print_malformed_data_warning(social_media, payload)
            return []

        extract_result['social_media'] = social_media
        return [(social_media, extract_result)]
    
    else:
        print("---")
        print(f"Warning: unhandled social media: {social_media}")
        print(payload)
        print("---")
        return []
    
def binned_timestamp_map(key_value):
    social_media, payload = key_value
    minute = payload["timestamp"].minute
    binned_minute = (minute // 5) * 5
    timestamp = payload["timestamp"].replace(minute=binned_minute, second=0)
    payload["timestamp"] = timestamp
    return (f"{social_media};{timestamp.isoformat()}", payload)

def update_function(new_payload_list, old_payload):
    if len(new_payload_list) == 0:
        return old_payload
    
    mode = "update"
    if old_payload is None:
        mode = "insert"
        payload = {
            "social_media": "",
            "timestamp": None,
            "count": 0,
            "unique_count": 0,
            "user_ids": set(),
            "created_at": datetime.datetime.now().astimezone(TIMEZONE).replace(tzinfo=None),
            "updated_at": datetime.datetime.now().astimezone(TIMEZONE).replace(tzinfo=None)
        }
        
    else:
        payload = old_payload

    for new_payload in new_payload_list:
        payload["social_media"] = new_payload["social_media"]
        payload["timestamp"] = new_payload["timestamp"]
        payload["count"] += 1
        if new_payload["user_id"] not in payload["user_ids"]:
            payload["unique_count"] += 1
            payload["user_ids"].add(new_payload["user_id"])
        
    payload["updated_at"] = datetime.datetime.now().astimezone(TIMEZONE).replace(tzinfo=None)

    insert_row(mode, payload)

    return payload

def insert_row(mode, payload):
    format = "%Y-%m-%d %X"
    social_media = payload['social_media']
    timestamp = payload['timestamp'].strftime(format)
    count = payload['count']
    unique_count = payload['unique_count']
    created_at = payload['created_at'].strftime(format)
    updated_at = payload['updated_at'].strftime(format)
    conn = connect(database = properties_db["database"], user = properties_db["user"], password = properties_db["password"], host = properties_db["host"], port = properties_db["port"])
    cursor = conn.cursor()
    if mode == "insert":
        cursor.execute("INSERT INTO " + properties_db["table"] + " (social_media, timestamp, count, unique_count, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)", (social_media, timestamp, count, unique_count, created_at, updated_at))
    elif mode == "update":
        cursor.execute("UPDATE " + properties_db["table"] + " SET count=%s, unique_count=%s, updated_at=%s WHERE social_media=%s AND timestamp=%s", (count, unique_count, updated_at, social_media, timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def calculate_aggregate(lines, window_length = 2, sliding_interval = 2):
    payloads = lines.flatMap(parse_data_flat_map)
    specific_payloads = payloads.flatMap(extract_flat_map)
    binned_timestamp_payloads = specific_payloads.map(binned_timestamp_map)
    aggregated_payloads = binned_timestamp_payloads.updateStateByKey(update_function)
    return aggregated_payloads

print("Running (2) ...")

# run the function
result = calculate_aggregate(lines, window_length=2, sliding_interval=2)
# Print
result.pprint()
ssc.start()
ssc.awaitTermination()

print("Stop.")
