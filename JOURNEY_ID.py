# Note: http://www.cars-data.com was crawled to generate the car models
# Note: switching over to https://www.autobytel.com
# Other useful databases to consider (which don't require web scraping) are:
# - https://www.teoalida.com/cardatabase/
# - https://www.fueleconomy.gov/feg/ws/index.shtml

import pandas as pd
import numpy as np
import datetime as dt
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import pairwise_distances

import carsdata_crawler2 as crawler

NUM_FEATURES = ['msrp', 'Number of speeds', 'Horse Power', 'Fuel tank capacity', 'City', 'Highway', 'Total Seating Capacity', 'Overall height', 'Overall Length', 'Overall Width', 'Wheelbase']
CAT_FEATURES = ['Recommended fuel']
OTHER_FEATURES = ['img', 'model']
with open('car_database/all_makes.txt', 'r') as f:
    MAKES = f.read().split('\n')

def get_make(string):
    for make in MAKES:
        if make.lower() in string.lower():
            return make.lower()

def load_car_data(make):
    # Read CSV
    print('Reading CSV...')
    df = pd.read_csv(f'car_database/{make}.csv', index_col=0, na_values='n/a')
    print('Done reading CSV...')

    # Keep the rows/columns we need
    df = df[NUM_FEATURES + CAT_FEATURES + OTHER_FEATURES]

    # If fuel tank capacity is empty, then an electric car; fill with 0
    df['Fuel tank capacity'].fillna(0, inplace=True)

    # Drop rows that lack all info
    df.dropna(inplace=True)

    # Reformat the number columns
    df['msrp'] = df['msrp'].replace(',', '', regex=True).astype(float)
    df['Number of speeds'] = df['Number of speeds'].replace('Continuously variable', '0').astype(float)
    df['Wheelbase'] = df['Wheelbase'].astype(float)

    # extract year from model
    df['year'] = df['model'].str.extract(r'(\d{4})')

    # Turn categorical variables into numbers
    enc = OrdinalEncoder()
    df[CAT_FEATURES] = enc.fit_transform(df[CAT_FEATURES])

    df.to_csv(f'car_database/{make}_cleaned.csv')
    # print(df.dtypes)
    # print(df.isna().sum())
    # print(df.shape)

    return df

def string_to_trims(df, string_name):
    # Find all trims that contain the string's key words
    matching_trims = []
    string_words = string_name.lower().split()
    for trim in df.index:
        trim_words = trim.lower().split()
        if all(word in trim_words for word in string_words):
            matching_trims.append(trim)
    
    if len(matching_trims) != 0:
        return matching_trims
    else: # e.g. "I don't know" -> return all trims
        return df.index.tolist()


def get_distance_metrics(df1, df2):
    # categorical variables
    df1_ = df1[CAT_FEATURES]
    df2_ = df2[CAT_FEATURES]
    categorical = pairwise_distances(df1_, df2_, metric='hamming')

    # numerical variables
    df1_ = df1[NUM_FEATURES]
    df2_ = df2[NUM_FEATURES]
    numerical = pairwise_distances(df1_, df2_, metric='euclidean')
    
    # simple weighted sum
    scores = categorical * 0.5 + numerical * 0.5
    return scores

# def find_newest_trims(trims, percentile):
#     df_ = df[df.index.isin(trims)]
#     df_ = df_.sort_values(by=['End'])
#     n = int(len(df_) * percentile) + 1 # prevent n=0
#     df_ = df_.iloc[-n:]
#     return df_.index.tolist()

def best_car_matches(K, interest, compare):
    # Step 0: minor cleaning of interest and compare names
    # so far, so good...
    
    # Step 1: find the makes of the interest and compare
    make1_df = load_car_data(get_make(interest))
    make2_df = load_car_data(get_make(compare))

    # Step 2: Find the trims of the interest and compare models
    interest_trims = string_to_trims(make1_df, interest)
    compare_trims  = string_to_trims(make2_df, compare)

    # print(interest_trims)
    # print(compare_trims)

    # Step 2: Find the 25% of newest trims to use (older trims are less relevant)
    # interest_trims = find_newest_trims(interest_trims, 0.25)
    # compare_trims = find_newest_trims(compare_trims, 0.25)
    
    # Step 3: Prepare the dataframe again for distance metrics
    # convert categorical and ordinal columns to numbers

    # Step 4: find the distances between each interest trim and compare trim
    trim1_df = make1_df.loc[interest_trims]
    trim2_df = make2_df.loc[compare_trims]
    scores = get_distance_metrics(trim1_df, trim2_df) # len(df1) x len(df2)

    # Step 5: find the K most similar trims (lowest distance)
    trim_scores = scores.sum(axis=1)
    best_trims = trim_scores.argsort()[:K]
    best_trims = np.take(interest_trims, best_trims)
    return best_trims

if __name__ == '__main__':
    best_trims = best_car_matches(5, 'Audi e-tron GT', 'Porsche Taycan GTS')
    print(best_trims)