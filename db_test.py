#! /usr/bin/env python3

################################################
# Load Dependencies
################################################

import sqlite3
import pickle
import time
import datetime
import os

import threading
from queue import Queue

from f1_2020_telemetry.packets import unpack_udp_packet
from f1_2020_db import DbHandler, PacketParser, Session


            
                   
#################
### SETUP
os.remove("f1-2020.sqlite3")

with open('packets.dictionary', 'rb') as file:
    # Read & print the entire file
    p = pickle.load(file)
    
packets = []
for string in p:
    packets.append(unpack_udp_packet(string))
    
################
db_queue = Queue()
session = Session()

pp = PacketParser(db_queue, session)
db = DbHandler("f1-2020.sqlite3",db_queue)

session.get_last_session("f1-2020.sqlite3")

# Determine what the sessionSID should be
db.start()

for packet in packets:
    pp.parse_packet(packet, restrict=False)
    # time.sleep(1/1000)
    
time.sleep(2)
db.close()





