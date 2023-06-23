import numpy
from utils import *

# NEED TO CONVERT FROM ARRAY TO KEY INDEX!!!

def best_sales_rep(con, client_id):
    sales = get_table(con, 'sales')
    client = get_table_entry(con, 'clients', client_id)

    # Calculate distances
    metrics = ['age', 'male', 'race', 'quality', 'exp']
    scores = []
    for sale in sales:
        score = 0
        score += 20 / (abs(client['age'] - sale['age']) + 1)
        score += 30 if client['male'] == sale['male'] else 0
        score += 10 if client['race'] == sale['race'] else 0
        score += sale['quality']

        scores.append(score)
    
    # Find best sales rep
    print(scores)
    best_sales_rep = sales[numpy.argmax(scores)]
    return best_sales_rep