import pandas as pd
import itertools
from rdflib import Graph, Literal, RDF, URIRef, Namespace, SKOS #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import json
import unidecode
import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON




with open("sample.json", "r", encoding="utf-8") as f:
  dict_whole = json.load(f)
  




ALT_LABELS = ["450a", "label_en", "label_fr", "label_ger", "label_ukr"]
RELATED = ["550a", "555a", "555 'w': 'g'", "555 'w': 'h'"]
BROADER = ["550 'w': 'g'"]
NARROWER = ["550 'w': 'h'"]
CLOSE_MATCH = ["lcsh", "YSO", "openalex", "eurovoc"]
PREF_LABELS = []

for k,v in dict_whole.items():
  PREF_LABELS.append(k)
  
  
graph = Graph()
TERMS = Namespace('http://opensubjects.org/terms/')
TERMS = Namespace('https://iqvoc01.apps.paas-dev.psnc.pl/')

TERMS1 = Namespace('http://opensubjects.org/terms/')
TERMS2 = Namespace('http://opensubjects.org/terms/literature/')

WIKIDATA = Namespace("http://www.wikidata.org/entity/")

schema = Namespace('http://schema.org/')

lcsh = Namespace("http://id.loc.gov/authorities/subjects/")
YSO = Namespace("https://finto.fi/yso/en/page")
eurovoc = Namespace("")
openalex = Namespace("https://openalex.org/")

BN_SKOS = "BN-SKOS"



graph.add((URIRef(TERMS + BN_SKOS), RDF['type'], SKOS.Concept))
#graph.add((URIRef(TERMS + BN_SKOS), URIRef(schema+'name'), Literal(BN_SKOS, datatype=XSD.string) ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.inScheme, URIRef(TERMS)))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.topConceptOf, URIRef(TERMS)))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.altLabel, Literal("BN_skos", lang = "en") ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.prefLabel, Literal("BN-SKOS", lang = "pl") )),

for single_dict in dict_whole.values():
  for k, v in single_dict.items():

    if k == "150":
      
      pref_label = unidecode.unidecode(v.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
      v = v.strip()
      graph.add((URIRef(TERMS + pref_label), RDF['type'], SKOS.Concept))
      graph.add((URIRef(TERMS + pref_label), SKOS.prefLabel, Literal(v, lang= 'pl') ))
      #graph.add((URIRef(TERMS + pref_label), URIRef(schema+'name'), Literal(pref_label, datatype=XSD.string) ))
      graph.add((URIRef(TERMS + pref_label), SKOS.inScheme, URIRef(TERMS)))
    
    elif k == "450a" and type(v) != float:
        for elem in v:
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "pl")))
            
    elif k == "label_en" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "en")))
    elif k == "label_fr" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "fr")))
    elif k == "label_ger" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "de")))
    elif k == "label_ukr" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "uk")))
            
    elif k in RELATED and type(v) != float:
      for elem in v:
        if elem in PREF_LABELS:
          related_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.related, URIRef(TERMS + unidecode.unidecode(related_term))))
        
    elif k in BROADER and type(v) != float:
      for elem in v:
        if elem in PREF_LABELS:
          broader_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS + unidecode.unidecode(broader_term))))
          
    elif k in NARROWER and type(v) != float:
      for elem in v:
        if elem in PREF_LABELS:
          narrower_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.narrower, URIRef(TERMS + unidecode.unidecode(narrower_term))))
          



      
      
      
      
      
      
      
      
      
print(graph.serialize(format='pretty-xml'))  
graph.serialize('new_bnskos_28_09.ttl',format='turtle')


# for single_dict in dict_whole.values():
#   for k, v in single_dict.items():

#     if k == "150":
      
#       pref_label = unidecode.unidecode(v.replace(" ", "_").replace('"', ""))
#       graph.add((URIRef(TERMS + pref_label), RDF['type'], SKOS.Concept))
#       graph.add((URIRef(TERMS + pref_label), SKOS.prefLabel, Literal(unidecode.unidecode(pref_label), lang= 'pl') ))
#       graph.add((URIRef(TERMS + pref_label), URIRef(schema+'name'), Literal(pref_label, datatype=XSD.string) ))
#       graph.add((URIRef(TERMS + pref_label), SKOS.inScheme, URIRef(TERMS)))


#     elif k in NARROWER and k in PREF_LABELS and type(v) != float:
#       temp = v.replace("'", "").replace("[", "").replace("]", "").split(",")
#       for elem in temp:
#         elem = elem.strip().replace(" ", "_").strip("_")
#         graph.add((URIRef(TERMS + pref_label), SKOS.narrower, URIRef(TERMS + unidecode.unidecode(elem))))
        
        
        
