#! /usr/bin/env python
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import time

from zwave_lib import Backend_with_dimmers_and_sensors


class producerThread (threading.Thread):
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def run(self):
        while True:
            producer.send(topic, key="network_info", value=str.encode(self.backend.network_info()))
            time.sleep(5)
            producer.send(topic, key="nodes_get_nodes_list", value=str.encode(self.backend.get_nodes_list()))
            time.sleep(5)
            producer.send(topic, key="sensors_get_sensors_list", value=str.encode(self.backend.get_sensors_list()))
            time.sleep(5)
            producer.send(topic, key="dimmers_get_dimmers_list", value=str.encode(self.backend.get_dimmers()))
            time.sleep(5)

class consumerThread (threading.Thread):
    def __init__(self, consumer, producer, topic):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.producer = producer
        self.topic = topic
        self.backend = Backend_with_dimmers_and_sensors()
        self.backend.start()

    def produce(self, message):
        try:
            self.producer.send(self.topic, str.encode(message))
        except:
            print('error with producer')

    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key:
                if message.key.decode("utf-8") == "nodes_get_battery":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_battery(node))
                elif message.key.decode("utf-8") == "nodes_get_location":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_node_location(node))
                elif message.key.decode("utf-8") == "nodes_get_name":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_node_name(node))
                elif message.key.decode("utf-8") == "sensors_get_all_measures":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_all_Measures(node))
                elif message.key.decode("utf-8") == "sensors_get_temperature":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_temperature(node))
                elif message.key.decode("utf-8") == "sensors_get_humidity":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_humidity(node))
                elif message.key.decode("utf-8") == "sensors_get_luminance":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_luminance(node))
                elif message.key.decode("utf-8") == "sensors_get_motion":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                        node = int(content['node_id'])
                        self.produce(self.backend.get_motion(node))
                elif message.key.decode("utf-8") == "dimmers_get_level":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id']):
                        node_id = int(content['node_id'])
                        self.produce(self.backend.get_dimmer_level(node_id))
                elif message.key.decode("utf-8") == "dimmers_set_level":
                    content = json.loads(message.value)
                    if all(item in content.keys() for item in ['node_id', 'percentage']):
                        node = int(content['node_id'])
                        value = int(content['percentage'])
                        if 99 < value:
                            value = 99
                        elif value < 0:
                            value = 0
                        self.backend.set_dimmer_level(node, value)
                        self.produce("dimmer %s is set to level %s" % (node, value))
                    else:
                        print('wrong input')
        self.backend.stop()

if __name__ == "__main__":
    topic = "zwave"
    servers = 'iot.liatti.ch:29092'
    producer = KafkaProducer(bootstrap_servers='iot.liatti.ch:29092')
    consumer = KafkaConsumer(topic, bootstrap_servers='iot.liatti.ch:29092')
    time.sleep(5)
    p = producerThread(producer, topic)
    c = consumerThread(consumer, producer, topic)
    c.start()
    p.start()
    time.sleep(2)
