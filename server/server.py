#!/usr/bin/env python3

import sys
import time
import os

import threading
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer

file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)

from flask import Flask, render_template, jsonify, Response, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'iot'
app.config['MYSQL_DB'] = 'iot'
app.config['MYSQL_HOST'] = 'db'
mysql = MySQL(app)
# mysql.init_app(app)

servers = ['iot.liatti.ch:29092']
KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"
producer = KafkaProducer(bootstrap_servers=servers)
consumer = KafkaConsumer(bootstrap_servers=servers)
consumer.subscribe([KNX_TOPIC, OPENZWAVE_TOPIC])

def manage_blinds(minor, kind, key, percentage=-1):
    query = ("SELECT number, floor "
        "FROM Room JOIN Beacon ON Beacon.room_number = Room.number "
        "JOIN Knx_device ON Room.number = Knx_device.room_number "
        "WHERE minor = {} AND type = \"{}\";".format(minor, kind))
    
    print(query)
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    room, floor = cursor.fetchone()
    cursor.close()

    if percentage != -1:
        kafka_message = '{ "room": ' + str(room) + ', "floor": ' + str(floor) + ', "percentage": ' + str(percentage) + ' }'
    else:
        kafka_message = '{ "room": ' + str(room) + ', "floor": ' + str(floor) + ' }'

    print(kafka_message)
    producer.send(KNX_TOPIC, key=str.encode(key), value=str.encode(kafka_message))

########################## KNX ROUTES ########################################################################

@app.route('/open_blinds', strict_slashes=False)
def open_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            manage_blinds(content.get('minor'), 'blind', 'open_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/close_blinds', strict_slashes=False)
def close_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            manage_blinds(content.get('minor'), 'blind', 'close_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/percentage_blinds', strict_slashes=False)
def percentage_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            manage_blinds(content.get('minor'), 'blind', 'percentage_blinds', percentage)
            return { "success": True }
    return { "success": False }

@app.route('/percentage_radiator', strict_slashes=False)
def percentage_radiator():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            manage_blinds(content.get('minor'), 'radiator', 'percentage_radiator', percentage)
            return { "success": True }
    return { "success": False }

@app.route('/read_percentage_blinds', strict_slashes=False)
def read_percentage_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # SELECT id, type, knx_device_room_number, number, floor, value, timestamp FROM Room JOIN Beacon ON Beacon.room_number = Room.number JOIN Knx_device ON Room.number = Knx_device.room_number JOIN Knx_log ON Room.number = Knx_log.knx_device_room_number WHERE minor = 12302 AND type = "blind" ORDER BY timestamp DESC LIMIT 1;
            query = ("SELECT number, floor, value, timestamp "
                "FROM Room JOIN Beacon ON Beacon.room_number = Room.number "
                "JOIN Knx_device ON Room.number = Knx_device.room_number "
                "JOIN Knx_log ON Room.number = Knx_log.knx_device_room_number "
                "WHERE minor = {} AND type = \"blind\" LIMIT(1);".format(content.get('minor')))
            return devicesInfos.get('DEVICEID')
    return { "success": False }

########################## END KNX ROUTES ########################################################################

########################## OPENZWAVE ROUTES ######################################################################
@app.route('/sensor_get_temperature', strict_slashes=False)
def sensor_get_temperature():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # TROUVER DANS DB NODE_ID
            # TROUVER DERNIERE MESURE DANS DB
            return { "success": True }
    return { "success": False }

@app.route('/sensor_get_humidity', strict_slashes=False)
def sensor_get_humidity():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # TROUVER DANS DB NODE_ID
            # TROUVER DERNIERE MESURE DANS DB
            return { "success": True }
    return { "success": False }

@app.route('/sensor_get_luminance', strict_slashes=False)
def sensor_get_luminance():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # TROUVER DANS DB NODE_ID
            # TROUVER DERNIERE MESURE DANS DB
            return { "success": True }
    return { "success": False }

@app.route('/sensor_get_motion', strict_slashes=False)
def sensor_get_motion():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # TROUVER DANS DB NODE_ID
            # TROUVER DERNIERE MESURE DANS DB
            return { "success": True }
    return { "success": False }

@app.route('/dimmer_get_level', strict_slashes=False)
def dimmer_get_level():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # TROUVER DANS DB NODE_ID
            # TROUVER DERNIERE MESURE DANS DB
            return { "success": True }
    return { "success": False }

@app.route('/percentage_dimmers', strict_slashes=False)
def percentage_dimmers():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['node_id', 'percentage']):
            node_id = content.get('node_id')
            percentage = content.get('percentage')
            producer.send(OPENZWAVE_TOPIC, key=b'dimmers_set_level', value=str.encode('{"node_id":' + node_id + ', "percentage": ' + percentage + '}'))
            return { "success": True }
    return { "success": False }


########################## END OPENZWAVE ROUTES ##################################################################


########################## CONSUMER THREAD #######################################################################

class consumerThread (threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def decode_knx_infos(self, value):
        content = json.loads(value)
        if all(item in content.keys() for item in ['room', 'floor', 'percentage']):
            bloc = content['room']
            floor = content['floor']
            percentage = content['percentage']
            return bloc, floor, percentage
        else:
            print("Not a correct format")
            return None, None, None

    def run(self):
        for message in self.consumer:
            # Consume les messages produits par KNX et OPENZWAVE et les insert
            # dans les tables de logs de la DB
            content = json.loads(message.value.decode("utf-8"))

            if message.topic == KNX_TOPIC:
                bloc, floor, percentage = self.decode_knx_infos(content)
    
                query = ("INSERT INTO Knx_log "
                    "(timestamp, value, knx_device_type, knx_device_room_number) "
                    "VALUES (NOW(), {}, {}, {});".format(percentage, "blind", bloc))

                cursor = mysql.connection.cursor()
                cursor.execute(query)
                mysql.connection.commit()
                cursor.close()
            elif message.topic == OPENZWAVE_TOPIC:
                pass
            else:
                pass



from logging import FileHandler, Formatter, DEBUG

if __name__ == '__main__':
    try:
        #backend.start()
        file_handler = FileHandler("flask.log")
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)

        app.run(host='::', debug=False, use_reloader=False)

        # Start threads for consume data produces by devices
        consumerThread = consumerThread(consumer)
        consumerThread.start()

    except KeyboardInterrupt:
        exit(0)
