#! /usr/bin/env python3

from enum import IntEnum, auto, unique

@unique
class TableID(IntEnum):
    """Lookup table for database table IDs """
    
    PACKETS = 00
    SESSION = 10
    WEATHER = 11
    MARSHALS = 12
    LAPDATA = 20
    PARTICIPANTS = 40
    TELEMETRY = 60

SessionType = {
    0: 'unknown',
    1: 'Practice 1',
    2: 'Practice 2',
    3: 'Practice 3',
    4: 'Short Practice',
    5: 'Qualy 1',
    6: 'Qualy 2',
    7: 'Qualy 3',
    8: 'Short Qualy',
    9: 'One Shot Qualy',
    10: 'Race',
    11: 'Race 2',
    12: 'Time Trial'
}
    
    
    
# Drivers
DriverIDs = {
    0: ("Carlos Sainz", "SAI"),
    1: ("Daniil Kvyat", "KVY"),
    2: ("Daniel Ricciardo", "RIC"),
    6: ("Kimi Räikkönen", "RAI"),
    7: ("Lewis Hamilton", "HAM"),
    9: ("Max Verstappen", "VER"),
    10: ("Nico Hulkenberg", "HUL"),
    11: ("Kevin Magnussen", "MAG"),
    12: ("Romain Grosjean", "GRO"),
    13: ("Sebastian Vettel", "VET"),
    14: ("Sergio Perez", "PER"),
    15: ("Valtteri Bottas", "BOT"),
    17: ("Esteban Ocon", "OCO"),
    19: ("Lance Stroll", "STR"),
    20: ("Arron Barnes", "BAR"),
    21: ("Martin Giles", "GIL"),
    22: ("Alex Murray", "MUR"),
    23: ("Lucas Roth", "ROT"),
    24: ("Igor Correia", "COR"),
    25: ("Sophie Levasseur", "LEV"),
    26: ("Jonas Schiffer", "SCH"),
    27: ("Alain Forest", "FOR"),
    28: ("Jay Letourneau", "LET"),
    29: ("Esto Saari", "SAA"),
    30: ("Yasar Atiyeh", "ATI"),
    31: ("Callisto Calabresi", "CAL"),
    32: ("Naota Izum", "IZU"),
    33: ("Howard Clarke", "CLA"),
    34: ("Wilhelm Kaufmann", "KAU"),
    35: ("Marie Laursen", "LAU"),
    36: ("Flavio Nieves", "NIE"),
    37: ("Peter Belousov", "BEL"),
    38: ("Klimek Michalski", "MIC"),
    39: ("Santiago Moreno", "MOR"),
    40: ("Benjamin Coppens", "COP"),
    41: ("Noah Visser", "VIS"),
    42: ("Gert Waldmuller", "WAL"),
    43: ("Julian Quesada", "QUE"),
    44: ("Daniel Jones", "JON"),
    45: ("Artem Markelov", "MAR"),
    46: ("Tadasuke Makino", "MAK"),
    47: ("Sean Gelael", "GEL"),
    48: ("Nyck De Vries", "VRI"),
    49: ("Jack Aitken", "AIT"),
    50: ("George Russell", "RUS"),
    51: ("Maximilian Günther", "GUN"),
    52: ("Nirei Fukuzumi", "FUK"),
    53: ("Luca Ghiotto", "GHI"),
    54: ("Lando Norris", "NOR"),
    55: ("Sérgio Sette Câmara", "CAM"),
    56: ("Louis Delétraz", "DEL"),
    57: ("Antonio Fuoco", "FUO"),
    58: ("Charles Leclerc", "LEC"),
    59: ("Pierre Gasly", "GAS"),
    62: ("Alexander Albon", "ALB"),
    63: ("Nicholas Latifi", "LAT"),
    64: ("Dorian Boccolacci", "BOC"),
    65: ("Niko Kari", "KAR"),
    66: ("Roberto Merhi", "MER"),
    67: ("Arjun Maini", "MAI"),
    68: ("Alessio Lorandi", "LOR"),
    69: ("Ruben Meijer", "MEI"),
    70: ("Rashid Nair", "NAI"),
    71: ("Jack Tremblay", "TRE"),
    74: ("Antonio Giovinazzi", "GIO"),
    75: ("Robert Kubica", "KUB"),
    78: ("Nobuharu Matsushita", "MAT"),
    79: ("Nikita Mazepin", "MAZ"),
    80: ("Guanyu Zhou", "ZHO"),
    81: ("Mick Schumacher", "SCH"),
    82: ("Callum Ilott", "ILO"),
    83: ("Juan Manuel Correa", "COR"),
    84: ("Jordan King", "KIN"),
    85: ("Mahaveer Raghunathan", "RAG"),
    86: ("Tatiana Calderón", "CAL"),
    87: ("Anthoine Hubert", "HUB"),
    88: ("Giuliano Alesi", "ALE"),
    89: ("Ralph Boschung", "BOS"),
}