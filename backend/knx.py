#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
import sys

from backend import knx_lib


class producerThread (threading.Thread):
    def __init__(self, producer, topic):
        threading.Thread.__init__(self)
        self.producer = producer
        self.topic = topic

    def run(self):
        for line in sys.stdin:
            try:
                producer.send(topic, str.encode(line.rstrip()))
            except:
                print('error with producer')
        return

class consumerThread (threading.Thread):
    XBLINDS = 1
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
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))
            if message.key == "open_blinds":
                group_address = str(self.XBLINDS)+"/"+ str(self.FLOOR)+"/"+ str(self.BLOC)
                knx = knx(group_address, "data", 1, 2)
                conn_channel_id = knx.creat_connexion()
                knx.send_datas(conn_channel_id)
                knx.disconnect(conn_channel_id)

            elif message.key == "close_blinds":
                group_address = str(self.XBLINDS) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                knx = knx(group_address, "data", 1, 2)
                conn_channel_id = knx.creat_connexion()
                knx.send_datas(conn_channel_id)
                knx.disconnect(conn_channel_id)
            elif message.key == "pourcentage_blinds":
                content = message.value.get_json()
                if all(item in content.keys() for item in ['percentage']):
                    group_address = str(self.XBLINDS) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                    knx = knx(group_address, int(content['percentage']), 1, 2)
                    conn_channel_id = knx.creat_connexion()
                    knx.send_datas(conn_channel_id)
                    knx.disconnect(conn_channel_id)
                else:
                    print("Error key")
            elif message.key == "read_blinds":
                group_address = str(self.XBLINDS) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                knx = knx(group_address, "data", 1, 2)
                conn_channel_id = knx.creat_connexion()
                res = knx.send_datas(conn_channel_id)
                knx.disconnect(conn_channel_id)
                self.produce(res) # Produce the message contain the status of blinds
            elif message.key == "pourcentage_radiator":
                content = message.value.get_json()
                if all(item in content.keys() for item in ['percentage']):
                    group_address = str(self.XBLINDS) + "/" + str(self.FLOOR) + "/" + str(self.BLOC)
                    knx = knx(group_address, int(content['percentage']), 1, 2)
                    conn_channel_id = knx.creat_connexion()
                    knx.send_datas(conn_channel_id)
                    knx.disconnect(conn_channel_id)
                else:
                    print("Error key")


if __name__ == "__main__":
    topic = "test"
    servers = ['iot.liatti.ch:29092']
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(topic, bootstrap_servers=servers)
    p = producerThread(producer, topic)
    c = consumerThread(consumer)
    p.start()
    c.start()