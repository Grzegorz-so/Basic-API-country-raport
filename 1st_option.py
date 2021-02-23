# 1st stage - importing libraries and data

import requests
import pandas as pd 
import datetime
import time

start = time.time()     # Starting time of the program for measurement purposes

response1 = requests.get("https://restcountries.eu/rest/v2/region/europe?fields=name;nativeName;alpha2Code;alpha3Code;latlng;population;area;capital;languages;topLevelDomain;timezones;regionalBlocs;currencies")

print(f"Status code is: {response1.status_code}")

eu_json = response1.json()

from math import sin, cos, sqrt, atan2, radians


def distance_pl(latlon):    # Function which calculates the distance between x country and Poland
    
    R = 6373.0

    lat1 = radians(52.0)
    lon1 = radians(20.0)
    lat2 = radians(latlon[0])
    lon2 = radians(latlon[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return round(distance,3)



from coinbase.wallet.client import Client

client = Client("https://api.coinbase.com/v2/exchange-rates",api_secret="PLN")

# 2nd Stage - Looping per country and appending lists (yeah, I know...)

name=[]
nativeName=[]
alpha2Code=[]
alpha3Code=[]
latlng=[]
population=[]
area=[]
capital=[]
languages=[]
topLevelDomain=[]
timezones=[]
regionalBlocs=[]
currencies=[]
currencies_symbol=[]
currencies_to_PLN=[]
distance_to_PL=[]

print("Uploading and clearing data...")

for x in eu_json:
    
    to_PLN = client.get_exchange_rates(currency=x["currencies"][0]["code"])
    
    name.append(x["name"])
    nativeName.append(x["nativeName"])
    alpha2Code.append(x["alpha2Code"])
    alpha3Code.append(x["alpha3Code"])
    latlng.append(x["latlng"])
    population.append(x["population"])
    try:
        area.append(x["area"])
    except KeyError:
        area.append("")
    capital.append(x["capital"])
    whole_str=""
    for lng in x["languages"]:
        if len(x["languages"]) <2:
            lng_name= lng["name"]
            whole_str = whole_str + str(f"{lng_name}, ")
        else:
            lng_name = lng["name"]
            whole_str = whole_str + str(f"{lng_name}, ")
    
    languages.append(whole_str[:-2])
    topLevelDomain.append(x["topLevelDomain"][0])
    timezones.append(x["timezones"])
    if x["regionalBlocs"]==[]:
        regionalBlocs.append(False)
    elif "EU" not in x["regionalBlocs"][0].values() and "European Union" not in x["regionalBlocs"][0].values():
        regionalBlocs.append(False)
    else:
        regionalBlocs.append(True)
    currencies.append(x["currencies"][0]["name"])
    if "symbol" in x["currencies"][0]:
        currencies_symbol.append(x["currencies"][0]["symbol"])
    else:
        currencies_symbol.append("")
    currencies_to_PLN.append(round(float(to_PLN["rates"]["PLN"]),2))
    distance_to_PL.append(distance_pl(x["latlng"]))



# 3rd stage - making DataFrame and dumping it to csv file

pd.DataFrame({"Country name - English":name,"Country name - Native":nativeName,"Country 2 code":alpha2Code,"Country 3 code":alpha3Code,"Coordinates":latlng,"Population":population,"Area":area,"Capital city":capital,"Languages":languages,"topLevelDomain":topLevelDomain,"timezones":timezones,"Is the country in EU?":regionalBlocs,"Distance to Poland in km":distance_to_PL,"Currency name":currencies,"Currency symbol":currencies_symbol,"To PLN":currencies_to_PLN,"Time of extraction":datetime.datetime.now() }).to_csv("raport1.csv")

end = time.time()     # Ending time of the program for measurement purposes
print(f"Done! It took me {round(end - start,2)} seconds")