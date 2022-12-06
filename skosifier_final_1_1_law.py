import pandas as pd
import itertools
from rdflib import Graph, Literal, RDF, URIRef, Namespace, SKOS #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import json
import unidecode
import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON



data = pd.read_csv("Kategorie tematyczne\df_prawo i wymiar sprawiedliwości.csv")
dict_whole = data.to_dict(orient='index')
# with open("sample.json", "r", encoding="utf-8") as f:
#   dict_whole = json.load(f)
  




ALT_LABELS = ["450a", "label_en", "label_fr", "label_ger", "label_ukr"]
RELATED = ["550a", "555a", "555 'w': 'g'", "555 'w': 'h'"]
BROADER = ["550 'w': 'g'"]
NARROWER = ["550 'w': 'h'"]
CLOSE_MATCH = ["lcsh", "YSO", "openalex", "eurovoc"]
PREF_LABELS = []

for k,v in dict_whole.items():
  PREF_LABELS.append(k)
  
  
graph = Graph()
# TERMS = Namespace('http://opensubjects.org/terms/')
# TERMS = Namespace('https://iqvoc01.apps.paas-dev.psnc.pl/')
TERMS = Namespace('https://bn-law-skos.lab.dariah.pl/')
TERMS_MATCH = Namespace('https://bn-skos.lab.dariah.pl/')

TERMS1 = Namespace('http://opensubjects.org/terms/')
TERMS2 = Namespace('http://opensubjects.org/terms/literature/')

WIKIDATA = Namespace("http://www.wikidata.org/entity/")

schema = Namespace('http://schema.org/')

lcsh = Namespace("http://id.loc.gov/authorities/subjects/")
YSO = Namespace("https://finto.fi/yso/en/page")
eurovoc = Namespace("")
openalex = Namespace("https://openalex.org/")

BN_SKOS = "Deskryptory_prawo_i_administracja_BN_w_SKOS"



graph.add((URIRef(TERMS + BN_SKOS), RDF['type'], SKOS.Concept))
#graph.add((URIRef(TERMS + BN_SKOS), URIRef(schema+'name'), Literal(BN_SKOS, datatype=XSD.string) ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.inScheme, URIRef(TERMS)))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.topConceptOf, URIRef(TERMS)))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.altLabel, Literal("BN_SKOS", lang = "en") ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.prefLabel, Literal("Deskryptory Prawo i administracja BN w SKOS", lang = "pl") )),

for single_dict in dict_whole.values():
  for k, v in single_dict.items():

    if k == "150":
      
      pref_label = unidecode.unidecode(v.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
      v = v.strip()
      graph.add((URIRef(TERMS + pref_label), RDF['type'], SKOS.Concept))
      graph.add((URIRef(TERMS + pref_label), SKOS.prefLabel, Literal(v, lang= 'pl') ))
      #graph.add((URIRef(TERMS + pref_label), URIRef(schema+'name'), Literal(pref_label, datatype=XSD.string) ))
      graph.add((URIRef(TERMS + pref_label), SKOS.inScheme, URIRef(TERMS)))
      graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
    
    elif k == "450a" and type(v) != float:
      
          v = v.split(",")
          for elem in v:
            elem = elem.replace("[", "").replace("]", "").replace("'", "").strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "pl")))
            graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
          
    elif k == "label_en" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "en")))
            graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
    elif k == "label_fr" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "fr")))
            graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
    elif k == "label_ger" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "de")))
            graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
    elif k == "label_ukr" and type(v) != float:
        for elem in v:
            elem = elem.strip()
            graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(elem, lang= "uk")))
            graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
            
    elif k in RELATED and type(v) != float:
          v = v.split(",")
          for elem in v:
            elem = elem.replace("[", "").replace("]", "").replace("'", "").strip()
            for elem in v:
              
                related_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
                graph.add((URIRef(TERMS + pref_label), SKOS.relatedMatch, URIRef(TERMS_MATCH + unidecode.unidecode(related_term))))
                #graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
        
    elif k in BROADER and type(v) != float:
          v = v.split(",")
          for elem in v:
            elem = elem.replace("[", "").replace("]", "").replace("'", "").strip()
            for elem in v:
              
                broader_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
                graph.add((URIRef(TERMS + pref_label), SKOS.broadMatch, URIRef(TERMS_MATCH + unidecode.unidecode(broader_term))))
                #graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))
          
    elif k in NARROWER and type(v) != float:
          v = v.split(",")
          for elem in v:
            elem = elem.replace("[", "").replace("]", "").replace("'", "").strip()
            for elem in v:
              
                narrower_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
                graph.add((URIRef(TERMS + pref_label), SKOS.narrowMatch, URIRef(TERMS_MATCH + unidecode.unidecode(narrower_term))))
                #graph.add((URIRef(TERMS + pref_label), SKOS.hasTopConcept, URIRef(TERMS+BN_SKOS)))

    elif k in CLOSE_MATCH and type(v) != float:
      for elem in v:
        if k == "lcsh":
          close_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(lcsh + unidecode.unidecode(close_term))))
      
        elif k == "YSO":
          close_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(YSO + unidecode.unidecode(close_term))))
          
        elif k == "openalex":
          close_term = unidecode.unidecode(elem.replace(" ", "_").replace('"', "").replace("(", "-")).strip()
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(openalex + unidecode.unidecode(close_term))))
          



      
      
      
      
      
      
      
      
      
#print(graph.serialize(format='pretty-xml'))  
#graph.serialize('new_bnskos_09_11.ttl',format='turtle')
graph.serialize('law.ttl', format='turtle')