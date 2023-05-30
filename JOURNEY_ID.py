# databases taken from:
# - https://www.teoalida.com/cardatabase/
# - https://www.fueleconomy.gov/feg/ws/index.shtml

import pandas as pd

# import the vehicle data, and get the following important metrics
df = pd.read_csv('car_database/vehicles.csv')
df = df[['year', 'createdOn', 'modifiedOn', 'drive', 'cylinders', 'make', 'model', 'VClass',
         'highway08', 'highwayA08', 'city08', 'cityA08', 'fuelType', 'trany',
         'hlv', 'hpv', 'lv2', 'lv4', 'pv2', 'pv4']]
print(df.head(10))
for i in range(10):
    row = df.iloc[i]
    print(row['year'], row['make'], row['model'])