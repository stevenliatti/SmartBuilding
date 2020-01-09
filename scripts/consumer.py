#!/usr/bin/env python3

import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

from kafka import KafkaConsumer

consumer = KafkaConsumer(bootstrap_servers=[os.getenv('IOT_DOMAIN') + ':' + str(os.getenv('IOT_KAFKA_PORT'))])
consumer.subscribe(['test', 'db', 'knx', 'zwave'])
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print("%s:%d:%d: key=%s value=%s" % 
        (message.topic, message.partition, message.offset, message.key, message.value))
