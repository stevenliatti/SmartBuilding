#!/usr/bin/env python3

import sys
import time
import os
import json
from kafka import KafkaProducer

file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)

from flask import Flask, render_template, jsonify, Response, request
from flask_mysqldb import MySQL

from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
mysql = MySQL(app)

servers = [os.getenv('IOT_DOMAIN') + ':' + str(os.getenv('IOT_KAFKA_PORT'))]
KNX_TOPIC = "knx"
OPENZWAVE_TOPIC = "zwave"
producer = KafkaProducer(bootstrap_servers=servers)

def manage_knx(minor, kind, key, percentage=-1):
    query = ("SELECT bloc, floor FROM KnxNode JOIN Device ON \
            Device.id = KnxNode.device_id JOIN Beacon ON \
            Beacon.room_number = Device.room_number \
            WHERE minor = {} AND KnxNode.kind = \"{}\";".format(minor, kind))
    print(query)
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    bloc, floor = cursor.fetchone()
    cursor.close()

    if percentage != -1:
        kafka_message = '{ "bloc": ' + str(bloc) + ', "floor": ' + str(floor) + ', "percentage": ' + str(percentage) + ' }'
    else:
        kafka_message = '{ "bloc": ' + str(bloc) + ', "floor": ' + str(floor) + ' }'

    print(kafka_message)
    producer.send(KNX_TOPIC, key=str.encode(key), value=str.encode(kafka_message))

def read_logs(minor, reason):
    query = ("SELECT value FROM Log JOIN Device \
        ON Device.id = Log.device_id JOIN Beacon ON \
        Beacon.room_number = Device.room_number \
        WHERE minor = {} AND reason = \"{}\" \
        ORDER BY timestamp DESC LIMIT 1;"
        .format(minor, reason))
    print(query)
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    value = cursor.fetchone()
    cursor.close()
    return value[0]

########################## KNX ROUTES ########################################################################

@app.route('/open_blinds', strict_slashes=False)
def open_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            manage_knx(content.get('minor'), 'blind', 'open_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/close_blinds', strict_slashes=False)
def close_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            manage_knx(content.get('minor'), 'blind', 'close_blinds')
            return { "success": True }
    return { "success": False }


@app.route('/percentage_blinds', strict_slashes=False)
def percentage_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            manage_knx(content.get('minor'), 'blind', 'percentage_blinds', percentage)
            return { "success": True }
    return { "success": False }

@app.route('/percentage_radiator', strict_slashes=False)
def percentage_radiator():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')
            manage_knx(content.get('minor'), 'radiator', 'percentage_radiator', percentage)
            return { "success": True }
    return { "success": False }

@app.route('/read_percentage_blinds', strict_slashes=False)
def read_percentage_blinds():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'read_percentage_blinds') }
    return { "success": False }

########################## END KNX ROUTES ########################################################################

########################## OPENZWAVE ROUTES ######################################################################
@app.route('/sensor_get_temperature', strict_slashes=False)
def sensor_get_temperature():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'temperature') }
    return { "success": False }

@app.route('/sensor_get_humidity', strict_slashes=False)
def sensor_get_humidity():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'relative humidity') }
    return { "success": False }

@app.route('/sensor_get_luminance', strict_slashes=False)
def sensor_get_luminance():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'luminance') }
    return { "success": False }

@app.route('/sensor_get_motion', strict_slashes=False)
def sensor_get_motion():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'sensor') }
    return { "success": False }

@app.route('/dimmer_get_level', strict_slashes=False)
def dimmer_get_level():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            return { "success": True, "value": read_logs(content.get('minor'), 'get_dimmer_level') }
    return { "success": False }

