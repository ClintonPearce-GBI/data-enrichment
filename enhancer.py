# I M P O R T S
# handles web requests
import requests
# parsing and formatting data
import json
# sleeping 1 second in between searches
import time
# adding a timestamp to matches
from datetime import datetime
# now we're getting serious
import re

# D O C S 
# 3600 API calls/hr, limit iteration to 60 products/minute
# USDA API          -->     https://fdc.nal.usda.gov/api-spec/fdc_api.html#/FDC/getFoodsSearch
# Get API key       -->     https://api.data.gov/signup

# Nutritionix API   -->     https://docs.google.com/document/d/1_q-K-ObMTZvO0qUEAxROrN3bwMujwAN25sLHwJzliK0/edit#heading=h.h3vlpu5rgxy0 
# Get API key       -->     http://developer.nutritionix.com

# V A R S 

# USDA api key
api_key = 'oe8evxrmRDE5WdzjuMgP3fe01kLqt6Y8K6mHEh8T'

# USDA api REST endpoint
USDA_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'

# USDA score max (dial in accuracy here)
score = 1100

# Nutritionix url
Nutritionix_url = 'https://trackapi.nutritionix.com/v2/search/instant'

# Nutritionix app id
Nutritionix_app_id = 'd66513f9'

# Nutritionix app key
Nutritionix_app_key = '060087d7350edddbe9e6f01e92dd638c'

# new product data list
enhancedProductData = []

# iteration ranges (for testing)
min = 0
max = 100

# I T E R A T E   F O O D   D A T A B A S E
# open data source
with open('foods.json') as inputProductData:

    # global record counter
    counter = 0

    # success counter
    enhanced_records = 0

    # convert the data to JSON
    foodData = json.load(inputProductData)

    # iterate the product data
    for product in foodData[min:max]:

        # increment counter
        counter += 1

        # print current product name
        print(f'{counter}/{len(foodData[min:max])} - {product["name"]}')

        # set current product name & brand
        name = product['name'].strip('/')
        brand = product['brand']
        categories = product['buckets']

        query = f'{name.split(",")[0].replace(brand, "").strip()} {brand} {categories}'

        # detect hyphenated words, and add them back without
        if re.search("(?=\S*['-])([a-zA-Z-]+)", query):
            hyphenatedWords = " ".join(re.findall("(?=\S*['-])([a-zA-Z-]+)", query))
            query = f'{query} {hyphenatedWords.replace("-", "")}'            

        # request product and brand to USDA
        USDA_response = requests.get(
            USDA_url,
            params = {
                # search by the product item's name
                'query': query,
                'api_key': api_key,
                # and sort by match accuracy
                'sortBy': 'score'
            }
        )

        # print query to user
        print(f'Search String: {query}')

        # filter records with no nutrients
        try:
            # iterate the USDA records
            for USDA_record in json.loads(USDA_response.text)['foods']:
                
                # skip records if there is no nutrition
                if len(USDA_record['foodNutrients']) == 0:
                    pass
                # append the new nutrition data
                elif USDA_record['score'] > score:
                    product['nutrition'] = {
                        'nutritionDetails': USDA_record['foodNutrients'],
                        'nutritionMetadata': {
                            'dateMatched': str(datetime.now()),
                            'matchedName': USDA_record['description'],
                            'matchedOn': 'USDA'
                        }
                    }

                    # increment our successfully updated records
                    enhanced_records += 1

                    # update user
                    print('Match on a USDA record!')
                    print(USDA_record['description'])

                    # record updated, break loop
                    break
                else:
                    # found the product, but without nutrition information or the product was a poor match so we'll alternate to Nutritionix
                    print('Trying Nutritionix...')
                    # if the USDA has failed, alternate to nutritionix where we can aim for at least calories
                    Nutritionix_response = requests.get(
                        Nutritionix_url,
                        params = {
                            # search by the product item's name
                            'query': query,
                            'common': True
                        },
                        headers = {
                            'x-app-id': Nutritionix_app_id,
                            'x-app-key': Nutritionix_app_key
                        }
                    )
                    try:
                        # queue up the first branded Nutritionix record
                        Nutritionix_record = json.loads(Nutritionix_response.text)['branded'][0]
                        Nutritionix_calories = Nutritionix_record['nf_calories']
                        Nutritionix_match_name = Nutritionix_record['brand_name_item_name']
                        product['nutrition'] = {
                            'nutritionDetails': [
                                {
                                "nutrientId":1008,
                                "nutrientName":"Energy",
                                "nutrientNumber":"208",
                                "unitName":"KCAL",
                                "value": Nutritionix_calories
                                }
                            ],
                            'nutritionMetadata': {
                                'dateMatched': str(datetime.now()),
                                'matchedName': Nutritionix_match_name,
                                'matchedOn': 'Nutritionix'
                            }
                        }

                            
                        # increment our successfully updated records
                        enhanced_records += 1
                        
                        # update user
                        print('Match on a Nutritionix record!')
                        print(Nutritionix_record['brand_name_item_name'])

                        break

                    # well we tried
                    except TypeError:
                        # USDA records are sorted by score, so if the first one isn't good enough none are, and Nutritionix failed us so we move on
                        break

        # oh no D:
        except KeyError as e:
            print('Cannot find the item at all, or server error...')
            pass

        # add current product to enhancedProductData
        enhancedProductData.append(product)

        # sleep one second to avoid burning out the USDA api key
        print('')
        time.sleep(1)


with open('enhanced_foods.json', 'w') as outputFoodData:
    json.dump(enhancedProductData, outputFoodData)

print(f'{enhanced_records}/{counter} records enhanced - {enhanced_records/counter*100:3.2f}% Update Rate')