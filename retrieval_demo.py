#! /usr/bin/env python3

"""
Demo of how to retrieve data from the SQLite database.
"""

################################################
# Load Dependencies

import sqlite3
import numpy as np
import pandas as pd

from f1_2020_db import setup_sqlite_types

################################################
# Scripting

setup_sqlite_types()

# Connect, if not connected
filename = "f1-2020.sqlite3"
if 'conn' not in locals():
    conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    print(f'Connected to {filename}')

# Set query to grab session info
get_sessions = """
    SELECT *
    FROM session;
"""

# Execute query
res = conn.execute(get_sessions)
columns = list(zip(*res.description))[0]
data = res.fetchall()

# Enter results into pandas DataFrame
sessions = pd.DataFrame(data=data, columns=columns)
print(sessions)

# Get most recent session SID
last_session = sessions.iloc[-1]['sessionSID']

###

get_player_traces = """
    SELECT {columns} 
    FROM packets p
    INNER JOIN lapdata d 
    ON p.packetUID=d.packetUID
    WHERE p.sessionSID == {sessionSID};
"""


res = conn.execute("select * from session")
columns = list(zip(*res.description))[0]
data = res.fetchone()

sessions = []
while True:
    data = res.fetchone()
    if data != None:
        sessions.append(Session(conn, data, columns))
    else:
        break

for i,s in enumerate(sessions):
    print(f'{i:<12}', s.info)

query = """

"""