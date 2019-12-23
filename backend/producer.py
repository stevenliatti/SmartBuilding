#!/usr/bin/env python3

import logging
import time
import sys

from kafka import KafkaProducer

print('Wait for 10 seconds')
time.sleep(10)
print('Listen on stdin ...')

producer = KafkaProducer(bootstrap_servers=['kafka:9092'])

for line in sys.stdin:
    try:
        producer.send('test', str.encode(line.rstrip()))
    except:
        print('error with producer')
