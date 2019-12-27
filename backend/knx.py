#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
import sys
import json

import knx_lib


class producerThread (threading.Thread):
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def run(self):
        for line in sys.stdin:
            try:
                producer.send(topic, key=b'percentage_blinds', value=str.encode(line.rstrip()))
            except:
                print('error with producer')
        return

class consumerThread (threading.Thread):
    XBLINDS = 1
    XBLINDSPERCENT = 3
    XBLINDSREAD = 4
    XRADIATOR = 0
    FLOOR = 4
    BLOC = 1
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def produce(self, message):
        try:
            producer.send(topic, str.encode(message))
        except:
            print('error with producer')

    def run(self):
        knx = knx_lib.knx()
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))
            if message.key.decode("utf-8") == "open_blinds":
                print("Fewrfewrewrojewr")
                group_address = str(self.XBLINDS)+"/"+ str(self.FLOOR)+"/"+ str(self.BLOC)
                knx.send_datas(group_address, 0, 1, 2)


            elif message.key.decode("utf-8") == "close_blinds":
                group_address = str(self.XBLINDS) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                knx.config(group_address, 1, 1, 2)
            elif message.key.decode("utf-8") == "percentage_blinds":
                content = json.loads(message.value.decode("utf-8"))
                if all(item in content.keys() for item in ['percentage']):
                    percent = int(content['percentage'] * 255 / 100)
                    group_address = str(self.XBLINDSPERCENT) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                    knx.send_datas(group_address, percent, 2, 2)
                else:
                    print("Error key")
            elif message.key.decode("utf-8") == "read_blinds":
                group_address = str(self.XBLINDSREAD) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                knx.send_datas(group_address, 0, 1, 0, True)

                #self.produce(res) # Produce the message contain the status of blinds
            elif message.key.decode("utf-8") == "pourcentage_radiator":
                content = json.loads(message.value.decode("utf-8"))
                if all(item in content.keys() for item in ['percentage']):
                    group_address = str(self.XRADIATOR) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                    percent = int(content['percentage'] * 255 / 100)
                    knx.send_datas(group_address, percent, 2, 2)
                else:
                    print("Error key")
        knx.disconnect()



if __name__ == "__main__":
    topic = "test"
    servers = ['iot.liatti.ch:29092']
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(topic, bootstrap_servers=servers)
    p = producerThread(producer, topic)
    c = consumerThread(consumer)
    p.start()
    c.start()