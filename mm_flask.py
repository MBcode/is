#!/usr/bin/env python3
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True) 
