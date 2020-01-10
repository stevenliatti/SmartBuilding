#!/usr/bin/env python3

import logging
import time
import sys
import json

import dotenv
dotenv.load('../.env')

import mysql.connector
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=[dotenv.get('IOT_DOMAIN') + ':' + str(dotenv.get('IOT_KAFKA_PORT'))])

cnx = mysql.connector.connect(user=str(dotenv.get('MYSQL_USER')), password=str(dotenv.get('MYSQL_PASSWORD')), host=str(dotenv.get('MYSQL_HOST')), database=str(dotenv.get('MYSQL_DATABASE')))
cursor = cnx.cursor()

query = "select device_id, room_number, KnxNode.kind, bloc, floor from Device join KnxNode on id = device_id;"
cursor.execute(query)
for (device_id, room_number, kind, bloc, floor) in cursor:
    device = {
        "device_id": device_id,
        "room_number": room_number,
        "kind": kind,
        "bloc": bloc,
        "floor": floor
    }
    producer.send('db', key=str.encode('knx_db'), value=str.encode(json.dumps(device)))
    print(device)
    time.sleep(0.1)

query = "select device_id, room_number, node_id, name from Device join ZwaveNode on id = device_id;"
cursor.execute(query)
for (device_id, room_number, node_id, name) in cursor:
    device = {
        "device_id": device_id,
        "room_number": room_number,
        "node_id": node_id,
        "name": name
    }
    producer.send('db', key=str.encode('zwave_db'), value=str.encode(json.dumps(device)))
    print(device)
    time.sleep(0.1)

producer.send('db', key=str.encode('end_read_db'), value=str.encode('end_read_db'))

cursor.close()
cnx.close()
