#!/usr/bin/env python3
import threading
from kafka import KafkaConsumer
import json


class init_devices:
    def __init__(self):
        threading.Thread.__init__(self)
        self.consumer = KafkaConsumer(auto_offset_reset='earliest', bootstrap_servers=['iot.liatti.ch:29092'])
        self.consumer.subscribe(['db'])

    def map_devices(self):
        map = {}
        for message in self.consumer:
            content = json.loads(message.value)
            if all(item in content.keys() for item in ['device_id', 'room_number', 'kind', 'bloc', 'floor']):
                map[content['device_id']] = content

            if all(item in content.keys() for item in ['device_id', 'room_number', 'node_id', 'name']):
                map[content['device_id']] = content

            if message.key:
                if message.key.decode("utf-8") == "end_read_db":
                    break
        return map




if __name__ == "__main__":
    test = init_devices()
    l = test.map_devices()
    print(l)