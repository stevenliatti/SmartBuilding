#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, sys
from knxnet import *


class knx:
    def __init__(self, group_address, data, data_size, apci):
        self.gateway_ip = "127.0.0.1"
        self.gateway_port = 3671
        self.endpoint_port = 3672
        self.group_address = group_address
        self.data = data
        self.data_size = data_size
        self.apici = apci

        # -> Socket creation
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.endpoint_port))
        # -> in this example, for the sake of simplicity, the two ports are the same
        # With the simulator, the gateway_ip must be set to 127.0.0.1 and gateway_port to 3671
        self.data_endpoint = (self.gateway_ip, self.endpoint_port)
        self.control_enpoint = (self.gateway_ip, self.endpoint_port)

    def transmit(self, object_frame, message_status):
        self.sock.sendto(object_frame, (self.gateway_ip, self.gateway_port))
        data_recv, addr = self.sock.recvfrom(1024)
        conn_resp_object = knxnet.decode_frame(data_recv)
        print(message_status)
        print(conn_resp_object)
        return conn_resp_object

    def creat_connexion(self):
        # -> Sending Connection request
        conn_req_object = knxnet.create_frame(
            knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
            self.control_enpoint,
            self.data_endpoint
        )
        conn_resp_object = self.transmit(conn_req_object.frame, "CONNECTION_RESPONSE")

        # <- Retrieving channel_id from Connection response
        conn_channel_id = conn_resp_object.channel_id

        # Send connection state request
        conn_state_request_object = knxnet.create_frame(
            knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
            conn_channel_id,
            self.control_enpoint
        )
        conn_resp_object = self.transmit(conn_state_request_object.frame, "CONNECTION_STATE_RESPONSE")
        return conn_channel_id

    def send_datas(self, conn_channel_id):
        # Send tunelling ack
        tunnelling_request_obj = knxnet.create_frame(
            knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
            knxnet.GroupAddress.from_str(group_address),
            conn_channel_id,
            self.data,
            self.data_size,
            self.apci
        )
        # Receive tunelling ack and request from gateway
        conn_resp_object = self.transmit(tunnelling_request_obj.frame, "TUNNELLING_ACK")
        conn_resp_object = self.transmit(tunnelling_request_obj.frame, "TUNNELLING_REQUEST")
        return conn_resp_object


    def disconnect(self, conn_channel_id):
        # Send disconnect request
        disconnect_req_obj = knxnet.create_frame(
            knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST,
            conn_channel_id,
            self.control_enpoint
        )
        conn_resp_object = self.transmit(disconnect_req_obj.frame, "DISCONNECT_RESPONSE")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: " + sys.argv[0] + " '<action>/<floor>/<bloc>' <data> <size> <apci>")
        exit(1)

        #data = 100
        #data size = 1 ou 2 bytes
        #apic = 0 pour lire 2 pour écrire

        #action = x
        #floor = 4eme
        #bloc = 1

    group_address = sys.argv[1]
    data = int(sys.argv[2])
    data_size = int(sys.argv[3])
    apci = int(sys.argv[4])

    knx = knx(group_address, data, data_size, apci)
    conn_channel_id = knx.creat_connexion()
    knx.send_datas(conn_channel_id)
    knx.disconnect(conn_channel_id)