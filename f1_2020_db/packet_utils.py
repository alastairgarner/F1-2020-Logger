#! /usr/bin/env python3

import os
import time
import datetime
import sqlite3
import threading
from queue import Queue

from f1_2020_telemetry.packets import PacketID

from .sqlite_utils import TableID, EntryFields

class Session(object):
    """Contains details on the current session"""
    
    def __init__(self):
        
        self.SID = None
        self.UID = None
        self.pID = 0
        
        self.get_SID()
        
    def get_SID(self):
        """Docstring"""
        
        date = datetime.datetime.now()
        date_str = date.strftime('%Y%m%d%H%M%S')[2:]
        self.SID = int(date_str)

    def update(self, sessionUID):
        """Docstring"""
        
        self.UID = sessionUID
        self.get_SID()
        
    def get_last_session(self, filename:str = 'f1-2020.sqlite3'):
        """ """
        
        if os.path.isfile(filename):
            conn = sqlite3.connect(filename)
            # entries = conn.execute("SELECT sessionSID,sessionUID FROM session;").fetchall()
            entries = conn.execute("SELECT MAX(packetUID),sessionSID FROM packets;").fetchall()
            
            if entries[0][0] != None:
                self.pID = entries[0][0] + 1

            conn.close()
            
        else:
            print(f"'{filename}' does not exist - can't grab last session")
            
            
class PacketParser(object):
    

    def __init__(self, queue=None, session=None):
        """docstring"""
        
        if queue is None:
            queue = Queue()
            print("No Queue object passed - created one instead")

        self.sess = session
        self._queue = queue
        
        self._prev_id = {
            'session': None,
            'participants': None
        }
        
    def get_rows(self, packet, fields={'header': 'sessionUID'}, prepend=[]):
        """
        Grab relevant data from a packet and return it in a tuple, formatted for database entry.
        Takes a dictionary to indicate which fields to grab from the packet.
        Can specific values to be prepended to the tuple, to tag data.
        """
        
        n_prep = len(prepend)
        
        field_data = []
        for key in fields.keys():
            subpacket = getattr(packet, key, packet) # fails on 'packet' key, returning the base packet instead
            
            # If subpacket is an array, loop over array rows and grab fielsds
            if hasattr(subpacket,'__len__'):
                field_data.append( [[getattr(subpacket_row, field) for field in fields[key]] for subpacket_row in subpacket] )
                
            # Else, if the packet is not an array, just grab the fields
            else:
                field_data.append( [[getattr(subpacket, field) for field in fields[key]]] )

        # Make a blank list of lists with length equal to the longest array
        n = [len(list_) for list_ in field_data]
        rows = [[*prepend] for i in range(max(n))]
        
        # If one of the lists has >1 entries, prepend the array index
        if max(n) > 1:
            field_data = [[[i] for i in range(max(n))]] + field_data
            n = [max(n)] + n

        # Fill the 
        for i,list_ in enumerate(field_data):
            for j in range(len(rows)):
                rows[j].extend(list_[j%n[i]])
                
        return rows
    
    def stage_entries(self, entries):
        """Add entries to the commit queue"""
        
        [self._queue.put(entry) for entry in entries]
    
    def parse_packet(self, packet=None, **kw):
        """Send the packet to the correct parser method"""
        
        # Check inputs
        if packet is None:
            raise TypeError('"packet" argument missing')

        if packet.header.sessionUID != self.sess.UID:
            self.sess.update(packet.header.sessionUID)
        
        # Parse the packet header
        self._parse_header(packet)
        
        # Determine which parser to run
        packetId = packet.header.packetId
        
        if packetId == PacketID.MOTION.value:
            pass
        
        elif packetId == PacketID.SESSION.value:
            self._parse_session(packet, **kw)
        
        elif packetId == PacketID.LAP_DATA.value:
            self._parse_lapdata(packet)

        elif packetId == PacketID.EVENT.value:
            pass

        elif packetId == PacketID.PARTICIPANTS.value:
            self._parse_participants(packet, **kw)

        elif packetId == PacketID.CAR_SETUPS.value:
            pass

        elif packetId == PacketID.CAR_TELEMETRY.value:
            self._parse_telemetry(packet)
        
        elif packetId == PacketID.CAR_STATUS.value:
            pass

        elif packetId == PacketID.FINAL_CLASSIFICATION.value:
            pass

        elif packetId == PacketID.LOBBY_INFO.value:
            pass
        
        self.sess.pID += 1

    def _parse_header(self, packet):
        """Parse the header, for the 'packets' table"""
        
        entries = self.get_rows(
            packet,
            EntryFields.PACKETS,
            prepend=[TableID.PACKETS.value, self.sess.SID, self.sess.pID])
        self.stage_entries(entries)
        
    def _parse_session(self, packet, restrict=True):
        """Parse the PacketSessionData_V1 packet"""
        
        #
        if self._prev_id['session'] != packet.header.sessionUID:
            
            entries = self.get_rows(
                packet, 
                EntryFields.SESSIONS, 
                prepend=(TableID.SESSION.value, self.sess.SID, str(self.sess.UID)))
            # entries[0][2] = str(entries[0][2]) # Hacky way to resolve large integer problem
            self.stage_entries(entries)
            
            self._prev_id['session'] = packet.header.sessionUID
            print('Updated session')
        
        if not restrict:
            # Get entries for MARSHALS table
            entries = self.get_rows(
                packet, 
                EntryFields.MARSHALS, 
                prepend=(TableID.MARSHALS.value, self.sess.pID))
            self.stage_entries(entries)
            
            # Get entries for WEATHER table
            entries = self.get_rows(
                packet, 
                EntryFields.WEATHER, 
                prepend=(TableID.WEATHER.value, self.sess.pID))
            self.stage_entries(entries)
            
    def _parse_participants(self, packet, restrict=True):
        """Parse the ParticipantData_V1 packet"""
        
        # Get entries for PARTICIPANTS table
        if self._prev_id['participants'] != packet.header.sessionUID:
            
            entries = self.get_rows(
                packet,
                EntryFields.PARTICIPANTS, 
                prepend=(TableID.PARTICIPANTS.value, self.sess.SID))
            self.stage_entries(entries)
            
            self._prev_id['participants'] = packet.header.sessionUID
            print('Updated participants')
            
    def _parse_lapdata(self, packet):
        """docstring"""
        
        # Get entries for LAPDATA table
        entries = self.get_rows(
            packet, 
            EntryFields.LAPDATA, 
            prepend=(TableID.LAPDATA.value, self.sess.pID))
        self.stage_entries(entries)
        
    def _parse_telemetry(self, packet):
        """docstring"""
        
        # Get entries for LAPDATA table
        entries = self.get_rows(
            packet, 
            EntryFields.TELEMETRY, 
            prepend=(TableID.TELEMETRY.value, self.sess.pID))
        self.stage_entries(entries)
