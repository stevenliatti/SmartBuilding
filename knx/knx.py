#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
import json

import knx_lib

XBLINDS = 1
XBLINDSPERCENT = 3
XBLINDSREAD = 4
XRADIATOR = 0
FLOOR = 4
BLOC = 1

knx = knx_lib.knx()

class producerThread (threading.Thread):
    KEY_READ_PERCENTAGE_BLINDS = 'read_percentage_blinds'
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def produce(self, percentage_blinds):
        self.producer.send(self.topic, key=str.encode(self.KEY_READ_PERCENTAGE_BLINDS),
                           value=str.encode(percentage_blinds))  # Produce the message contain the status of blinds

    def run(self):
        while True:
            group_address = str(XBLINDSREAD) + "/" + str(FLOOR) + "/" + str(BLOC)  # Read the state of blinds
            res = knx.send_datas(group_address, 0, 2, 0, True)
            percentage_blinds = str(int(res.data / 255 * 100))
            self.produce(percentage_blinds)
            time.sleep(5)

class consumerThread (threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def decode_knx_infos(self, value):
        content = json.loads(value)
        if all(item in content.keys() for item in ['room', 'floor']):
            bloc = content['room']
            floor = content['floor']
            if all(item in content.keys() for item in ['percentage']):
                percent = int(content['percentage'] * 255 / 100)
                return bloc, floor, percent
            else:
                return bloc, floor, None
        else:
            print("Not a correct format")
            return None, None, None


    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key.decode("utf-8") == "open_blinds":
                bloc, floor, percent = self.decode_knx_infos(message.value.decode("utf-8"))
                if bloc and floor:
                    group_address = str(XBLINDS)+"/" + floor + "/" + bloc
                    knx.send_datas(group_address, 0, 1, 2)

            elif message.key.decode("utf-8") == "close_blinds":
                bloc, floor, percent = self.decode_knx_infos(message.value.decode("utf-8"))
                if bloc and floor:
                    group_address = str(XBLINDS) + "/" + floor + "/" + bloc
                    knx.send_datas(group_address, 1, 1, 2)

            elif message.key.decode("utf-8") == "percentage_blinds":
                bloc, floor, percent = self.decode_knx_infos(message.value.decode("utf-8"))
                if bloc and floor and percent:
                    group_address = str(XBLINDSPERCENT) + "/" + floor + "/" + bloc
                    knx.send_datas(group_address, percent, 2, 2)
                else:
                    print("Error key")

            elif message.key.decode("utf-8") == "percentage_radiator":
                bloc, floor, percent = self.decode_knx_infos(message.value.decode("utf-8"))
                if bloc and floor and percent:
                    group_address = str(XRADIATOR) + "/" + floor + "/" + bloc
                    knx.send_datas(group_address, percent, 2, 2)
                else:
                    print("Error key")



if __name__ == "__main__":
    topic = "knx"
    servers = ['iot.liatti.ch:29092']
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(topic, bootstrap_servers=servers)
    p = producerThread(producer, topic)
    c = consumerThread(consumer)
    p.start()
    c.start()
    p.join()
    c.join()
    print("join threads")
    knx.disconnect()