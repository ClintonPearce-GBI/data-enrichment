# Data Enrichment Tool - Nutrition
### Purpose
To seek out (via two APIs: USDA & Nutritionix) nutrition information on various products.  Currently with testing (two separate ranges of 100 products) there was a success rate of 100%.
### Input
A JSON file of food products in the GBI data format.
### Output
A JSON file with an added key per item:

    nutrition: {
      nutritionDetails:
        [An array of nutrition objects, with a minimum of calories],
      nutritionMetadata: {
          dateMatched: the time matched (timestamp),
          matchedName: the matching product name (string),
          matchedOn: the API the product was matched on (string)
      }
    }
    
The script is meant to be manipulated, as such the commenting is excessive.  Any questions please reach me @ clinton.pearce@groupbyinc.com
