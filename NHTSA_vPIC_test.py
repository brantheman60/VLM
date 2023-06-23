import requests
import json

def get_results(url):
    r = requests.get('https://vpic.nhtsa.dot.gov/api' + url)
    return r.json()['Results']

def post_results(url, post_fields):
    r = requests.post('https://vpic.nhtsa.dot.gov/api' + url, data=post_fields)
    return r.json()['Results']

def get_make_id(make_str):
    # Get all car makes (NOT models), e.g. 'Toyota', 'Honda', etc.
    url = '/vehicles/GetAllMakes?format=json'
    makes = get_results(url)
    for m in makes:
        if m['Make_Name'].casefold() == make_str.casefold():
            return m['Make_ID']
    return None

def get_models(make_id):
    # Get all car models for a given make, e.g. 'Camry', 'Accord', etc.
    url = f'/vehicles/GetModelsForMakeId/{make_id}?format=json'
    models = get_results(url)
    
    # Only return the model ids and names
    for m in models:
        del m['Make_ID']
        del m['Make_Name']
    return models

def get_wmis(manufacturer_str):
    # Get all WMIs for a given manufacturer, e.g. 'Toyota', 'Honda', etc.
    url = f'/vehicles/GetWMIsForManufacturer/{manufacturer_str}?format=json'
    wmis = get_results(url)

    # Only return the WMI ids and names (and vehicle types)
    for w in wmis:
        del w['Id']
        del w['Country']
        del w['CreatedOn']
        del w['DateAvailableToPublic']
        del w['UpdatedOn']
    return wmis

AUDI_ID = get_make_id('Audi') # 582
HONDA_ID = get_make_id('Honda') # 474

AUDI_WMIS = get_wmis('audi') # 'WAU', 'WA1', etc.

# Get all car models for a given make, e.g. 'Camry', 'Accord', etc.
# audi_models = get_models(AUDI_ID)
# print(audi_models)

url = '/vehicles/DecodeVINValuesBatch/'
post_fields = {'format': 'json', 'data':'WAU*'}
r = post_results(url, post_fields)
print(r)