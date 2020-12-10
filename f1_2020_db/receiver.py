#! /usr/bin/env python3

import threading
import socket
import time
import datetime
from queue import Queue
from collections import namedtuple

from f1_2020_telemetry.packets import unpack_udp_packet
from .utils.packet import PacketParser

class PacketReceiver(threading.Thread):
    """ 
    Docstring
    """
    
    def __init__(self, port:int = 20777, queue=None, session=None):
        """Doc"""
        
        super().__init__()
        
        self.parser = PacketParser(queue=queue, session=session)
        self._quitflag = True
        self.socket = None

    def connect(self, port:int = 20777):
        """Docstring"""
        
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(("", port))
        
        print(f'Connected on port: {port}')

    def close(self):
        """Stop the thread"""
        
        if self._quitflag:
            self._quitflag = True
            print('PacketReceiver stopped')
        
    def run(self):
        """ Doc """
        
        self._quitflag = False
        
        if self.socket is None:
            self.connect()
        
        count = 0
        elapsed = 0
        timer = time.time()
        while not self._quitflag:
            udp_packet = self.socket.recv(2048)
            packet = unpack_udp_packet(udp_packet)
            
            start = time.time()
            self.parser.parse_packet(packet)
            elapsed += time.time() - start
            count += 1
            
            # Print progress once per second
            duration = time.time() - timer
            if duration > 1:
                print(f'Parsed {count} packets in {elapsed} seconds')
                count = 0; elapsed = 0;
                timer = time.time()
            
