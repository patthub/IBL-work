
def query_wikidata(term):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = """
      SELECT distinct ?item ?itemLabel ?itemDescription WHERE{  
      ?item ?label "%s"@pl.  
      ?article schema:about ?item .
      ?article schema:inLanguage "pl" .
      ?article schema:isPartOf <https://pl.wikipedia.org/>.	
      SERVICE wikibase:label { bd:serviceParam wikibase:language "pl". }    
    }
    """ % (term)
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.json_normalize(results['results']['bindings'])
    return list(results_df["item.value"])

