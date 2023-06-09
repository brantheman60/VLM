import numpy
from utils import *

# NEED TO CONVERT FROM ARRAY TO KEY INDEX!!!

def best_sales_rep():
    con = get_database_connection()
    
    sales = get_table(con, 'sales')
    clients = get_table(con, 'clients')
    last_client = clients[-1]

    # Calculate distances
    metrics = ['age', 'male', 'race', 'quality']
    distances = []
    for sale in sales:
        dist = 0
        dist += (last_client['age'] - sale['age'])**2 # age difference
        dist += 30 if last_client['male'] != sale['male'] else 0
        dist += 10 if last_client['race'] != sale['race'] else 0
        dist += 1 / sale['quality']**2

        distances.append(dist)
    
    # Find best sales rep
    print(distances)
    best_sales_rep = sales[numpy.argmin(distances)]
    return best_sales_rep