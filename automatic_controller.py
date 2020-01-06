#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from time import gmtime, strftime
import json

KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"

ROOMS = {
    "1": {"tempertature": 5, "humidity": 10},
    "2": {"tempertature": 5, "humidity": 10},
    "3": {"tempertature": 5, "humidity": 10},
    "4": {"tempertature": 5, "humidity": 10}
}

class consumerThread (threading.Thread):
    def __init__(self, consumer, producer):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.producer = producer

    def produce(self, topic, key, value):
        self.producer.send(topic, key=str.encode(key),
                           value=str.encode(value))

    def intelligence(self, device_id):
        ###TODO: A PARTIR DU DEVICE ID => RETROUVER DANS MAP NODEID ET KINND BLOC FLOR EN FONCTION DU KIND(KNX OU Z)
        bloc = ''
        floor = ''
        dimmersNodeId = ''

        map = {"bloc": bloc, "floor": floor, 'node_id': dimmersNodeId}
        ##### Temperature management #########
        if self.motion == False:
            map['percentage'] = 10
            self.produce(KNX_TOPIC, 'percentage_radiator', json.dumps(map))
        else:
            map['percentage'] = 90
            self.produce(KNX_TOPIC, 'percentage_radiator', json.dumps(map))

        ##### Humidity management #########
        if self.humidity >= 50:
            self.produce(KNX_TOPIC, 'close_blinds', json.dumps(map))

        ##### Luminance management #########
        time = int(strftime("%H", gmtime()))
        if time < 19 and self.motion and self.luminance <= 20:
            self.produce(KNX_TOPIC, 'open_blinds', json.dumps(map))

        if (time > 19 or time < 7) and self.motion and self.luminance <= 20:
            map['percentage'] = 90
            self.produce(OPENZWAVE_TOPIC, 'dimmers_set_level', json.dumps(map))


    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            changed = False

            content = message.value.decode("utf-8")
            if message.topic == KNX_TOPIC:
                if all(item in content.keys() for item in ['bloc', 'floor', 'kind', 'percentage']):
                    bloc = content['bloc']
                    floor = content['floor']
                    kind = content['kind']
                    value = content['percentage']
                    #### deviceId =  RETROUVER LE DEVICE ID
            elif message.topic == OPENZWAVE_TOPIC:
                if all(item in content.keys() for item in ['value', 'sensor']):
                    sensor = content['sensor']
                    value = content['value']
                    #### deviceId = RETROUVER DEVICE ID

            if message.key.decode("utf-8") == "sensors_get_temperature":
                if ROOMS[room]['temperature'] != value:
                    ROOMS[room]['temperature'] = value
                    changed = True

            elif message.key.decode("utf-8") == "sensors_get_humidity":
                if ROOMS[room]['humidity'] != value:
                    ROOMS[room]['humidity'] = value
                    changed = True

            elif message.key.decode("utf-8") == "sensors_get_luminance":
                if ROOMS[room]['luminance'] != value:
                    ROOMS[room]['luminance'] = value
                    changed = True

            elif message.key.decode("utf-8") == "sensors_get_motion":
                if ROOMS[room]['motion'] != value:
                    ROOMS[room]['motion'] = value
                    changed = True
            elif message.key.decode("utf-8") == "read_percentage_blinds": ## KNX
                if ROOMS[room]['blinds'] != value:
                    ROOMS[room]['blinds'] = value
                    changed = True

            if changed:
                self.intelligence(deviceId)



if __name__ == "__main__":
    topic = "knx"
    servers = ['iot.liatti.ch:29092']
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(bootstrap_servers=servers)
    consumer.subscribe([KNX_TOPIC, OPENZWAVE_TOPIC])
    time.sleep(5)
    c = consumerThread(consumer, producer)
    c.start()
    c.join()
    print("join threads")