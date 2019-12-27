#!/usr/bin/env python3

import sys
import time
import os

from kafka import KafkaProducer

file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)

from flask import Flask, render_template, jsonify, Response, request

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers=['iot.liatti.ch:29092'])
topic_openzwave = "zwave"
topic_knx = "knx"

@app.route('/', strict_slashes=False)
def index():
    # returns a html page with a list of routes
    return render_template("index.html", title=configpi.name)


@app.route('/network/info', strict_slashes=False)
def network_info():
    producer.send(topic_openzwave, key=b'network_info')
    return backend.network_info()

@app.route('/network/set_sensor_nodes_basic_configuration', methods=['GET', 'POST'], strict_slashes=False)
def network_configure_sensor_Nodes():
    # configure all the nodes of the network with a specific configuration
    if request.method == 'POST':
        content = request.get_json()
        if all(item in content.keys() for item in ['Group_Interval', 'Group_Reports', 'Wake-up_Interval']):
            Grp_interval = int(content['Group_Interval'])
            Grp_reports = int(content['Group_Reports'])
            Wakeup_interval = int(content['Wake-up_Interval'])
            producer.send(topic_openzwave, key=b'network_info', value=str.encode("{\"Grp_interval\"}:"+str(Grp_interval)))
        return 'wrong input'
    return 'use POST method'

@app.route('/network/get_nodes_configuration', strict_slashes=False)
def get_nodes_Configuration():
    # gets a html with the list of nodes with their config parameters
    producer.send(topic_openzwave, key=b'network_get_nodes_configuration')

    return backend.get_nodes_Configuration()

@app.route('/network/start', strict_slashes=False)
def start():
    # start software representation
    backend.start()
    return "Z-Wave Network Started"

@app.route('/network/stop', strict_slashes=False)
def stop():
    # stop the software representation
    backend.stop()
    time.sleep(2)
    return "Z-Wave Network Stopped"

@app.route('/network/reset', strict_slashes=False)
def reset():
    # restart software representation
    backend.reset()
    return "Z-Wave Network Reset"

@app.route('/nodes/get_nodes_list', strict_slashes=False)
def nodes():
    # gets a list of all nodes in the network in a JSON format
    return backend.get_nodes_list()


@app.route('/nodes/add_node', methods=['POST'], strict_slashes=False)
def add_node():
    # passes controller to inclusion mode
    return backend.addNode()

@app.route('/nodes/remove_node', methods=['POST'], strict_slashes=False)
def remove_node():
    # passes controller to exclusion mode
    return backend.removeNode()

@app.route('/nodes/set_parameter', methods=['GET', 'POST'], strict_slashes=False)
def set_config_param():
    # sets a config parameter of a sensor node
    if request.method == 'POST':
        content = request.get_json()
        if all(item in content.keys() for item in ['node_id', 'parameter_index', 'value', 'size']):
            node = int(content['node_id'])
            param = int(content['parameter_index'])
            value = int(content['value'])
            size = int(content['size'])
            return backend.set_node_config_parameter(node, param, value, size)
        return 'wrong input'
    return 'use POST method'

@app.route('/nodes/<int:node>/get_parameter/<int:param>', strict_slashes=False)
def get_config_param(node, param):
    # gets a config parameter of a sensor node
    return backend.get_node_config_parameter(node, param)

@app.route('/nodes/<int:node>/get_battery', strict_slashes=False)
def get_battery(node):
    return backend.get_battery(node)

@app.route('/nodes/set_location', methods=['GET', 'POST'], strict_slashes=False)
def set_node_location():
    if request.method == 'POST':
        content = request.get_json()
        if all(item in content.keys() for item in ['node_id', 'value']):
            node = int(content['node_id'])
            value = content['value']
            return backend.set_node_location(node, value)
        return 'wrong input'
    return 'use POST method'

@app.route('/nodes/set_name', methods=['GET', 'POST'], strict_slashes=False)
def set_node_name():
    if request.method == 'POST':
        content = request.get_json()
        if all(item in content.keys() for item in ['node_id', 'value']):
            node = int(content['node_id'])
            value = content['value']
            return backend.set_node_name(node, value)
        return 'wrong input'
    return 'use POST method'


@app.route('/nodes/<int:node>/get_location', strict_slashes=False)
def get_node_location(node):
    return backend.get_node_location(node)

@app.route('/nodes/<int:node>/get_name', strict_slashes=False)
def get_node_name(node):
    return backend.get_node_name(node)

@app.route('/nodes/<int:node>/get_neighbours', strict_slashes=False)
def get_neighbours_list(node):
    return backend.get_neighbours_list(node)

@app.route('/sensors/get_sensors_list', strict_slashes=False)
def get_sensors_list():
    # returns a list of all sensors in the network in a JSON format(only sensors)
    return backend.get_sensors_list()


@app.route('/sensors/<int:node>/get_all_measures', strict_slashes=False)
def get_all_measures(node):
    return backend.get_all_Measures(node)


@app.route('/sensors/<int:node>/get_temperature', strict_slashes=False)
def get_temperature(node):
    return backend.get_temperature(node)


@app.route('/sensors/<int:node>/get_humidity', strict_slashes=False)
def get_humidity(node):
    return backend.get_humidity(node)

@app.route('/sensors/<int:node>/get_luminance', strict_slashes=False)
def get_luminance(node):
    return backend.get_luminance(node)

@app.route('/sensors/<int:node>/get_motion', strict_slashes=False)
def get_motion(node):
    return backend.get_motion(node)


@app.route('/dimmers/get_dimmers_list', strict_slashes=False)
def get_dimmers():
    return backend.get_dimmers()

@app.route('/dimmers/<int:node_id>/get_level', strict_slashes=False)
def get_dimmer_level(node_id):
    return backend.get_dimmer_level(node_id)


@app.route('/dimmers/set_level', methods=['GET', 'POST'], strict_slashes=False)
def set_dimmer_level():
    if request.method == 'POST':
        content = request.get_json()
        if all(item in content.keys() for item in ['node_id', 'value']):
            node = int(content['node_id'])
            value = int(content['value'])
            if 99 < value:
                value = 99
            elif value < 0:
                value = 0
            backend.set_dimmer_level(node, value)
            return "dimmer %s is set to level %s" % (node, value)
        return 'wrong input'
    return 'use POST method'


from logging import FileHandler, Formatter, DEBUG

if __name__ == '__main__':
    try:
        #backend.start()
        file_handler = FileHandler("flask.log")
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)

        app.run(host='::', debug=False, use_reloader=False)

    except KeyboardInterrupt:
        exit(0)