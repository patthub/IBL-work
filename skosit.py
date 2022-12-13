# -*- coding: utf-8 -*-
"""Skosit

Input json file is located here: https://drive.google.com/file/d/1fDPwXFBePzfN2y0CRPOf7pw-ST3qIS2D/view?usp=sharing

"""

!pip install rdflib
!pip install unidecode
!pip install tqdm
!pip install SPARQLWrapper
!pip install pandas

import pandas as pd
import itertools
from rdflib import Graph, Literal, RDF, URIRef, Namespace, SKOS, RDFS #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's
import json
import unidecode
from tqdm import tqdm
from SPARQLWrapper import SPARQLWrapper, JSON

with open("/content/drive/MyDrive/sample (1).json", "r", encoding="utf-8") as f:
  dict_whole = json.load(f)

'''
Name of controlled dictionary
'''

BN_SKOS = "Deskryptory_BN_w_SKOS"


'''
Namespaces 
'''
TERMS = Namespace('https://bn-skos.lab.dariah.pl/scheme')
WIKIDATA = Namespace("http://www.wikidata.org/entity/")

schema = Namespace('http://schema.org/')
lcsh = Namespace("http://id.loc.gov/authorities/subjects/")
YSO = Namespace("https://finto.fi/yso/en/page")
EUROVOC = Namespace("")
openalex = Namespace("https://openalex.org/")


'''
Types of relations (with labels) in BN-SKOS
'''
ALT_LABELS = ["450a", "label_en", "label_fr", "label_ger", "label_ukr"]
RELATED = ["550a", "555a", "555 'w': 'g'", "555 'w': 'h'"]
BROADER = ["550 'w': 'g'"]
NARROWER = ["550 'w': 'h'"]
CLOSE_MATCH = ["lcsh", "YSO", "openalex", "eurovoc"]

'''
Creation of preferred labels list 
(for graph creation purposes; used in create_graph_from_json function)
'''
PREF_LABELS = []
for k,v in dict_whole.items():
  PREF_LABELS.append(k)

def prepare_term(term):

  def replacer(text):
    chars = "\\`*{})[]>#+.!$"
    for c in chars:
        if c in text:
            text = text.replace(c, "")
    return text

  final_term = unidecode.unidecode(
      term.replace(" (", "-")
      .replace(" ", "_")
      .replace('"', "")
      .strip()
  )
  return replacer(final_term)
  

def add_alt_label_node(elem, language):
  if not isinstance(elem, float):
    for item in elem:
        graph.add((URIRef(TERMS + pref_label), SKOS.altLabel, Literal(item, lang = language)))
        graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS+BN_SKOS)))

#Create an empty RDF graph
graph = Graph()

#Create top concept of graph, altLables, prefLabel and basic info about the graph
graph.add((URIRef(TERMS + BN_SKOS), RDF['type'], SKOS.Concept))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.inScheme, URIRef(TERMS)))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.topConceptOf, URIRef(TERMS)))
graph.add((URIRef(TERMS),SKOS.topConceptOf, URIRef(TERMS + BN_SKOS)))
graph.add((URIRef(TERMS), RDFS.label, Literal("Deskryptory BN w SKOS", lang = "en") ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.altLabel, Literal("BN_SKOS", lang = "en") ))
graph.add((URIRef(TERMS + BN_SKOS), SKOS.prefLabel, Literal("Deskryptory BN w SKOS", lang = "pl") ))
graph.add((URIRef(TERMS + BN_SKOS), RDFS.label, Literal("Deskryptory BN w SKOS", lang = "pl") ))



for single_dict in tqdm(dict_whole.values()):
  for k, v in single_dict.items():

    if k == "150":

      pref_label = prepare_term(v)
      #v = v.strip()
      graph.add((URIRef(TERMS + pref_label), RDF['type'], SKOS.Concept))
      graph.add((URIRef(TERMS + pref_label), SKOS.prefLabel, Literal(v.strip(), lang= 'pl') ))
      graph.add((URIRef(TERMS + pref_label), SKOS.inScheme, URIRef(TERMS)))
      graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS+BN_SKOS)))

    elif k == "450a":
      add_alt_label_node(v, "pl")

    elif k == "label_en":
      add_alt_label_node(v, "en")

    elif k == "label_fr":
      add_alt_label_node(v, "fr")

    elif k == "label_ger":
      add_alt_label_node(v, "de")

    elif k == "label_ukr":
      add_alt_label_node(v, "uk")


    elif k in RELATED and not isinstance(v, float):
        for elem in v:
          if elem in PREF_LABELS:
            related_term = prepare_term(elem)
            graph.add((URIRef(TERMS + pref_label), SKOS.related, URIRef(TERMS + unidecode.unidecode(related_term))))
            graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS+BN_SKOS)))
          
    elif k in BROADER and not isinstance(v, float):
      for elem in v:
        if elem in PREF_LABELS:
          broader_term = prepare_term(elem)
          graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS + unidecode.unidecode(broader_term))))
          graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS+BN_SKOS)))
          
    elif k in NARROWER and not isinstance(v, float):
      for elem in v:
        if elem in PREF_LABELS:
          narrower_term = prepare_term(elem)
          graph.add((URIRef(TERMS + pref_label), SKOS.narrower, URIRef(TERMS + unidecode.unidecode(narrower_term))))
          graph.add((URIRef(TERMS + pref_label), SKOS.broader, URIRef(TERMS+BN_SKOS)))

    elif k in CLOSE_MATCH and not isinstance(v, float):
      for elem in v:
        if k == "lcsh":
          close_term = prepare_term(elem)
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(lcsh + unidecode.unidecode(close_term))))
      
        elif k == "YSO":
          close_term = prepare_term(elem)
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(YSO + unidecode.unidecode(close_term))))
          
        elif k == "openalex":
          close_term = prepare_term(elem)
          graph.add((URIRef(TERMS + pref_label), SKOS.closeMatch, URIRef(openalex + unidecode.unidecode(close_term))))



    

graph.serialize("bn_skos_13_12_22.ttl", format = "turtle")
