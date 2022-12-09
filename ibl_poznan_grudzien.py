
import pandas as pd
import numpy as np
from tqdm import tqdm
import spacy
import os
import regex as re
import json
from pymarc import MARCReader
import requests

from heapq import nlargest as _nlargest
from collections import namedtuple as _namedtuple
from difflib import SequenceMatcher

import jellyfish
from Levenshtein import ratio

nlp = spacy.load("pl_core_news_lg")

print("Done")

def open_data(path):
    with open (path, "r") as f:
        data = json.load(f)
    return data


def get_data(url: str) -> list:
    responses = []
    while url:
        url = requests.get(url)
        if url.status_code == 200:
            url = url.json()
            responses.append(url)
            url = url["nextPage"]
            print(f"Downloading: {url}")
        else:
            print("Error while accessing API")
    print("Download complete")
    return responses


def get_subj(sub: str, header: str, field_numbers: list) -> dict:  
    responses = get_data(f"http://data.bn.org.pl/api/authorities.json?{header}={sub}")
    subjects = []
    for response in responses:
        for authority in response["authorities"]:
            for field in authority["marc"]["fields"]:
                for field_number in field_numbers:
                    if field_number in field:
                        for i in field:
                            subjects.append(list(field[i]["subfields"][-1].values())[0])
                
    subjects_dict = {}
    subjects_dict[sub] = subjects
    return subjects_dict




def lemmatize(term):
    lemmas = " ".join([w.lemma_ for w in nlp(term)])
    return lemmas


def get_closest_match(term):
  res = difflib.get_close_matches(term, data_bn.keys(), 2, 0.86)
  return res



Match = _namedtuple('Match', 'a b size')


def get_close_matches(word, possibilities, n=3, cutoff=0.6):
    """Use SequenceMatcher to return list of the best "good enough" matches.
    word is a sequence for which close matches are desired (typically a
    string).
    possibilities is a list of sequences against which to match word
    (typically a list of strings).
    Optional arg n (default 3) is the maximum number of close matches to
    return.  n must be > 0.
    Optional arg cutoff (default 0.6) is a float in [0, 1].  Possibilities
    that don't score at least that similar to word are ignored.
    The best (no more than n) matches among the possibilities are returned
    in a list, sorted by similarity score, most similar first.
    >>> get_close_matches("appel", ["ape", "apple", "peach", "puppy"])
    ['apple', 'ape']
    >>> import keyword as _keyword
    >>> get_close_matches("wheel", _keyword.kwlist)
    ['while']
    >>> get_close_matches("Apple", _keyword.kwlist)
    []
    >>> get_close_matches("accept", _keyword.kwlist)
    ['except']
    """

    if not n >  0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for x in possibilities:
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), x))

    # Move the best scorers to head of list
    result = _nlargest(n, result)
    # Strip scores for the best n matches
    #return [x for score, x in result]
    final_result = []
    if result:
      highest_score = result[0][0]
      for elem in result:
        if elem[0] < highest_score: break
        else: final_result.append(elem[1])
    return final_result

data_bn = open_data("/content/drive/MyDrive/sample (1).json")

def identify_dbn(term: str):
    #term_lemma = lemmatize(term)

    #result_150 = [(k, data_bn[k]["subject_category"]) for k in data_bn.keys() if term == k]
    result = []
    try:
      po_czym_zlapalo = ("150", data_bn[term]["150"])
      result = [data_bn[term], po_czym_zlapalo]
    except KeyError:
      for k,v in data_bn.items():
        if "450a_lemma" in v:
          for elem in v["450a_lemma"]:
            if term == elem:
              po_czym_zlapalo = ("450a", elem)
              result = [v, po_czym_zlapalo]
    if not result:
      close_matches = get_closest_match(term, data_bn.keys()) #po 150
      if close_matches:
        result = []
        for match in close_matches:
          po_czym_zlapalo = ("150_leven", data_bn[match]["150"])
          result.append((data_bn[match], po_czym_zlapalo))
      else:
        part_results_dict = {}
        for k,v in data_bn.items():
          if "450a_lemma" in v:
            part_result = get_closest_match(term, v["450a_lemma"])
            if part_result:
              part_results_dict[part_result[0]] = (k, v["450a_lemma"])
        keys = get_closest_match(term, part_results_dict.keys())
        result = []
        for key in keys:
          key150 = part_results_dict[key][0]
          po_czym_zlapalo = part_results_dict[key][1]
          result.append((data_bn[key150], ("450_leven", po_czym_zlapalo)))
    return result

identify_dbn("Barok")
