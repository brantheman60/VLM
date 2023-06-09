import pandas as pd
import sqlite3

client = {'age': 25, 'male': True, 'race': 'asian', 'emotion': 'neutral', 'name': 'Brandon',
          'new': True, 'interest': 'Honda Civic', 'similar': "I don't know", 'current': 'Honda Civic'}

# This is the types and order of the data in the database
CLIENT_KEYS = {'name': 'TEXT', 'age': 'INTEGER', 'male': 'BOOLEAN',
               'race': 'TEXT', 'emotion': 'TEXT', 'new': 'BOOLEAN',
               'interest': 'TEXT', 'similar': 'TEXT', 'current': 'TEXT'}
values = [client[key] for key in CLIENT_KEYS.keys()]
values = [v.replace("'", "''") if type(v) == str else v for v in values] # add escape characters
keys_types = [f'{k} {v}' for k, v in zip(CLIENT_KEYS.keys(), CLIENT_KEYS.values())]

con = sqlite3.connect('clients.db') # create a connection to database
cur = con.cursor() # create a cursor to execute SQL commands

string = "CREATE TABLE IF NOT EXISTS clients({});".format(', '.join(keys_types))
cur.execute(string)
string = "INSERT INTO clients VALUES ('{}', {}, {}, '{}', '{}', {}, '{}', '{}', '{}');".format(*values)
cur.execute(string)
# res = cur.execute("PRAGMA table_info(clients);").fetchall()
# print(res)
res = cur.execute("SELECT * FROM clients").fetchall()
for r in res:
    print(r)

con.commit()