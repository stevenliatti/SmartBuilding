#!/usr/bin/env python3

import sys
import time
import os

import json
from kafka import KafkaConsumer
import mysql.connector

class logs:
    def __init__(self, consumer):
        self.consumer = consumer
        self.cnx = mysql.connector.connect(user='user', password='iot', host='db', database='iot')
        self.cursor = self.cnx.cursor()

    def decode_knx_infos(self, content):
        if all(item in content.keys() for item in ['kind', 'bloc', 'floor', 'reason', 'value']):
            kind = content['kind']
            bloc = content['bloc']
            floor = content['floor']
            reason = content['reason']
            value = content['value']
            return kind, bloc, floor, reason, value
        else:
            print("Not a correct format")
            return None, None, None, None, None

    def decode_openzwave_infos(self, content):
        if all(item in content.keys() for item in ['node_id', 'reason', 'value']):
            node_id = content['node_id']
            reason = content['reason']
            value = content['value']
            return node_id, reason, value
        else:
            print("Not a correct format")
            return None, None, None

    def run(self):
        for message in self.consumer:
            # Consume les messages produits par KNX et OPENZWAVE et les insert
            # dans les tables de logs de la DB
            content = json.loads(message.value.decode("utf-8"))
            print(content)

            if message.topic == KNX_TOPIC:
                kind, bloc, floor, reason, value = self.decode_knx_infos(content)
                query = ("SELECT device_id FROM KnxNode WHERE KnxNode.kind = 'blind' \
                        AND bloc = {} and floor = {};".format(bloc, floor))
                self.cursor.execute(query)
                device_id = self.cursor.fetchone()[0]

                query = ("INSERT INTO Log (timestamp, value, reason, device_id) \
                        VALUES (NOW(), {}, \"{}\", {});"
                        .format(value, reason, device_id))
                self.cursor.execute(query)
                self.cnx.commit()
            elif message.topic == OPENZWAVE_TOPIC:
                node_id, reason, value = self.decode_openzwave_infos(content)
                query = ("SELECT device_id FROM ZwaveNode WHERE node_id = {};"
                        .format(node_id))
                self.cursor.execute(query)
                device_id = self.cursor.fetchone()[0]

                query = ("INSERT INTO Log (timestamp, value, reason, device_id) \
                        VALUES (NOW(), {}, \"{}\", {});"
                        .format(value, reason, device_id))
                self.cursor.execute(query)
                self.cnx.commit()
            else:
                pass

        self.cursor.close()
        self.cnx.close()


if __name__ == '__main__':
    consumer = KafkaConsumer(bootstrap_servers=['iot.liatti.ch:29092'])
    KNX_TOPIC = "knx"
    OPENZWAVE_TOPIC = "zwave"
    consumer.subscribe([KNX_TOPIC, OPENZWAVE_TOPIC])

    l = logs(consumer)
    l.run()