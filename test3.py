import sqlite3
from utils import *
from SALES_ID import *

CLIENT1 = {'name': 'Adam',
           'age': 60,
           'male': True,
           'race': 'white',
           'emotion': 'angry',
           'new': True,
           'interest': "I don't know",
           'compare': "Range Rover",
           'current': '2016 Ford Focus'}

CLIENT2 = {'name': 'Brenda',
           'age': 16,
           'male': False,
           'race': 'latino',
           'emotion': 'happy',
           'new': True,
           'interest': 'Audi A6',
           'compare': "Audi Q3",
           'current': 'Honda Civic'}

CLIENT3 = {'name': 'Cameron',
           'age': 25,
           'male': True,
           'race': 'black',
           'emotion': 'sad',
           'new': False,
           'interest': 'Audi A1',
           'compare': "Audi A4",
           'current': "I don't drive"}

SALES1  = {'name': 'Xavier',
           'age': 35,
           'male': True,
           'race': 'latino',
           'quality': 9.5}

SALES2  = {'name': 'Yolanda',
           'age': 41,
           'male': False,
           'race': 'white',
           'quality': 7.2}

SALES3  = {'name': 'Zachary',
           'age': 27,
           'male': True,
           'race': 'black',
           'quality': 6.6}

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = get_database_connection()

# Start brand new
drop_table(con, 'clients')
drop_table(con, 'sales')

# Add sample clients and sales reps
insert_table_entry(con, 'clients', CLIENT1)
insert_table_entry(con, 'clients', CLIENT2)
insert_table_entry(con, 'clients', CLIENT3)
insert_table_entry(con, 'sales', SALES1)
insert_table_entry(con, 'sales', SALES2)
insert_table_entry(con, 'sales', SALES3)

view_table(con, 'clients')
view_table(con, 'sales')

# Find the best sales rep for 3rd client
rep = best_sales_rep(con, 3)
print('Best sales rep: ', rep['name'])
print(rep)