#! /usr/bin/env python3

"""

"""


################################################
# Load Dependencies
################################################

from queue import Queue

from ..utils import DbHandler, PacketParser, Session
from ..receiver import PacketReceiver

################################################
# Functions
################################################

def main():
    db_queue = Queue()
    session = Session()

    receiver = PacketReceiver(queue=db_queue, session=session)
    receiver.connect()
    db = DbHandler("f1-2020.sqlite3",db_queue)

    # Determine what the sessionSID should be
    session.get_last_session("f1-2020.sqlite3")

    receiver.start()
    db.start()
        
    receiver.join()
    db.join()    

# db.close()
# receiver.close()

if __name__ == '__main__':
    main()
