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
consumerKNX = KafkaConsumer(KNX_TOPIC, bootstrap_servers=servers)
consumerZWAVE = KafkaConsumer(OPENZWAVE_TOPIC, bootstrap_servers=servers)

devicesInfos = {}

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
            # DEVICEID = TROUVE EN FAISANT QUERY SQL
            return devicesInfos.get('DEVICEID')
    return { "success": False }

########################## END KNX ROUTES ########################################################################

########################## OPENZWAVE ROUTES ######################################################################
@app.route('/percentage_dimmers', strict_slashes=False)
def percentage_dimmers():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            producer.send(OPENZWAVE_TOPIC, key=b'dimmers_set_level', value=str.encode('{"percentage":' + percentage + '}'))
            return { "success": True }
    return { "success": False }

@app.route('/get_network_info', strict_slashes=False)
def get_network_info():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # KEYFORNODEKEYFORNETWORKINFOSLISTE = TROUVE EN FAISANT QUERY SQL
            return devicesInfos.get('KEYFORNETWORKINFOS')
    return { "success": False }

@app.route('/get_nodes_list', strict_slashes=False)
def get_nodes_list():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            # KEYFORNODELISTE = TROUVE EN FAISANT QUERY SQL
            return devicesInfos.get('KEYFORNODELISTE')
    return { "success": False }


########################## END OPENZWAVE ROUTES ##################################################################


########################## CONSUMER THREAD #######################################################################

class consumerThread (threading.Thread):
    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self.consumer = consumer

    def run(self):
        for message in self.consumer:
            # Consume les messages produits par KNX et OPENZWAVE et les insert
            # dans la map qui réf les infos des devices
            content = json.loads(message.value.decode("utf-8"))
            if all(item in content.keys() for item in ['deviceId']):
                device_id = int(content['deviceId'])
                value = content['value']
                devicesInfos[device_id] = value


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
        consumerThreadKNX = consumerThread(consumerKNX)
        consumerThreadZWAVE = consumerThread(consumerZWAVE)
        consumerThreadKNX.start()
        consumerThreadZWAVE.start()

    except KeyboardInterrupt:
        exit(0)
