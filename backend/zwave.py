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
        for i in range(0, 10):
            producer.send(topic, key="", value=str.encode("test"+str(i)))

class consumerThread (threading.Thread):
    def __init__(self, consumer, producer, topic):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.producer = producer
        self.topic = topic
        self.backend = Backend_with_dimmers_and_sensors()

    def produce(self, message):
        try:
            producer.send(topic, str.encode(message))
        except:
            print('error with producer')

    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key.decode("utf-8") == "network_info":
                self.produce(self.backend.network_info())
            elif message.key.decode("utf-8") == "network_set_sensor_nodes_basic_configuration":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['Group_Interval', 'Group_Reports', 'Wake-up_Interval']):
                    Grp_interval = int(content['Group_Interval'])
                    Grp_reports = int(content['Group_Reports'])
                    Wakeup_interval = int(content['Wake-up_Interval'])
                    self.produce(
                        self.backend.set_basic_sensor_nodes_configuration(Grp_interval, Grp_reports, Wakeup_interval))
                else:
                    print('wrong input')
            elif message.key.decode("utf-8") == "network_get_nodes_configuration":
                self.produce(self.backend.get_nodes_Configuration())
            elif message.key.decode("utf-8") == "network_start":
                self.backend.start()
            elif message.key.decode("utf-8") == "network_stop":
                self.backend.stop()
            elif message.key.decode("utf-8") == "network_reset":
                self.backend.reset()
            elif message.key.decode("utf-8") == "nodes_get_nodes_list":
                self.produce(self.backend.get_nodes_list())
            elif message.key.decode("utf-8") == "nodes_add_node":
                self.produce(self.backend.addNode())  # passes controller to inclusion mode
            elif message.key.decode("utf-8") == "nodes_remove_node":
                self.produce(self.backend.removeNode())  # passes controller to exclusion mode
            elif message.key.decode("utf-8") == "nodes_set_parameter":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    param = int(content['parameter_index'])
                    value = int(content['value'])
                    size = int(content['size'])
                    self.produce(self.backend.set_node_config_parameter(node, param, value, size))
                else:
                    print('wrong input')
            elif message.key.decode("utf-8") == "nodes_get_parameter":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    param = int(content['parameter_index'])
                    # gets a config parameter of a sensor node
                    self.produce(self.backend.get_node_config_parameter(node, param))
            elif message.key.decode("utf-8") == "nodes_get_battery":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    self.produce(self.backend.get_battery(node))
            elif message.key.decode("utf-8") == "nodes_set_location":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'value']):
                    node = int(content['node_id'])
                    value = content['value']
                    self.produce(self.backend.set_node_location(node, value))
                else:
                    print('wrong input')
            elif message.key.decode("utf-8") == "nodes_set_name":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'value']):
                    node = int(content['node_id'])
                    value = content['value']
                    self.produce(self.backend.set_node_name(node, value))
                else:
                    print('wrong input')
            elif message.key.decode("utf-8") == "nodes_get_location":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    self.produce(self.backend.get_node_location(node))
            elif message.key.decode("utf-8") == "nodes_get_name":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    self.produce(self.backend.get_node_name(node))
            elif message.key.decode("utf-8") == "nodes_get_neighbours":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node = int(content['node_id'])
                    self.produce(self.backend.get_neighbours_list(node))
            elif message.key.decode("utf-8") == "sensors_get_sensors_list":
                self.produce(self.backend.get_sensors_list())
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
            elif message.key.decode("utf-8") == "dimmers_get_dimmers_list":
                self.produce(self.backend.get_dimmers())
            elif message.key.decode("utf-8") == "dimmers_get_level":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
                    node_id = int(content['node_id'])
                    self.produce(self.backend.get_dimmer_level(node_id))
            elif message.key.decode("utf-8") == "dimmers_set_level":
                content = json.loads(message.value)
                if all(item in content.keys() for item in ['node_id', 'value']):
                    node = int(content['node_id'])
                    value = int(content['value'])
                    if 99 < value:
                        value = 99
                    elif value < 0:
                        value = 0
                    self.backend.set_dimmer_level(node, value)
                    self.produce("dimmer %s is set to level %s" % (node, value))
                else:
                    print('wrong input')

if __name__ == "__main__":
    topic = "zwave"
    servers = 'iot.liatti.ch:29092'
    producer = KafkaProducer(bootstrap_servers='iot.liatti.ch:29092')
    consumer = KafkaConsumer(topic, bootstrap_servers='iot.liatti.ch:29092')
    time.sleep(5)
    p = producerThread(producer, topic)
    c = consumerThread(consumer, producer, topic)
    c.start()
    time.sleep(2)
    p.start()
    time.sleep(2)
