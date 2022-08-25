import pandas as pd
import numpy as np
from tqdm import tqdm
#import spacy
import itertools
import os
import regex as re
import json
from pymarc import MARCReader
import requests
from difflib import SequenceMatcher
import Levenshtein
from SPARQLWrapper import SPARQLWrapper, JSON
from concurrent.futures import ThreadPoolExecutor




#nlp = spacy.load("pl_core_news_lg")

print("Done")




def query_wikidata(term):
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        query = """
            SELECT distinct ?item ?itemLabel ?label_en ?label_fr ?label_ger 
            ?label_ukr ?itemDescription ?lcsh ?unesco ?eurovoc ?YSO ?openalex 

            WHERE{  
              ?item ?label "%s"@pl .  
              OPTIONAL {?item wdt:P244 ?lcsh . }
              OPTIONAL {?item wdt:P757 ?unesco . }
              OPTIONAL {?item wdt:P5437 ?eurovoc . }
              OPTIONAL {?item wdt:P10283 ?openalex . }
              OPTIONAL {?item wdt:P2347 ?YSO . }
              ?item rdfs:label ?label_en filter (lang(?label_en) = "en").
              ?item rdfs:label ?label_fr filter (lang(?label_fr) = "fr").
              ?item rdfs:label ?label_ger filter (lang(?label_ger) = "de").
              ?item rdfs:label ?label_ukr filter (lang(?label_ukr) = "uk").
              SERVICE wikibase:label { bd:serviceParam wikibase:language "pl". }    
            }
        """ % (term)
        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results["results"]["bindings"]
        # if results["results"]["bindings"]:
        #     results_df = pd.json_normalize(results['results']['bindings'])
        #     return results["results"]["bindings"]
            # wikidata_total[term] = results["results"]["bindings"]
            # return wikidata_total

    except:
        pass
    
    
def diff_query_wikidata(term):
    result = query_wikidata(term)
    if result and len(result) == 0:
        result = query_wikidata(term.lower())     
    return result


with open("data_lemmas.json", "r", encoding="utf-8") as f:
  dict_whole = json.load(f)
  



for k,v in tqdm(dict_whole.items()):
    result = diff_query_wikidata(v["150"])
    if result:
        for elem in result:
            for ka,va in elem.items():
                temp = {ka: [va["value"]]}
                dict_whole[k].update(temp)
        
print(dict_whole["Archeologia"]["450a"])
print(dict_whole["Archeologia"]["YSO"])

with open("sample.json", "w") as outfile:
    json.dump(dict_whole, outfile)
    
with open("sample.json", "r", encoding="utf-8") as file:
  sample = json.load(file)
  
print("----------")
print(sample["Archeologia"])
      
    






