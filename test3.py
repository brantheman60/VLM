import sqlite3
from utils import *
from SALES_ID import *

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