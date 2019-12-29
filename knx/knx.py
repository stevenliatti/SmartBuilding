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
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def run(self):
        while True:
            group_address = str(XBLINDSREAD) + "/" + str(FLOOR) + "/" + str(BLOC)  # Read the state of blinds
            res = knx.send_datas(group_address, 0, 2, 0, True)
            self.producer.send(self.topic, key=b'read_percentage_blinds', 
                value=str.encode(str(int(res.data / 255 * 100)))
            ) # Produce the message contain the status of blinds
            time.sleep(5)

class consumerThread (threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))
            if message.key.decode("utf-8") == "open_blinds":
                print("Fewrfewrewrojewr")
                group_address = str(XBLINDS)+"/"+ str(FLOOR)+"/"+ str(BLOC)
                knx.send_datas(group_address, 0, 1, 2)

            elif message.key.decode("utf-8") == "close_blinds":
                group_address = str(XBLINDS) + "/" + str(FLOOR) + "/" + str(BLOC)
                knx.send_datas(group_address, 1, 1, 2)

            elif message.key.decode("utf-8") == "percentage_blinds":
                content = json.loads(message.value.decode("utf-8"))
                if all(item in content.keys() for item in ['percentage']):
                    percent = int(content['percentage'] * 255 / 100)
                    group_address = str(XBLINDSPERCENT) + "/" + str(FLOOR) + "/" + str(BLOC)
                    knx.send_datas(group_address, percent, 2, 2)
                else:
                    print("Error key")

            elif message.key.decode("utf-8") == "percentage_radiator":
                content = json.loads(message.value.decode("utf-8"))
                if all(item in content.keys() for item in ['percentage']):
                    group_address = str(XRADIATOR) + "/" + str(FLOOR) + "/" + str(BLOC)
                    percent = int(content['percentage'] * 255 / 100)
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