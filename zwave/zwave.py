#! /usr/bin/env python
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import time
from init_devices import init_devices

from zwave_lib import Backend_with_dimmers_and_sensors

backend = Backend_with_dimmers_and_sensors()

class producerThread (threading.Thread):
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        init = init_devices()
        self.DEVICES = init.map_devices()
        self.producer = producer
        self.topic = topic

    def produce(self, key, data):
        producer.send(topic, key=str.encode(key), value=str.encode(json.dumps(data)))

    def run(self):
        while True:
            for key in self.DEVICES:
                if 'node_id' in self.DEVICES[key].keys():
                    node_id = int(self.DEVICES[key]['node_id'])

                    if self.DEVICES[key]['name'] == 'Multisensor 6':
                        # sensors_get_temperature
                        res = backend.get_temperature(node_id)
                        self.produce("sensors_get_temperature", res)
                        time.sleep(1)

                        # sensors_get_humidity
                        res = backend.get_humidity(node_id)
                        self.produce("sensors_get_humidity", res)

                        time.sleep(1)

                        # sensors_get_luminance
                        res = backend.get_luminance(node_id)
                        self.produce("sensors_get_luminance", res)
                        time.sleep(1)

                        # sensors_get_motion
                        res = backend.get_motion(node_id)
                        self.produce("sensors_get_motion", res)
                        time.sleep(1)
                    elif self.DEVICES[key]['name'] == 'ZE27':
                        # dimmers_get_level
                        res = backend.get_dimmer_level(node_id)
                        self.produce("dimmers_get_level", res)
                        time.sleep(1)
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
