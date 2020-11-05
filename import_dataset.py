# Importing Dataset
import json, requests
import pandas as pd
from datetime import date
import os
from os import path


today = date.today()


# ----------------------------------------------------------------------------
# Download JSON File
url_json = "https://covid.ourworldindata.org/data/owid-covid-data.json"
json_dump_path = 'Datasets/covid_{}.json'.format(today)

def download_json():
    """
    This function will download a json file from a link above.
    Output: a .json file where requests in dumped.
    """
    r = requests.get(url_json)
    json_data = r.json()
    with open(json_dump_path, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)


# ----------------------------------------------------------------------------
# Clean JSON Export Pandas
def split_json_to_dfs(filename):
    """
    Input: .json file containing full information
    Output:
    country_information---information of each countries. This is the first layer of the json file dictionary
    country_key---dataframe containing dictionary. For example: ['AFG'] ['Afganistan']
    combined_df---daily records of covid
    """
    read_df = pd.read_json(filename)
    ### Dataframe #1
    country_information = read_df.T.drop('data', 1).reset_index()
    ### Dataframe #2
    country_key = country_information[['index', 'location', 'continent']]
    ### Datafrane #3
    covid_cases = read_df.T['data']
    combined_df = pd.DataFrame()
    for country in list(covid_cases.keys()):
        new_df = pd.DataFrame.from_dict(covid_cases[country], orient='columns')
        new_df['country_code'] = country
        combined_df = combined_df.append(new_df)

    combined_df['date']= pd.to_datetime(combined_df['date'])
    
    return country_information, country_key, combined_df
