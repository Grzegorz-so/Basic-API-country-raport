import json
import requests
from coinbase.wallet.client import Client
import datetime
from math import sin, cos, sqrt, atan2, radians
import csv
import sys
import time

start = time.time()     # Starting time for measurement purposes

print("Connecting...")

response1 = requests.get("https://restcountries.eu/rest/v2/region/europe?fields=name;nativeName;alpha2Code;alpha3Code;latlng;population;area;capital;languages;topLevelDomain;timezones;regionalBlocs;currencies")

if response1.status_code == 200:
    print(f"Connected! Status code is: {response1.status_code}")  # Printing when status code == 200 
else:
    print(f"Unable to connect. Check status code {response1.status_code}")   # Printing when status code != 200
    sys.exit()

eu_json = response1.json()  # Converting repsonse to JSON



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

    return round(distance,3)

client = Client("https://api.coinbase.com/v2/exchange-rates",api_secret="PLN")      # Connecting to exchange rates API

exchange_rates_dict={}      # Dict created for optimalization purposes

class Country:      # Creating Class for every country
    def __init__(self, name, nativeName,alpha2Code,alpha3Code,topLevelDomain,capital,population,latlng,timezones,languages,regionalBlocs,currencies,area=None):
        
        
        self.name = name
        self.nativeName = nativeName
        self.alpha2Code = alpha2Code
        self.alpha3Code = alpha3Code
        if topLevelDomain ==[]:     # Validating if the country has own web domain
            self.topLevelDomain = ""
        else:
            self.topLevelDomain = topLevelDomain[0]
        self.capital = capital
        self.population = population
        self.latlng = latlng
        self.distance_to_poland = distance_pl(latlng)   # Using distance_pl function to measure distance to Poland
        self.timezones = timezones
        all_lang = ""
        for lng in languages:       # Simple clarification for multiple languages
            all_lang = all_lang + f'{lng["name"]}, '
        self.languages = all_lang[:-2]
        if regionalBlocs == []:     # Validating if the Country in EU. Output as boolean
            self.regionalBlocs = False
        else:
            for bloc in regionalBlocs:
                if "EU" in bloc["acronym"]:
                    self.regionalBlocs = True
                else:
                    self.regionalBlocs = False
        if "symbol" in currencies[0]:       # Validating if the currency has it's own symbol
            self.symbol = currencies[0]["symbol"]
        else:
            self.symbol = ""
        self.curr_name = currencies[0]["name"]
        
        if currencies[0]["code"] in exchange_rates_dict:    # Using previously created dict. Appending the dict with a Currency code and value in PLN to minimize using the API
            self.curr_in_pln = exchange_rates_dict[currencies[0]["code"]]
        else:
            to_PLN = client.get_exchange_rates(currency=currencies[0]["code"])
            self.curr_in_pln = round(float(to_PLN["rates"]["PLN"]),2)
            exchange_rates_dict[currencies[0]["code"]] = round(float(to_PLN["rates"]["PLN"]),2)
        
        self.area = area

    
    
    @classmethod        # Class method for decoding JSON to objects using Country class
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    def __repr__(self):     # Repr of an Object as a Country name
        return f'{self.name}'

if __name__ == '__main__':      # Making a csv file 
    filename = 'raport3.csv'
    items = []      # Items as a list of objects
    print("Converting data...")     
    for x in eu_json:
        items.append(Country.from_json(json.dumps(x))) # Most time consuming award winner - Appending Items list with Objects which are created using class method from JSON file

    print("Creating CSV file...")
    with open(filename, 'w',encoding="utf-8",newline='') as f:      # Writing in csv file and encoding it with "utf-8"
        writer = csv.writer(f)
        writer.writerow(["Country name","Native name","2 Code","3 Code","Web domain","Capital city","Population","Distance to Poland","Timezones","Languages","Is the Country in EU?","Area","Currency symbol","Currency name","Converted curr. to PLN","Extraction date"])     # Headers
        for item in items:  # For every object write proper attributes in one row
            writer.writerow([item.name ,item.nativeName,item.alpha2Code,item.alpha3Code,item.topLevelDomain,item.capital,item.population,item.distance_to_poland,item.timezones,item.languages,item.regionalBlocs,item.area,item.symbol,item.curr_name,item.curr_in_pln,datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
    
end = time.time()       # Ending time for measurement purposes

print(f"Done! It took me {round(end-start,2)} seconds")     # Printing duration of the function