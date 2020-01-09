#!/usr/bin/env python3

import logging
import time
import sys

from kafka import KafkaProducer

import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

print('Listen on stdin ...')

producer = KafkaProducer(bootstrap_servers=[os.getenv('IOT_DOMAIN') + ':' + str(os.getenv('IOT_KAFKA_PORT'))])

for line in sys.stdin:
    try:
        producer.send('knx', key=b'open_blinds', value=str.encode(line.rstrip()))
    except:
        print('error with producer')
