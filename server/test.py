#!/usr/bin/env python3

import mysql.connector
from mysql.connector import errorcode


try:
    cnx = mysql.connector.connect(user='user', password='iot', host='localhost', port='3306', database='iot')
    cursor = cnx.cursor()

    query = ("SELECT number, floor, type "
    "FROM Room JOIN Beacon ON Beacon.room_number = Room.number "
    "JOIN Knx_device ON Room.number = Knx_device.room_number "
    "WHERE minor = {};".format(12302))
    query = "SELECT * FROM Beacon;"
    print(query)

    cursor.execute(query)
    # for bob in cursor:
    #     print("{}".format(bob))

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        ("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        ("Database does not exist")
    else:
        (err)
else:
    cnx.close()



