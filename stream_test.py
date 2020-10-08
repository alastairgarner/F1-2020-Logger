#! /usr/bin/env python3

################################################
# Load Dependencies
################################################

import time
from queue import Queue

from f1_2020_db import DbHandler, PacketParser, Session, PacketReceiver



db_queue = Queue()
session = Session()

receiver = PacketReceiver(queue=db_queue, session=session)
receiver.connect()
db = DbHandler("f1-2020.sqlite3",db_queue)

session.get_last_session("f1-2020.sqlite3")

# Determine what the sessionSID should be
receiver.start()
db.start()
    
time.sleep(2)

db.close()
receiver.close()
