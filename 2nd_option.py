# 1st stage - importing data

import requests
import pandas as pd 
import json
import time
from coinbase.wallet.client import Client

start = time.time()     # Starting time for measurement purposes


response1 = requests.get("https://restcountries.eu/rest/v2/region/europe?fields=name;nativeName;alpha2Code;alpha3Code;latlng;population;area;capital;languages;topLevelDomain;timezones;regionalBlocs;currencies")

print(f"Status code is: {response1.status_code}")  # Printing status code

eu_json = response1.json()

df = pd.read_json(json.dumps(eu_json))      # df as a DataFrame from JSON type data


# 2nd stage - time for rearranging the df

cols =["name","nativeName","alpha2Code","alpha3Code","latlng","population","area","capital","languages","topLevelDomain","timezones","regionalBlocs","currencies"]
df = df[cols]       # Changing order of the columns

# 3rd stage - defining some useful functions

print("Organizing data...")

def languages_correct(x):       # Function which transforms "languages" data into more lucid data
    whole_str=""
    for lng in x:
        if len(x) <2:
            lng_name= lng["name"]
            whole_str = whole_str + str(f"{lng_name}, ")
        else:
            lng_name = lng["name"]
            whole_str = whole_str + str(f"{lng_name}, ")
    return whole_str[:-2]
    
df["languages"] = df["languages"].apply(languages_correct)      # Applying the function for the df column




from math import sin, cos, sqrt, atan2, radians


def distance_pl(latlon):    # Function which calculates distance between some country and Poland
    
    R = 6373.0

    lat1 = radians(52.0)    # latitiude of Poland
    lon1 = radians(20.0)        # Lenght of Poland 
    lat2 = radians(latlon[0])   # Latitiude of x Country
    lon2 = radians(latlon[1])   #Lenght of x Country

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return round(distance,3)    # Returns distance in km between two points

df["Distance from PL in km"] = df["latlng"].apply(distance_pl)  # Applying the function for the df column




def in_eu(x):       # Function which returns if the Country is in EU or not
    if len(x)==1:
        if x[0]["acronym"]=="EU":
            return True
        else:
            return False
    else:
        return False
df["regionalBlocs"] = df["regionalBlocs"].apply(in_eu)      # Applying the function for the df column
df = df.rename(columns={"regionalBlocs":"Is the country in EU?"})       # Changing the name of the column ( just for a better look :) )




def domain_correct(x):      # Function which clears output of the domain of the country
    if len(x)>0:
        return x[0]
    else:
        return ""
df["topLevelDomain"] = df["topLevelDomain"].apply(domain_correct)       # Applying the function for the df column
df = df.rename(columns={"topLevelDomain":"Country web domain"})       # Changing the name of the column ( just for a better look :) )





def currencies_name(x):         # Function which clarifies the currency data of the country
    return x[0]["name"]
def currencies_symbol(x):
    if "symbol" in x[0]:
        return x[0]["symbol"]
    else:
        return ""

df["currencies_symbol"] = df["currencies"].apply(currencies_symbol)       # Applying the function for the df column
df["currencies_name"] = df["currencies"].apply(currencies_name)       # Applying the function for the df column

print("Uploading exchange rates...")

def convert_to_pln(x):       # Function which uses given API to convert given currency to PLN
    client = Client("https://api.coinbase.com/v2/exchange-rates",api_secret="PLN")

    to_PLN = client.get_exchange_rates(currency=x[0]["code"])
    return round(float(to_PLN["rates"]["PLN"]),2)

df["To PLN"] = df["currencies"].apply(convert_to_pln)       # Applying the function for the df column
del df["currencies"]       # Deleting currencies column (we don't need it anymore)




import datetime

df["time of extraction"] = datetime.datetime.now()      # Making a column which contains current time of data extraction

#4th stage - creating a csv file

df.to_csv("raport2.csv")      # Finally making a csv file raport_eu.csv

end = time.time()       # Ending time for measurement purposes

print(f"Done! It took me {round(end-start,2)} seconds")     # Printing duration of the function