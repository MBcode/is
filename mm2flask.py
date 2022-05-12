#!/usr/bin/env python3
#like mm_flask.py but add 'routes' for subsumption etc. ;mike.bobak
#https://github.com/AnthonyMRios/pymetamap flask wrapper
#sknepal/MM-api had some problems, so a simpler flask #bobak
#INPUT:via curl/browser:  http://localhost:12345/mm/heart
#OUTPUT: [["0", "MMI", "5.18", "Heart", "C0018787", "[bpoc]", "[\"HEART\"-tx-1-\"heart\"-noun-0]", "TX", "1/5", ""]]
from flask import Flask
from flask import request
#from flask_ipban import IpBan
from pymetamap import MetaMap
mm = MetaMap.get_instance('/usr/local/umls/public_mm/bin/metamap20')
#sents = ['Heart Attack', 'John had a huge heart attack']
import json

app = Flask(__name__)

@app.route('/mm/<text>', methods=['GET'])
def mm_concepts(text):
    "get concepts from text"
    print(text)
    sents = [text]
    #concepts,error = mm.extract_concepts(sents,[1,2])
    concepts,error = mm.extract_concepts(sents,[0])
    for concept in concepts:
        print(concept)
    jr = json.dumps(concepts)
    print(jr)
    return jr

#in py code requests can make the spaces safe in the rest call
#INPUT:via curl/browser:  http://localhost:12345/mm/heart%20attack
#[["0", "MMI", "5.18", "Myocardial Infarction", "C0027051", "[dsyn]", "[\"HEART ATTACK\"-tx-1-\"heart attack\"-noun-0]", "TX", "1/12", ""]]
#-----------------------------------------include owlready_db
from owlready2 import *
default_world.set_backend(filename = "pym.sqlite3")
PYM = get_ontology("http://PYM/").load()
SNOMEDCT_US = PYM["SNOMEDCT_US"]
#from is/a14ors
def subsumes(parent, child):
    return (parent in child.parents)
#make predicate for other arg order
def subsumed(child, parent):
    return (parent in child.parents)

def related(a, b):
    if(subsumes(a, b)): return 1
    elif(subsumed(a, b)): return -1
    else: return 0

def split_ints(txt):
    sa=txt.split("_")
    return (int(sa[0]),int(sa[1]))

@app.route('/subsumes/<text>', methods=['GET'])
def subsumes_(txt):
    si=split_ints(txt)
    return subsumes(si[0],si[1])

@app.route('/subsumed/<text>', methods=['GET'])
def subsumed_(txt):
    si=split_ints(txt)
    return subsumed(si[0],si[1])

@app.route('/related/<text>', methods=['GET'])
def related_(txt):
    si=split_ints(txt)
    return related(si[0],si[1])

#-----------------------------------------
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080, debug=True)
    app.run(host='0.0.0.0', port=12345, debug=True)
