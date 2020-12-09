#! /usr/bin/env python3

import sqlite3
import ctypes
import time
import threading
from queue import Queue

from f1_2020_telemetry.types import (TeamIDs, TrackIDs, ButtonFlag, InfringementTypes, NationalityIDs, PenaltyTypes, SurfaceTypes)

from .types import TableID,DriverIDs

#
class DbHandler(threading.Thread):
    """
    Docstring
    """
    
    def __init__(self, db_file, db_queue):
        """docstring"""

        super().__init__()
        
        self.queue = db_queue
        self.file = db_file
        self.conn = SQLiteConnect(filename=db_file)

        self._lock = threading.Lock()
        
        self._entries = dict([[i.value,[]] for i in TableID])

        self._sessionUID = None
        self._quitflag = True
        
    def close(self):
        """Interrupt the main run loop"""
        
        if self.conn is not None:
            self._quitflag = True
    
    def run(self):
        """Commit queue packets to SQLite DB"""
        
        self.conn.open()
        self._quitflag = False
        
        while not self._quitflag:
            # print('...running')
            # Commit entries to db
            self.commit_entries(debug=False)
            
            # Clear the committed entries from memory
            self._entries = {k:[] for (k,_) in self._entries.items()}
            
            time.sleep(1)
        
        # Close database, if 'close' method invoked
        self.conn.close()
        
    def commit_entries(self, debug=True):
        """Docstring"""
        
        start = time.time()
        
        num_entries = self.queue.qsize()
        for i in range(num_entries):
            key,*data = self.queue.get()
            self._entries[key].append(data)
            
        if debug:
            print(f'Debug: Committed {num_entries} entries to the database')
            
        else:
            self.commit(Query.INSERT_INTO_SESSION, self._entries[TableID.SESSION])
            self.commit(Query.INSERT_INTO_PACKETS, self._entries[TableID.PACKETS])
            self.commit(Query.INSERT_INTO_PARTICIPANTS, self._entries[TableID.PARTICIPANTS])
            self.commit(Query.INSERT_INTO_LAPDATA, self._entries[TableID.LAPDATA])
            self.commit(Query.INSERT_INTO_LAPTIMES, self._entries[TableID.LAPTIMES])
            self.commit(Query.INSERT_INTO_TELEMETRY, self._entries[TableID.TELEMETRY])
            
        print(f'Committed {num_entries} packets in {time.time()-start} seconds')
        
    def commit(self, query: str, entries: list):
        """Wrapper for sqlite3.executemany()"""
        
        if len(entries) != 0:
            self.conn.execute(query,entries)
            
            
    def _commit_participants(self,list_entries):
        """Insert data to participants table"""
        
        if len(list_entries) > 0:
            print(list_entries[0])
            
            self._cursor.executemany(self._insert_into_participants, list_entries)
            self._conn.commit()
            
            print('Committed to participants table')
        
    def _commit_session(self,list_entries):
        """Insert data to participants table"""
        
        if len(list_entries) > 0:
            print(list_entries[0])
            
            self._cursor.executemany(self._insert_into_session, list_entries)
            self._conn.commit()
            
            print('Committed to session table')
        
    def _commit_lapdata(self, list_entries):
        """ """
        
        self._cursor.executemany(self._insert_into_lapdata, list_entries)
        self._conn.commit()

    def _commit_laptimes(self, list_entries):
        """ """
        
        self._cursor.executemany(self._insert_into_lapdata, list_entries)
        self._conn.commit()

    def _commit_packets(self, list_entries):
        """ """
        
        self._cursor.executemany(self._insert_into_lapdata, list_entries)
        self._conn.commit()

