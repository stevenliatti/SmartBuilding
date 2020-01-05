#! /usr/bin/env python
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import time

from zwave_lib import Backend_with_dimmers_and_sensors

backend = Backend_with_dimmers_and_sensors()

sensors = [
    { "node_id": 2}
]

dimmers = [
    { "node_id": 3}
]


class producerThread (threading.Thread):
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def run(self):
        while True:
            #producer.send(topic, key="sensors_get_sensors_list", value=str.encode(backend.get_sensors_list()))
            #time.sleep(5)
            #producer.send(topic, key="dimmers_get_dimmers_list", value=str.encode(backend.get_dimmers()))
            #time.sleep(5)

            for device in sensors:
                # sensors_get_temperature
                node = int(device['node_id'])
                producer.send(topic, key=b"sensors_get_temperature",
                              value=str.encode(backend.get_temperature(node)))
                time.sleep(1)
                # sensors_get_humidity
                node = int(device['node_id'])
                producer.send(topic, key=b"sensors_get_humidity",
                              value=str.encode(backend.get_humidity(node)))
                time.sleep(1)
                # sensors_get_luminance
                node = int(device['node_id'])
                producer.send(topic, key=b"sensors_get_luminance",
                              value=str.encode(backend.get_luminance(node)))
                time.sleep(1)

                # sensors_get_motion
                node = int(device['node_id'])
                producer.send(topic, key=b"sensors_get_motion",
                              value=str.encode(backend.get_motion(node)))
                time.sleep(1)

            for device in dimmers:
                # dimmers_get_level
                node_id = int(device['node_id'])
                value = backend.get_dimmer_level(node_id)
                producer.send(topic, key=b"dimmers_get_level",
                              value=str.encode(value))
            time.sleep(5)

class consumerThread (threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key:
                # val = '{"node_id": 3, "percentage": 100}'
                # producer.send("zwave", key=b'dimmers_set_level', value=str.encode(val))
                if message.key.decode("utf-8") == "dimmers_set_level":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'percentage']):
                        node = int(content['node_id'])
                        value = int(content['percentage'])
                        if 99 < value:
                            value = 99
                        elif value < 0:
                            value = 0
                        backend.set_dimmer_level(node, value)
                    else:
                        print('wrong input')

if __name__ == "__main__":
    topic = "zwave"
    servers = 'iot.liatti.ch:29092'
    producer = KafkaProducer(bootstrap_servers='iot.liatti.ch:29092')
    consumer = KafkaConsumer(topic, bootstrap_servers='iot.liatti.ch:29092')
    backend.start()
    time.sleep(5)
    p = producerThread(producer, topic)
    c = consumerThread(consumer)
    c.start()
    p.start()
    c.join()
    p.join()
    backend.stop()
