import requests
from time import sleep
import json

username = 'a57de080-f7bc-4022-93dc-612d2af58d31'
password = ''
url = 'http://128.199.176.197:7551/streaming'
response = requests.get(url, auth=(username, password), stream=8192)

for line in response.iter_content(chunk_size=8192):
    if line:
        try:
            item = json.loads(line)
            message = json.dumps(item).encode('utf-8')
            print(item['crawler_target']['specific_resource_type'])
            # print('=====')
        except json.JSONDecodeError:
            # print(line)
            pass