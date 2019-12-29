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

import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)

servers = ['iot.liatti.ch:29092']
KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"
producer = KafkaProducer(bootstrap_servers=servers)
consumerKNX = KafkaConsumer(KNX_TOPIC, bootstrap_servers=servers)
consumerZWAVE = KafkaConsumer(OPENZWAVE_TOPIC, bootstrap_servers=servers)

try:
    cnx = mysql.connector.connect(user='root', password='iot', host='db', database='iot')
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        ("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        ("Database does not exist")
    else:
        (err)
else:
    cnx.close()

devicesInfos = {}

########################## KNX ROUTES ########################################################################

@app.route('/open_blinds', strict_slashes=False)
def open_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            query = ("SELECT number, floor, type "
                "FROM Room JOIN Beacon ON Beacon.room_number = Room.number "
                "JOIN Knx_device ON Room.number = Knx_device.room_number "
                "WHERE minor = {};".format(content.get('minor')))
            print(query)

            # TODO: marche pas
            # cursor.execute(query)
            # for bob in cursor:
                # print("{}".format(bob))

            producer.send(KNX_TOPIC, key=b'open_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/close_blinds', strict_slashes=False)
def close_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            producer.send(KNX_TOPIC, key=b'close_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/percentage_blinds', strict_slashes=False)
def percentage_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            producer.send(KNX_TOPIC, key=b'percentage_blinds', value=str.encode('{"percentage":' + percentage + '}'))
            return { "success": True }
    return { "success": False }

@app.route('/percentage_radiator', strict_slashes=False)
def percentage_radiator():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            producer.send(KNX_TOPIC, key=b'percentage_radiator', value=str.encode('{"percentage":' + percentage + '}'))
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
        cnx.close()
        exit(0)
