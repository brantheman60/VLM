import pandas as pd
import numpy as np
import datetime as dt
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import pairwise_distances

df = None
number_cols = 'Price, Top Speed, Acceleration 0-100 Km / H, Engine Capacity'.split(', ')
date_cols = 'Introduction, End'.split(', ')
label_cols = 'Body Type, Transmission, Segment, Drive Wheel , Engine/motor Type, Fuel Type'.split(', ')
ordinal_cols = ['Energy Label']

def load_car_data():
    global df

    # Read CSV
    print('Reading CSV...')
    df = pd.read_csv('car_database/audi.csv', index_col=0, na_values='n/a')
    print('Done reading CSV...')

    # Keep the rows/columns we need
    needed_cols = ['image', 'url'] + number_cols + date_cols + label_cols + ordinal_cols
    df = df[needed_cols]
    df = df[~df.index.duplicated(keep='first')] # an efficient way to remove duplicate car names

    # Reformat the number columns
    df["Price"] = df["Price"].replace("[€,]", "", regex=True).astype(float)
    df["Top Speed"] = df["Top Speed"].replace("[km/h,]", "", regex=True).astype(float)
    df["Acceleration 0-100 Km / H"] = df["Acceleration 0-100 Km / H"].replace("[s,]", "", regex=True).astype(float)
    df["Engine Capacity"] = df["Engine Capacity"].replace("[cc,]", "", regex=True).astype(float)
    df["Engine Capacity"].fillna(0, inplace=True)

    # Reformat the date columns
    df["Introduction"] = pd.to_datetime(df["Introduction"], format='%B %Y')
    df["End"] = df["End"].replace("leverbaar", pd.Timestamp('today').strftime("%B %Y")) # current date
    df["End"] = pd.to_datetime(df["End"], format='%B %Y')
    
    # Reformat the label columns
    df["Segment"].fillna('Other', inplace=True)
    df["Fuel Type"].fillna('Electric only', inplace=True)
    df["Energy Label"].fillna('d', inplace=True)

    df.to_csv('car_database/audi_cleaned.csv')
    # print(df.dtypes)
    # print(df.isna().sum())
    # print(df.shape)

    return df

def models_to_trims(model_name):
    matching_trims = []
    for trims in df.index:
        if model_name in trims:
            matching_trims.append(trims)
    
    if len(matching_trims) != 0:
        return matching_trims
    else: # e.g. "I don't know" -> return all trims
        return df.index.tolist()


def get_distance_metrics(df1, df2):
    # categorical variables
    df1_ = df1[label_cols]
    df2_ = df2[label_cols]
    categorical = pairwise_distances(df1_, df2_, metric='hamming')

    # ordinal variables
    df1_ = df1[ordinal_cols]
    df2_ = df2[ordinal_cols]
    ordinal = pairwise_distances(df1_, df2_, metric='manhattan')

    # numerical variables
    df1_ = df1[number_cols]
    df2_ = df2[number_cols]
    numerical = pairwise_distances(df1_, df2_, metric='euclidean')
    
    # simple weighted sum
    scores = categorical * 0.5 + ordinal * 0.3 + numerical * 0.2
    return scores

def find_newest_trims(trims, percentile):
    df_ = df[df.index.isin(trims)]
    df_ = df_.sort_values(by=['End'])
    n = int(len(df_) * percentile) + 1 # prevent n=0
    df_ = df_.iloc[-n:]
    return df_.index.tolist()

def best_car_matches(K, interest, compare):
    # Step 1: Find the trims of the interest and compare models
    interest_trims = models_to_trims(model_name=interest)
    compare_trims = models_to_trims(model_name=compare)

    # Step 2: Find the 25% of newest trims to use (older trims are less relevant)
    interest_trims = find_newest_trims(interest_trims, 0.25)
    compare_trims = find_newest_trims(compare_trims, 0.25)
    
    # Step 3: Prepare the dataframe again for distance metrics
    # convert categorical and ordinal columns to numbers
    df_converted = df.copy()
    enc = OrdinalEncoder()
    df_converted[label_cols] = enc.fit_transform(df_converted[label_cols])
    df_converted[ordinal_cols] = enc.fit_transform(df_converted[ordinal_cols])

    # Step 4: find the distances between each interest trim and compare trim
    df1 = df_converted.loc[interest_trims]
    df2 = df_converted.loc[compare_trims]
    scores = get_distance_metrics(df1, df2) # len(df1) x len(df2)

    # Step 5: find the K most similar trims (lowest distance)
    trim_scores = scores.sum(axis=1)
    best_trims = trim_scores.argsort()[:K]
    best_trims = np.take(interest_trims, best_trims)
    return best_trims

if __name__ == '__main__':
    load_car_data()
    best_trims = best_car_matches(5, 'Audi A6', 'Audi Q3')
    print(best_trims)