@app.route('/percentage_dimmers', strict_slashes=False)
def percentage_dimmers():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor', 'percentage']):
            percentage = content.get('percentage')

            query = ("SELECT node_id FROM ZwaveNode JOIN Device ON \
                Device.id = ZwaveNode.device_id JOIN Beacon ON \
                Beacon.room_number = Device.room_number \
                WHERE minor = {} AND name = \"{}\";".format(content.get('minor'), "ZE27"))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            node_ids = cursor.fetchone()

            for id in node_ids:
                res = {
                    "node_id": id,
                    "percentage": percentage
                }
                producer.send(OPENZWAVE_TOPIC, key=b'dimmers_set_level', value=str.encode(json.dumps(res)))

            return { "success": True }
    return { "success": False }


########################## END OPENZWAVE ROUTES ##################################################################

########################## OTHER ROUTES ######################################################################

@app.route('/get_beacons', strict_slashes=False)
def get_beacons():
    query = "SELECT * FROM Beacon;"
    print(query)
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    beacons_db = cursor.fetchall()

    beacons = []
    for beacon in beacons_db:
        beacons.append({
            "uuid": beacon[0],
            "major": beacon[1],
            "minor": beacon[2],
            "room_number": beacon[3]
        })

    return { "success": True, "beacons": beacons }

@app.route('/get_devices', strict_slashes=False)
def get_devices():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            query = ("select id, KnxNode.kind from Device join Beacon on \
                Beacon.room_number = Device.room_number join KnxNode on \
                KnxNode.device_id = Device.id where minor = {};"
                .format(content.get('minor')))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            knx_db = cursor.fetchall()

            devices = []
            for device in knx_db:
                devices.append({
                    "id": device[0],
                    "name": device[1],
                })

            query = ("select id, name from Device join Beacon on \
                Beacon.room_number = Device.room_number join ZwaveNode on \
                ZwaveNode.device_id = Device.id where minor = {};"
                .format(content.get('minor')))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            zwave_db = cursor.fetchall()

            for device in zwave_db:
                devices.append({
                    "id": device[0],
                    "name": device[1],
                })

            return { "success": True, "devices": devices }

@app.route('/avg_temperature', strict_slashes=False)
def avg_temperature():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            query = ("select cast(avg(value) as signed) as avg_temperature from Log \
                join Device on Device.id = device_id join Beacon \
                on Beacon.room_number = Device.room_number \
                WHERE minor = {} and reason = 'temperature' \
                and timestamp >= NOW() - INTERVAL 3 hour;"
                .format(content.get('minor')))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            avg_temperature = cursor.fetchone()[0]

            return { "success": True, "avg_temperature": avg_temperature }

@app.route('/avg_humidity', strict_slashes=False)
def avg_humidity():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            query = ("select cast(avg(value) as signed) as avg_humidity from Log \
                join Device on Device.id = device_id join Beacon \
                on Beacon.room_number = Device.room_number \
                WHERE minor = {} and reason = 'relative humidity' \
                and timestamp >= NOW() - INTERVAL 3 hour;"
                .format(content.get('minor')))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            avg_humidity = cursor.fetchone()[0]

            return { "success": True, "avg_humidity": avg_humidity }

@app.route('/avg_luminance', strict_slashes=False)
def avg_luminance():
    content = request.args
    if content:
        if all(item in content.keys() for item in ['uuid', 'major', 'minor']):
            query = ("select cast(avg(value) as signed) as avg_luminance from Log \
                join Device on Device.id = device_id join Beacon \
                on Beacon.room_number = Device.room_number \
                WHERE minor = {} and reason = 'luminance' \
                and timestamp >= NOW() - INTERVAL 3 hour;"
                .format(content.get('minor')))
            print(query)
            cursor = mysql.connection.cursor()
            cursor.execute(query)
            avg_luminance = cursor.fetchone()[0]

            return { "success": True, "avg_luminance": avg_luminance }

########################## END OTHER ROUTES ##################################################################


from logging import FileHandler, Formatter, DEBUG

if __name__ == '__main__':
    try:
        file_handler = FileHandler("flask.log")
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)
        app.run(host='::', debug=False, use_reloader=False)

    except KeyboardInterrupt:
        exit(0)
