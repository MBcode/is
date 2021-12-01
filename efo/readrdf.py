"""
readrdf.py -- rdf utilities
"""
from rdflib import Graph
#from string import join
import sys

def readrdf(filename):
    graph = Graph()
    graph.parse(filename)
    return graph

def print_triples(graph):
    for s,p,o in graph:
        print(s,p,o)

def print_piped_triples(graph):
    for s,p,o in graph:
        print(join([s,p,o], '|'))
        
def doit(filename):
    graph = readrdf(filename)
    print_triples(graph)
    return graph

def save_graph(graph, filename, format='n3'):
    f = open(filename, 'w')
    f.write(graph.serialize(None, format))
    f.close()

def write_piped_triples(graph, filename):
    f = open(filename, 'w')
    for s,p,o in graph:
        f.write(('%s\n' % join([s,p,o], '|')).encode('utf-8'))
    f.close()
        


