#!/usr/bin/env python3
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
from time import gmtime, strftime
import json
from init_devices import init_devices

import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"


class automatic_controller:
    def __init__(self, consumer, producer):
        init = init_devices()
        self.DEVICES = init.map_devices()
        self.consumer = consumer
        self.producer = producer

    def produce(self, topic, key, value):
        self.producer.send(topic, key=str.encode(key), value=str.encode(value))

    def find_devices_in_room(self, device_id):
        device = self.DEVICES[device_id]
        devices_knx_in_room = []
        dimmers_zwave_in_room = []
        if 'room_number' in device.keys():
            room_number = device['room_number']
            for key in self.DEVICES:
                if self.DEVICES[key]['room_number'] == room_number:
                    if all(item in self.DEVICES[key].keys() for item in ['kind']):
                        devices_knx_in_room.append(self.DEVICES[key])
                    elif all(item in self.DEVICES[key].keys() for item in ['name']):
                        if self.DEVICES[key]['name'] == 'ZE27':
                            dimmers_zwave_in_room.append(self.DEVICES[key])
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
            if ((time > 19 or time < 7) and deviceChanged['sensor']) or deviceChanged['luminance'] <= 20:
                map['percentage'] = 90
                self.produce(OPENZWAVE_TOPIC, 'dimmers_set_level', json.dumps(map))
            else:
                map['percentage'] = 0
                self.produce(OPENZWAVE_TOPIC, 'dimmers_set_level', json.dumps(map))

    def find_device_id(self, kind=None, bloc=None, floor=None, node_id=None):
        for key in self.DEVICES:
            if node_id:
                if all(item in self.DEVICES[key].keys() for item in ['node_id']):
                    if self.DEVICES[key]['node_id'] == node_id:
                        return key
            else:
                if all(item in self.DEVICES[key].keys() for item in ['bloc', 'floor', 'kind']):
                    if self.DEVICES[key]['kind'] == kind and self.DEVICES[key]['bloc'] == bloc and self.DEVICES[key]['floor'] == floor:
                        return key


    def run(self):
        for message in self.consumer:
            print("%s:%d:%d: key=%s value=%s" %
                  (message.topic, message.partition, message.offset, message.key, message.value))

            if message.key:
                msgKey = message.key.decode("utf-8")
                content = json.loads(message.value.decode("utf-8"))
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

                    if 'reason' in self.DEVICES[device_id]:
                        if self.DEVICES[device_id][reason] != value:
                            self.DEVICES[device_id][reason] = value
                            self.intelligence(device_id, msgKey, self.DEVICES[device_id])
                    else:
                        self.DEVICES[device_id][reason] = value
                        self.intelligence(device_id, msgKey, self.DEVICES[device_id])




if __name__ == "__main__":
    print("Wait for DB...")
    time.sleep(30)
    servers = [os.getenv('IOT_DOMAIN') + ':' + str(os.getenv('IOT_KAFKA_PORT'))]
    producer = KafkaProducer(bootstrap_servers=servers)
    consumer = KafkaConsumer(bootstrap_servers=servers)
    consumer.subscribe([KNX_TOPIC, OPENZWAVE_TOPIC])
    time.sleep(5)
    print("Service start")
    ac = automatic_controller(consumer, producer)
    ac.run()