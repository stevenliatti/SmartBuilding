#!/usr/bin/env python3

import dotenv
dotenv.load('../.env')

from kafka import KafkaConsumer

consumer = KafkaConsumer(bootstrap_servers=[dotenv.get('IOT_DOMAIN') + ':' + str(dotenv.get('IOT_KAFKA_PORT'))])
consumer.subscribe(['test', 'db', 'knx', 'zwave'])
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print("%s:%d:%d: key=%s value=%s" % 
        (message.topic, message.partition, message.offset, message.key, message.value))
