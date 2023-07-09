# INSTEAD OF CARS-DATA.COM, USE AUTOBYTEL.COM!!!

import pandas as pd
import os
import requests
import re
import argparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

HOME = 'https://www.autobytel.com'
KEYS = ['Number of speeds', 'Horse Power', 'Fuel tank capacity', 'City', 'Highway',
        'Total Seating Capacity', 'Recommended fuel',
        'Overall height', 'Overall Length', 'Overall Width', 'Wheelbase']
UNITS = ['', ' hp', 'gal.', ' mpg', ' mpg', '', '', ' "', ' "', ' "', ' "']


def get_soup(url):
    page = requests.get(url)
    if page.status_code != 200:
        print('Error opening', url)
        return None
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

# save results from each step into file
def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)
def save_step(step, data):
    save_data(f'car_database/step{step}.json', data)


def load_data(file):
    if not os.path.exists(file):
        return None
    with open(file, 'r') as f:
        return json.load(f)
def load_step(step):
    return load_data(f'car_database/step{step}.json')

# Get links to all models
def step1(url):
    links1 = load_step(1)
    if links1 is not None:
        return links1
    
    soup = get_soup(url)
    links = []
    for div in soup.find_all('div', class_='col1of2-vertical general-list disc clearfix'):
        for li in div.find_all('li'):
            for link in li.find_all('a', href=True):
                links.append(HOME + link['href'])

    links = [*set(links)] # remove duplicates
    save_step(1, links)
    return links

# Get links to all years
def step2(urls):
    links2 = load_step(2)
    if links2 is not None:
        return links2
    
    links = []
    for link in tqdm(urls):
        soup = get_soup(link)
        for div in soup.find_all('div', class_='grid-2-5'):
            for li in div.find_all('li'):
                for link in li.find_all('a', href=True):
                    links.append(HOME + link['href'])
    
    save_step(2, links)
    return links

# Get links to all trims
def step3(urls):
    links3 = load_step(3)
    if links3 is not None:
        return links3
    links = []

    for link in tqdm(urls):
        soup = get_soup(link + 'prices')
        table = soup.find('table', class_='table-small')
        tbody = table.find('tbody')
        for tr in tbody.find_all('tr'):
            for link in tr.find_all('a', href=True):
                links.append(HOME + link['href'])
    
    save_step(3, links)
    return links


def get_car_feature(soup, key, unit=''):
    try:
        span = soup.find('span', class_='x-smaller uppercase', string=re.compile(f'^{key}:\s*'))
        val = span.find_next_sibling().get_text()
        if len(unit) > 0:
            val = val[:-len(unit)]
        return val
    except:
        return None

# Get specs for each trim
def step4(urls):
    all_trims = []
    all_dicts = []
    failures = []

    for link in tqdm(urls):

        trim_dict = dict()

        # Go to overview page to get pic and MSRP
        soup = get_soup(link)
        if soup is None:
            failures.append(link)
            continue
        trim_dict['img'] = soup.find('img', {'name': 'NewCarDetailPhoto'})['src'][2:].replace(',', '')
        trim_dict['msrp'] = soup.find('div', class_='data-table vdp-data-table') \
                                .find('div', class_='data-value').get_text()[1:]

        # Go to specs page
        soup = get_soup(link + 'specifications')
        if soup is None:
            failures.append(link)
            continue
        
        # Find trim and model
        a = soup.find('div', class_='shade clearfix').find_all('a', href=True)
        trim = a[-1]['title']
        trim_dict['model'] = a[-2]['title']

        # Find specs
        vals = []
        for key, unit in zip(KEYS, UNITS):
            vals.append(get_car_feature(soup, key, unit))
        specs = dict(zip(KEYS, vals))
        trim_dict.update(specs)

        all_trims.append(trim)
        all_dicts.append(trim_dict)
    
    return all_trims, all_dicts, failures

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str, help='Name of car make')
    parser.add_argument('-c', '--cores', type=int, default=1, help='Number of cores')
    args = parser.parse_args()

    make = args.m
    if make is None:
        raise ValueError('Must specify make')
    URL = f'{HOME}/' + make.lower()

    links1 = step1(URL)
    links2 = step2(links1) # links2 = ['https://www.autobytel.com/porsche/718-boxster/2023/', 'https://www.autobytel.com/porsche/718-boxster/2022/']
    links3 = step3(links2)
    all_trims, all_dicts, failures = step4(links3)

    # Write to file
    df = pd.DataFrame(all_dicts, index=all_trims)
    df.to_csv(f'car_database/{make}.csv')

    # Write failures to file
    save_data('car_database/failures.json', failures)