#!/usr/bin/env python3

from kafka import KafkaConsumer

consumer = KafkaConsumer(bootstrap_servers=['iot.liatti.ch:29092'])
consumer.subscribe(['test', 'db', 'knx', 'zwave'])
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print("%s:%d:%d: key=%s value=%s" % 
        (message.topic, message.partition, message.offset, message.key, message.value))
