#!/usr/bin/env python3
from kafka import KafkaConsumer
import json

class init_devices:
    def __init__(self):
        self.consumer = KafkaConsumer(auto_offset_reset='earliest', bootstrap_servers=['iot.liatti.ch:29092'])
        self.consumer.subscribe(['db'])

    def map_devices(self):
        map = {}
        for message in self.consumer:
            if message.key:
                if message.key.decode("utf-8") == "end_read_db":
                    break
                else:
                    content = json.loads(message.value.decode("utf-8"))
                    if all(item in content.keys() for item in ['device_id', 'room_number', 'kind', 'bloc', 'floor']):
                        map[content['device_id']] = content

                    if all(item in content.keys() for item in ['device_id', 'room_number', 'node_id', 'name']):
                        map[content['device_id']] = content

                    if 'device_id' in content.keys():
                        map[content['device_id']]['sensor'] = 0
                        map[content['device_id']]['relative humidity'] = 0
                        map[content['device_id']]['luminance'] = 0
                        map[content['device_id']]['temperature'] = 0

        return map
