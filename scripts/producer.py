#!/usr/bin/env python3

import logging
import time
import sys

from kafka import KafkaProducer

import dotenv
dotenv.load('../.env')

print('Listen on stdin ...')

producer = KafkaProducer(bootstrap_servers=[dotenv.get('IOT_DOMAIN') + ':' + str(dotenv.get('IOT_KAFKA_PORT'))])

for line in sys.stdin:
    try:
        producer.send('knx', key=b'open_blinds', value=str.encode(line.rstrip()))
    except:
        print('error with producer')