class SQLiteConnect(object):
    """
    SQLiteConnect
    Contains functions for creating and inserting to F1-2020 tables
    """

    def __init__(self, filename:str = "f1-2020.sqlite3"):
        """Doc"""

        self.file = filename

        self.conn = None
        self.cursor = None
        
        setup_sqlite_types()

        # Check tables exist - create them if not
        tables = self.select(Query.CHECK_TABLES)
        if len(tables) == 0:
            self.open()
            self.create_tables()
            self.fill_static_tables()
            self.close()
    
            print(f'Created {filename} file.')

    def open(self):
        """Connect to SQLite database"""

        if not ((self.conn is None) & (self.cursor is None)):
            print('Connection already established.')
            return
        
        self.conn = sqlite3.connect(self.file, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

        print(f'Connected to {self.file}.')

    def close(self):
        """Close the connection to the database"""

        try:
            self.cursor.close()
            self.conn.close()
            print(f'Closed connection to {self.file}')
        except:
            print('No database connection to close.')

        self.cursor = None
        self.conn = None

    def create_tables(self):
        """Create all necessary tables"""

        tables = [attr for attr in dir(Query) if attr.startswith('CREATE')]

        # Using Query class (Enum), loop through to execute CREATE commands
        for table in tables:
            self.cursor.execute(getattr(Query,table))
            print('Created table: \'{}\''.format(
                table.split('_')[-1].lower()))

    def fill_static_tables(self):
        """Build the static data tables, using predefined dictionaries"""

        # Fill Drivers table
        drivers = []
        for k, v in DriverIDs.items():
            drivers.append([k, *v[0].split(' ', 1), v[1]])
        self.cursor.executemany(Query.INSERT_INTO_DRIVERS, drivers)
        self.conn.commit()

        # Fill Teams
        self.cursor.executemany(Query.INSERT_INTO_TEAMS, list(TeamIDs.items()))
        self.conn.commit()

        # Fill Tracks
        self.cursor.executemany(Query.INSERT_INTO_TRACKS, list(TrackIDs.items()))
        self.conn.commit()
        
    def execute(self, query: str, entries: list, *args):
        """Calls execute function on cursor"""
        
        if len(entries) != 0:
            self.cursor.executemany(query, entries, *args)
            self.conn.commit()
            
    def select(self, query: str) -> list:
        """Runs a Select query through the database"""
        
        isconnected = self.conn != None
        if not isconnected:
            self.open()
            
        result = self.cursor.execute(query).fetchall()

        if not isconnected:
            self.close()
            
        return result


class EntryFields(object):
    """
    A class to parse packets from the f1-2020-telemetry package.
    """
    
    PACKETS = {
        'header': ['packetId', 'frameIdentifier', 'sessionTime', 'packetVersion']
    }
    SESSIONS = {
        'header': ['packetFormat','gameMajorVersion', 'gameMinorVersion', 'playerCarIndex', 'secondaryPlayerCarIndex'],
        'packet': ["totalLaps", "trackLength", "sessionType", "trackId", "formula", "networkGame", "sessionDuration",
                   "sliProNativeSupport",'isSpectating','spectatorCarIndex']
    }
    PARTICIPANTS = {
        'packet': ['numActiveCars'],
        'participants': ['aiControlled', 'driverId', 'name', 'nationality', 'raceNumber', 'teamId', 'yourTelemetry']
    }
    LAPDATA = {
        'lapData': ['sector1TimeInMS','sector2TimeInMS','currentLapTime','lapDistance','totalDistance','safetyCarDelta',
                    'carPosition','currentLapNum','pitStatus','sector','currentLapInvalid','driverStatus','resultStatus']
    }
    LAPTIMES = {
        'lapData': ['currentLapNum', 'lastLapTime']
    }
    TELEMETRY = {
        'carTelemetryData': ['speed', 'throttle', 'brake', 'clutch', 'gear',
                             'engineRPM', 'drs', 'revLightsPercent', 'brakesTemperature',
                             'tyresSurfaceTemperature', 'tyresInnerTemperature', 'engineTemperature', 'tyresPressure', 'surfaceType']
    }
    #####
    TIME = {
        'packet': ["sessionTimeLeft", "gamePaused"]
    }
    STATUS = {
        'packet': ["safetyCarStatus"]
    }
    WEATHER = {
        'packet': ['trackTemperature', 'airTemperature', 'weather'],
        'weatherForecastSamples': ['timeOffset', 'weather', 'trackTemperature', 'airTemperature']
    }
    MARSHALS = {
        'packet': ["pitSpeedLimit", "numMarshalZones"],
        'marshalZones': ['zoneStart', 'zoneFlag']
    }
    
    

def format_fields(dictionary:dict) -> str:
    fields = [val for k,vals in dictionary.items() for val in vals]
    fields_str = ', '.join(fields)
    qmarks_str = ', '.join('?'*len(fields))
    return fields_str,qmarks_str


class Query(object):
    """A table of useful SQLite queries """

    # CREATE STATEMENTS - Streamed tables
    CREATE_TABLE_SESSION = """
        CREATE TABLE IF NOT EXISTS session (
            sessionSID              INTEGER     NOT NULL,
            sessionUID              TEXT     NOT NULL,
            sessionType             INTEGER     NOT NULL,
            trackId                 INTEGER     NOT NULL,
            trackLength             INTEGER     NOT NULL,
            totalLaps               INTEGER     NOT NULL,
            networkGame             INTEGER     NOT NULL,
            isSpectating              INTEGER     NOT NULL,
            spectatorCarIndex INTEGER NOT NULL,
            sliProNativeSupport     INTEGER     NOT NULL,
            packetFormat INTEGER NOT NULL,
            gameMajorVersion INTEGER NOT NULL,
            gameMinorVersion INTEGER NOT NULL,
            playerCarIndex INTEGER NOT NULL,
            secondaryPlayerCarIndex INTEGER NOT NULL,
            formula                 INTEGER     NOT NULL,
            sessionDuration         INTEGER     NOT NULL,
            PRIMARY KEY (sessionSID,sessionUID)
        );
    """
    CREATE_TABLE_PACKETS = """
        CREATE TABLE IF NOT EXISTS packets (
            packetUID INTEGER NOT NULL,
            sessionSID INTEGER NOT NULL,
            packetId INTEGER NOT NULL,
            frameIdentifier INTEGER NOT NULL,
            sessionTime FLOAT NOT NULL,
            packetVersion INTEGER NOT NULL,
            PRIMARY KEY (packetUID)
        );
    """
    CREATE_TABLE_PARTICIPANTS = """
        CREATE TABLE IF NOT EXISTS participants (
            sessionSID      INTEGER     NOT NULL,
            vehicleID         INTEGER     NOT NULL,
            numActiveCars INTEGER NOT NULL,
            aiControlled    INTEGER     NOT NULL,
            driverId        INTEGER     NOT NULL,
            teamId          INTEGER     NOT NULL,
            raceNumber      INTEGER     NOT NULL,
            nationality     INTEGER     NOT NULL,
            name            VARCHAR     NOT NULL,
            yourTelemetry   INTEGER     NOT NULL,
            PRIMARY KEY (sessionSID, vehicleID)
        );
    """
    CREATE_TABLE_LAPDATA = """
        CREATE TABLE IF NOT EXISTS lapdata (
            packetUID INTEGER NOT NULL,
            vehicleID                 INTEGER     NOT NULL,
            sector1TimeInMS         FLOAT       NOT NULL,
            sector2TimeInMS         FLOAT       NOT NULL,
            currentLapTime          FLOAT       NOT NULL,
            lapDistance             FLOAT       NOT NULL,
            totalDistance           FLOAT       NOT NULL,
            safetyCarDelta          FLOAT       NOT NULL,
            carPosition             INTEGER     NOT NULL,
            currentLapNum           INTEGER     NOT NULL,
            pitStatus               INTEGER     NOT NULL,
            sector                  INTEGER     NOT NULL,
            currentLapInvalid       INTEGER     NOT NULL,
            driverStatus            INTEGER     NOT NULL,
            resultStatus            INTEGER     NOT NULL,
            PRIMARY KEY (packetUID, vehicleID)
        );
    """
    CREATE_TABLE_LAPTIMES = """
        CREATE TABLE IF NOT EXISTS laptimes (
            packetUID               INTEGER     NOT NULL,
            vehicleID               INTEGER     NOT NULL,
            currentLapNum           INTEGER     NOT NULL,
            lastLapTime             FLOAT       NOT NULL,
            PRIMARY KEY (packetUID, vehicleID)
        );
    """
    CREATE_TABLE_TELEMETRY = """
        CREATE TABLE IF NOT EXISTS telemetry (
            packetUID INTEGER NOT NULL,
            vehicleID INTEGER NOT NULL,
            speed FLOAT NOT NULL,
            throttle FLOAT NOT NULL,
            brake FLOAT NOT NULL,
            clutch INTEGER NOT NULL,
            gear INTEGER NOT NULL,
            engineRPM FLOAT NOT NULL,
            drs INTEGER NOT NULL,
            revLightsPercent FLOAT NOT NULL,
            brakesTemperature INT_ARRAY NOT NULL,
            tyresSurfaceTemperature INT_ARRAY NOT NULL,
            tyresInnerTemperature INT_ARRAY NOT NULL,
            engineTemperature INT_ARRAY NOT NULL,
            tyresPressure FLOAT_ARRAY NOT NULL,
            surfaceType INT_ARRAY NOT NULL,
            PRIMARY KEY (packetUID, vehicleID)
        );
    """
    # CREATE STATEMENTS - Static tables
    CREATE_TABLE_DRIVERS = """
        CREATE TABLE IF NOT EXISTS drivers (
            driverId       INTEGER     PRIMARY KEY,
            firstname       VARCHAR     NOT NULL,
            lastname        VARCHAR     NOT NULL,
            displayname     CHAR(3)     NOT NULL 
        );
    """
    CREATE_TABLE_TRACKS = """
        CREATE TABLE IF NOT EXISTS tracks (
            trackId    INTEGER     PRIMARY KEY,
            trackname   VARCHAR     NOT NULL
        );
    """
    CREATE_TABLE_TEAMS = """
        CREATE TABLE IF NOT EXISTS teams (
            teamId     INTEGER     PRIMARY KEY,
            teamname    VARCHAR     NOT NULL
        );
    """
    CREATE_TABLE_PENALTIES = """
        CREATE TABLE IF NOT EXISTS penalties (
            penaltyId     INTEGER     PRIMARY KEY,
            description         VARCHAR     NOT NULL
        );
    """
    CREATE_TABLE_NATIONALITY = """
        CREATE TABLE IF NOT EXISTS nationality (
            nationalityId  INTEGER     PRIMARY KEY,
            nationality     VARCHAR     NOT NULL
        );
    """

    # INSERT STATEMENTS - Static tables
    INSERT_INTO_TEAMS = """
        INSERT OR IGNORE INTO teams (teamId, teamname) 
        VALUES (?, ?);
    """
    INSERT_INTO_DRIVERS = """
        INSERT OR IGNORE INTO drivers (driverId, firstname, lastname, displayname) 
        VALUES (?, ?, ?, ?);
    """
    INSERT_INTO_TRACKS = """
        INSERT OR IGNORE INTO tracks (trackId, trackname) 
        VALUES (?, ?);
    """
    INSERT_INTO_PENALTIES = """
        INSERT OR IGNORE INTO penalties (penaltyId, description) 
        VALUES (?, ?);
    """
    INSERT_INTO_NATIONALITY = """
        INSERT OR IGNORE INTO nationality (nationalityId, nationality) 
        VALUES (?, ?);
    """
    # INSERT STATEMENTS - Streamed tables
    INSERT_INTO_SESSION = """
        INSERT OR IGNORE INTO session (sessionSID, sessionUID, {})
        VALUES (?, ?, {})
    """ .format(*format_fields(EntryFields.SESSIONS))

    INSERT_INTO_PACKETS = """
        INSERT INTO packets (sessionSID, packetUID, {})
        VALUES (?, ?, {});
    """.format(*format_fields(EntryFields.PACKETS)) 

    INSERT_INTO_PARTICIPANTS = """
        INSERT OR IGNORE INTO participants (sessionSID, vehicleID, {}) 
        VALUES (?, ?, {});
    """.format(*format_fields(EntryFields.PARTICIPANTS))
    
    INSERT_INTO_LAPDATA = """
        INSERT INTO lapdata (packetUID, vehicleID, {}) 
        VALUES (?, ?, {});
    """.format(*format_fields(EntryFields.LAPDATA))

    INSERT_INTO_LAPTIMES = """
        INSERT INTO laptimes (packetUID, vehicleID, {}) 
        VALUES (?, ?, {});
    """.format(*format_fields(EntryFields.LAPTIMES))

    INSERT_INTO_TELEMETRY = """
        INSERT INTO telemetry (packetUID, vehicleID, {}) 
        VALUES (?, ?, {});
    """.format(*format_fields(EntryFields.TELEMETRY))
    
    # SELECT STATEMENTS
    PULL_SESSIONS = "SELECT sessionSID,sessionUID FROM session;"
    
    CHECK_TABLES = 'SELECT name FROM sqlite_master WHERE type= "table"'

def setup_sqlite_types():
    def adapt_float_array(array):
        return '{:.2f} {:.2f} {:.2f} {:.2f}'.format(*array).encode('ascii')

    def adapt_int_array(array):
        return '{:d} {:d} {:d} {:d}'.format(*array).encode('ascii')

    def convert_float_array(string):
        return list(map(float,string.split(b" ")))

    def convert_int_array(string):
        return list(map(int,string.split(b" ")))

    sqlite3.register_adapter(ctypes.c_uint8 * 4, adapt_int_array)
    sqlite3.register_adapter(ctypes.c_uint16 * 4, adapt_int_array)
    sqlite3.register_converter('int_array', convert_int_array)

    sqlite3.register_adapter(ctypes.c_float * 4, adapt_float_array)
    sqlite3.register_converter('float_array', convert_float_array)
    
def main():
    conn = SQLiteConnect()
    conn.open()
    conn.create_tables()
    conn.fill_static_tables()
    conn.close()


if __name__ == "__main__":
    main()
