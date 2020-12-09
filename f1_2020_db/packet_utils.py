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
        
        for SID,UID in self.previous:
            if sessionUID == int(UID):
                print(f'Appending to previous session: {SID}, {sessionUID}')
                self.SID = SID
                self.UID = sessionUID
                return
        
        self.UID = sessionUID
        self.get_SID()
        
    def get_last_session(self, filename:str = 'f1-2020.sqlite3'):
        """ """
        
        if os.path.isfile(filename):
            conn = sqlite3.connect(filename)
            
            self.previous = conn.execute("SELECT sessionSID,sessionUID FROM session ORDER BY sessionSID DESC LIMIT 20").fetchall()
            
            entries = conn.execute("SELECT MAX(packetUID),sessionSID FROM packets;").fetchall()
            if entries[0][0] != None:
                self.pID = entries[0][0] + 1

            conn.close()
            
        else:
            print(f"'{filename}' does not exist - can't grab last session")
            
            
class PacketParser(object):
    """
    Docstring
    """
    
    def __init__(self, queue=None, session=None):
        """docstring"""
        
        if queue is None:
            queue = Queue()
            print("No Queue object passed - created one instead")

        self.sess = session
        self._queue = queue
        
        self.updated = {
            'session': True,
            'participants': True
        }
        
        self._cache = {
            'laptimes': [[] for i in range(22)]
        }
        
    # def get_rows(self, packet, fields={'header': 'sessionUID'}, length=1, prepend=[]):
    #     """
    #     Grab relevant data from a packet and return it in a tuple, formatted for database entry.
    #     Takes a dictionary to indicate which fields to grab from the packet.
    #     Can specific values to be prepended to the tuple, to tag data.
    #     """
        
    #     n_prep = len(prepend)
        
    #     field_data = []
    #     for key in fields.keys():
    #         subpacket = getattr(packet, key, packet) # fails on 'packet' key, returning the base packet instead
            
    #         # If subpacket is an array, loop over array rows and grab fielsds
    #         if hasattr(subpacket,'__len__'):
    #             field_data.append( [[getattr(subpacket_row, field) for field in fields[key]] for subpacket_row in subpacket] )
                
    #         # Else, if the packet is not an array, just grab the fields
    #         else:
    #             field_data.append( [[getattr(subpacket, field) for field in fields[key]]] )

    #     # Make a blank list of lists with length equal to the longest array
    #     n = [len(list_) for list_ in field_data]
    #     rows = [[*prepend] for i in range(max(n))]
        
    #     # If one of the lists has >1 entries, prepend the array index
    #     if max(n) > 1:
    #         field_data = [[[i] for i in range(max(n))]] + field_data
    #         n = [max(n)] + n

    #     # Fill the 
    #     for i,list_ in enumerate(field_data):
    #         for j in range(len(rows)):
    #             rows[j].extend(list_[j%n[i]])
                
    #     return rows
    
    def getattrs(self, obj, attrs):
        return [getattr(obj, attr) for attr in attrs]

    def get_rows(self, packet, fields, length=1, prepend=[]):
        if length > 1:
            data = [[*prepend,i] for i in range(length)]
        else:
            data = [[*prepend] for i in range(length)]
            
        for key,attrs in fields.items():
            subpack = getattr(packet, key, packet)
            
            if hasattr(subpack,'_length_'):
                vals = [self.getattrs(subrow, attrs) for subrow in subpack]
                _ = [data[i].extend(vals[i]) for i in range(length)]

            else:
                val = self.getattrs(subpack, attrs)
                _ = [data[i].extend(val) for i in range(length)]
                
        return data
    
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
            self.updated = {k: True for k in self.updated}
        
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
            self._parse_laptimes(packet)

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
            length=1,
            prepend=[TableID.PACKETS.value, self.sess.SID, self.sess.pID])
        self.stage_entries(entries)
        
    def _parse_session(self, packet, restrict=True):
        """Parse the PacketSessionData_V1 packet"""
        
        #
        # if self._prev_id['session'] != packet.header.sessionUID:
        if self.updated['session']:
            
            entries = self.get_rows(
                packet, 
                EntryFields.SESSIONS, 
                length=1,
                prepend=(TableID.SESSION.value, self.sess.SID, str(self.sess.UID)))
            self.stage_entries(entries)
            
            # self._prev_id['session'] = packet.header.sessionUID
            self.updated['session'] = False
            print('Updated session')
        
        if not restrict:
            # Get entries for MARSHALS table
            entries = self.get_rows(
                packet, 
                EntryFields.MARSHALS, 
                length=21,
                prepend=(TableID.MARSHALS.value, self.sess.pID))
            self.stage_entries(entries)
            
            # Get entries for WEATHER table
            entries = self.get_rows(
                packet, 
                EntryFields.WEATHER, 
                length=20,
                prepend=(TableID.WEATHER.value, self.sess.pID))
            self.stage_entries(entries)
            
    def _parse_participants(self, packet, restrict=True):
        """Parse the ParticipantData_V1 packet"""
        
        # Get entries for PARTICIPANTS table
        # if self._prev_id['participants'] != packet.header.sessionUID:
        if self.updated['participants']:
            
            entries = self.get_rows(
                packet,
                EntryFields.PARTICIPANTS, 
                length=22,
                prepend=(TableID.PARTICIPANTS.value, self.sess.SID))
            self.stage_entries(entries)
            
            # self._prev_id['participants'] = packet.header.sessionUID
            self.updated['participants'] = False
            print('Updated participants')
            
    def _parse_lapdata(self, packet):
        """docstring"""
        
        # Get entries for LAPDATA table
        entries = self.get_rows(
            packet, 
            EntryFields.LAPDATA, 
            length=22,
            prepend=(TableID.LAPDATA.value, self.sess.pID))
        self.stage_entries(entries)
       
    def _parse_laptimes(self, packet):
        """docstring"""
        
        # Get entries for LAPDATA table
        entries = self.get_rows(
            packet, 
            EntryFields.LAPTIMES, 
            length=22,
            prepend=(TableID.LAPTIMES.value, self.sess.pID))
        
        entries_new = [entries[i] for i in range(22) if entries[i][2:4]!=self._cache['laptimes'][i][2:4]]
        if len(entries_new) > 0:
            self.stage_entries(entries_new)
            self._cache['laptimes'] = entries
         
    def _parse_telemetry(self, packet):
        """docstring"""
        
        # Get entries for LAPDATA table
        entries = self.get_rows(
            packet, 
            EntryFields.TELEMETRY, 
            length=22,
            prepend=(TableID.TELEMETRY.value, self.sess.pID))
        self.stage_entries(entries)
