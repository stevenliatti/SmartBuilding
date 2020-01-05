#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
import json

KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"

class consumerThread (threading.Thread):
    def __init__(self, consumer, producer):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.producer = producer

    def produce(self, topic, key, value):
        self.producer.send(topic, key=str.encode(key),
                           value=str.encode(value))

    def intelligence(self, temperature, humidity, luminance, motion):
        pass

    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            content = message.value.decode("utf-8")
            if all(item in content.keys() for item in ['value']):
                value = content['value']

            if message.key.decode("utf-8") == "sensors_get_temperature":
                temperature = value

            elif message.key.decode("utf-8") == "sensors_get_humidity":
                humidity = value

            elif message.key.decode("utf-8") == "sensors_get_luminance":
                luminance = value

            elif message.key.decode("utf-8") == "sensors_get_motion":
                motion = value

            self.intelligence(temperature, humidity, luminance, motion)



if __name__ == "__main__":
    topic = "knx"
    servers = ['iot.liatti.ch:29092']
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(bootstrap_servers=servers)
    consumer.subscribe([KNX_TOPIC, OPENZWAVE_TOPIC])
    time.sleep(5)
    c = consumerThread(consumer, producer)
    p.start()
    c.start()
    p.join()
    c.join()
    print("join threads")