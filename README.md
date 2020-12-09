# F1 2020 Telemetry Recorder

[![Python version](https://img.shields.io/badge/python-3.8-blue?style=flat-square)]()

The f1-2020-db package allows users to capture, unpack and save telemetry broadcast by the F1 2020 videogame to an SQLite database. It is designed with post-race analysis in mind, with a database structure that allows specific data to be queried within or across sessions.



Much of the code for parsing the packets has been adapted from the excellent package, [f1-2020-telemetry](https://gitlab.com/gparent/f1-2020-telemetry), written by Guillaume Parent, to whom I owe my thanks.



This package is a work in progress and was meant as a good excuse to learn some SQL. Therefore it is not guaranteed to be supported in the future.



[TOC]


---

## Usage



### Recording data


### Retrieving data

The data can be accessed using standard SQL queries, or at least those supported by [SQLite](https://sqlite.org/lang.html).


---

## Dependencies

**Recording**
- f1-2020-telemetry
- pandas
- numpy

**Plotting**
- matplotlib
- scipy (for interpolation)

---

## Database schema

Below is the proposed schema for the sqlite database. In brief, there are three primary tables through which all other tables can be linked:

**sessions:** One entry for each session recorded (practice/quali/race etc).
**packets:** One entry for each packet processed by the record.
**participants:** 22 entries for each session, listing the participants in the session.

From this, two fields are predominantly used as the joint primary keys, identifying a single driver for a single frame.

**packetUID:** Unique packet identifer, which is unique for a given session.
**vehicleId:** The unique vehicle identifier (0-21), which is consistent across all packets for a given session. They are not consistent across different sessions.


![](./img/F1-db-schema.svg)


The proposed schema is not yet fully implemented in the package. However, some of key tables (primary tables, lapdata & cartelemetry) are.

---

## Other

```python
def function(inp):
    """Docstring"""
    
    for i in range(inp):
        print(i)
```

[Writing python packages](https://code.tutsplus.com/tutorials/how-to-write-package-and-distribute-a-library-in-python--cms-28693)