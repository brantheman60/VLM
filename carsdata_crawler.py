import pandas as pd
import os
import requests
import re
import argparse
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_soup(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

# Get links to all models
def step1(url):
    soup = get_soup(url)
    links = []
    for div in soup.find_all('div', {'class': 'col-4'}):
        for link in div.find_all('a', href=True):
            href = link['href']
            if url in href:
                links.append(href)
    return links

# Get links to all sub-models
def step2(urls):
    links = []
    for link in tqdm(urls):
        soup = get_soup(link)
        for div in soup.find_all('div', {'class': 'col-4'}):
            for link in div.find_all('a', href=True):
                href = link['href']
                if 'https://' in href:
                    links.append(href)
    return links

# Get links to all trims
def step3(urls):
    links = []

    # Each trim has a set of years
    years = []
    for link in tqdm(urls):
        soup = get_soup(link)
        for a in soup.find_all('a', {'class': 'typesallyears'}, href=True):
            years.append(a['href'])

    for link in tqdm(years):
        soup = get_soup(link)
        for div in soup.find_all('h3'):
            for link in div.find_all('a', href=True):
                href = link['href']
                links.append(href + '/tech')
    return links

# Get specs for each trim
def step4(urls):
    all_trims = []
    all_dicts = []

    for link in tqdm(urls):
        soup = get_soup(link)
        
        # Find trim
        trim = soup.find_all('span', {'itemprop': 'name'})[-1].get_text()

        # Find specs
        specs = []
        for td in soup.find_all('td', {'class': 'col-6'}):
            specs.append(td.get_text())
        keys = specs[::2]
        keys = [k[:-1] for k in keys] # remove ':'
        vals = specs[1::2]
        specs = dict(zip(keys, vals))

        # Find images
        img = soup.find('source', {'type': 'image/jpg'})
        specs['image'] = 'https://www.cars-data.com' + img['srcset']
        specs['url'] = link[:-5]

        all_trims.append(trim)
        all_dicts.append(specs)
        
    
    return all_trims, all_dicts

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str, help='Name of car make')
    parser.add_argument('-c', '--cores', type=int, default=1, help='Number of cores')
    args = parser.parse_args()

    make = args.m
    URL = 'https://www.cars-data.com/en/' + make.lower()
    if make is None:
        raise ValueError('Must specify make')
    if requests.get(URL).status_code != 200:
        raise ValueError('URL does not exist')

    links1 = step1(URL)
    links2 = step2(links1)
    links3 = step3(links2)
    all_trims, all_dicts = step4(links3)

    # Write to file
    df = pd.DataFrame(all_dicts, index=all_trims)
    df.to_csv(f'car_database/{make}.csv')