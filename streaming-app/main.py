import json
from kafka import KafkaProducer
import requests

username = 'a57de080-f7bc-4022-93dc-612d2af58d31'
password = ''
url = 'http://128.199.176.197:7551/streaming'

producer = KafkaProducer(bootstrap_servers=["kafka:9092"],
                         value_serializer=lambda x: x.encode('utf-8'))

print("Start streaming ...")
stop = False
while not stop:
    try:
        response = requests.get(url, auth=(username, password), headers={"Content-Type": "application/json"}, stream=True)
        temporary_text = b""
        for content in response.iter_content(chunk_size=1024):
            if content == b',' and len(temporary_text) > 0:
                try:
                    if temporary_text.startswith(b"["):
                        temporary_text = temporary_text[1:]

                    item = json.loads(temporary_text)
                    
                    social_media_topic = "social_media"
                    payload = json.dumps(item)
                    producer.send(social_media_topic, payload)
                    
                except json.JSONDecodeError:
                    print("\nUnhandled:", temporary_text)
                    
                temporary_text = b""

            else:
                temporary_text += content

    except requests.exceptions.ChunkedEncodingError as error:
        error_text = str(error)
        if "ConnectionResetError" in error_text:
            print("Connection reset. Reconnecting ...")
        elif "InvalidChunkLength" in error_text and "0 bytes read" in error_text:
            print("Ignoring InvalidChunkLength 0 bytes read ...")
        else:
            raise error

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stop.")
        stop = True
