#!/usr/bin/env python3
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from time import gmtime, strftime
import json

KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"

DEVICES = {
    "1": {"node_id": 5, "humidity": 10, 'room': 10},
    "2": {"bloc": 5, "floor": 10, 'room': 10},
    "3": {"bloc": 5, "floor": 10, 'room': 2},
    "4": {"bloc": 5, "floor": 10, 'room': 10}
}

class consumerThread (threading.Thread):
    def __init__(self, consumer, producer):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.producer = producer

    def produce(self, topic, key, value):
        self.producer.send(topic, key=str.encode(key),
                           value=str.encode(value))

    def find_devices_in_room(self, device_id):
        device = DEVICES[device_id]
        devices_knx_in_room = []
        dimmers_zwave_in_room = []
        if all(item in device.keys() for item in ['room']):
            room = device['room']
            for key in DEVICES:
                if DEVICES[key]['room'] == room:
                    if all(item in DEVICES[key].keys() for item in ['kind']):
                        devices_knx_in_room.append(DEVICES[key])
                    elif all(item in DEVICES[key].keys() for item in ['name']):
                        if DEVICES[key]['name'] == 'ZE27':
                            dimmers_zwave_in_room.append(DEVICES[key])
        return devices_knx_in_room, dimmers_zwave_in_room

    def intelligence(self, device_id, msgKey, deviceChanged):
        devices_knx_in_room, dimmers_zwave_in_room = self.find_devices_in_room(device_id)

        for device_knx in devices_knx_in_room:
            self.KNX_device_manager(msgKey, deviceChanged, device_knx['bloc'], device_knx['floor'])
        for dimmers_zwave in dimmers_zwave_in_room:
            self.zwave_device_manager(msgKey, deviceChanged, dimmers_zwave['node_id'])

    def KNX_device_manager(self, msgKey, deviceChanged, bloc, floor):
        map = {"bloc": bloc, "floor": floor}

        ##### Temperature management #########
        if msgKey == "sensors_get_motion":
            if not deviceChanged['sensor']:
                map['percentage'] = 10
                self.produce(KNX_TOPIC, 'percentage_radiator', json.dumps(map))
            else:
                map['percentage'] = 90
                self.produce(KNX_TOPIC, 'percentage_radiator', json.dumps(map))

        ##### Humidity management #########
        if msgKey == "sensors_get_humidity":
            if deviceChanged['relative humidity'] >= 50:
                self.produce(KNX_TOPIC, 'close_blinds', json.dumps(map))

        ##### Luminance management #########
        if msgKey == "sensors_get_luminance" or msgKey == "sensors_get_motion":
            time = int(strftime("%H", gmtime()))
            if time < 19 and deviceChanged['sensor'] and deviceChanged['luminance'] <= 20:
                self.produce(KNX_TOPIC, 'open_blinds', json.dumps(map))

    def zwave_device_manager(self, msgKey, deviceChanged, node_id):
        map = {'node_id': node_id}
        if msgKey == "sensors_get_luminance" or msgKey == "sensors_get_motion":
            time = int(strftime("%H", gmtime()))
            if (time > 19 or time < 7) and deviceChanged['sensor'] and deviceChanged['luminance'] <= 20:
                map['percentage'] = 90
                self.produce(OPENZWAVE_TOPIC, 'dimmers_set_level', json.dumps(map))

    def find_device_id(self, kind=None, bloc=None, floor=None, node_id=None):
        for key in DEVICES:
            if node_id:
                if DEVICES[key]['node_id'] == node_id:
                    return key
            else:
                if DEVICES[key]['kind'] == kind and DEVICES[key]['bloc'] == bloc and DEVICES[key]['floor'] == floor:
                    return key


    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key:
                msgKey = message.key.decode("utf-8")
                content = message.value.decode("utf-8")
                if msgKey == "sensors_get_temperature" or msgKey == "sensors_get_humidity" or msgKey == "sensors_get_luminance" or msgKey == "sensors_get_motion" or msgKey == "read_percentage_blinds":  ## KNX
                    if message.topic == KNX_TOPIC:
                        if all(item in content.keys() for item in ['bloc', 'floor', 'kind', 'reason', 'percentage']):
                            bloc = content['bloc']
                            floor = content['floor']
                            kind = content['kind']
                            reason = content['reason']
                            value = content['percentage']
                            device_id = self.find_device_id(kind, bloc, floor)
                    elif message.topic == OPENZWAVE_TOPIC:
                        if all(item in content.keys() for item in ['node_id', 'reason', 'value']):
                            node_id = content['node_id']
                            reason = content['reason']
                            value = content['value']
                            device_id = self.find_device_id(node_id=node_id)

                    if DEVICES[device_id][reason] != value:
                        DEVICES[device_id][reason] = value
                        self.intelligence(device_id, msgKey, DEVICES[device_id])



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