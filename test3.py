import sqlite3
from utils import *
from SALES_ID import *

CLIENT1 = {'name': 'Henry',
          'age': 60,
          'male': True,
          'race': 'white',
          'emotion': 'angry',
          'new': True,
          'interest': "I don't know",
          'compare': "Range Rover",
          'current': '2016 Ford Focus'}

CLIENT2 = {'name': 'Vanessa',
          'age': 16,
          'male': False,
          'race': 'latino',
          'emotion': 'happy',
          'new': True,
          'interest': 'Audi A6',
          'compare': "Audi Q3",
          'current': 'Honda Civic'}

SALES1  = {'name': 'Markus',
           'age': 35,
           'male': True,
           'race': 'latino',
           'quality': 9.5}

SALES2  = {'name': 'Terrance',
           'age': 41,
           'male': True,
           'race': 'white',
           'quality': 7.2}

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = get_database_connection()

insert_table_entry(con, 'clients', CLIENT1)
insert_table_entry(con, 'clients', CLIENT2)
insert_table_entry(con, 'sales', SALES1)
insert_table_entry(con, 'sales', SALES2)

view_table(con, 'clients')
view_table(con, 'sales')

rep = best_sales_rep()
print(rep)