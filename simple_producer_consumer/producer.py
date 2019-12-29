#!/usr/bin/env python3

import logging
import time
import sys

from kafka import KafkaProducer

print('Listen on stdin ...')

producer = KafkaProducer(bootstrap_servers=['iot.liatti.ch:29092'])

for line in sys.stdin:
    try:
        producer.send('test', str.encode(line.rstrip()))
    except:
        print('error with producer')
