"""
 /rhome/wjrogers/studio/python/rdf/efo_extract.py, Mon Jan  9 14:05:05 2012, edit by Will Rogers

Extract concepts and synomyms from EFO_inferred_v2.18.owl and generate
UMLS format tables for use by MetaMap's Data File Builder.


Original Author: Willie Rogers, 09jan2012
"""
from rdflib import ConjunctiveGraph, Graph
from rdflib import Namespace, URIRef
#from string import join
from readrdf import readrdf
import re
import sys

from mwi_utilities import normalize_ast_string

#efo_datafile = '/usr/local/pub/rdf/EFO_inferred_v2.18.owl'
#efo_datafile = 'efo.owl'
#efo_datafile = 'efo1.owl'
 #xml.sax._exceptions.SAXParseException: file:///var/www/html/n/ff/is/src/lhncbc/efo/efo2dfb/efo1.owl:9974:0: no element found
efo_datafile = '../efo.owl'
EFO = Namespace("http://www.ebi.ac.uk/efo/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
OWL = Namespace("http://www.w3.org/2002/07/owl#")
BFO = Namespace("http://www.ifomis.org/bfo/1.1/snap#MaterialEntity")

mmencoding='ascii'

prefixdict = { 'http://www.ebi.ac.uk/efo/' : 'EFO',
               'http://purl.org/obo/owl/GO#' : 'GO',
               'http://purl.org/obo/owl/NCBITaxon#' : 'NCBITaxon',
               'http://purl.org/obo/owl/CL#' : 'CL',
               'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=' : 'CHEBI',
               'http://purl.obolibrary.org/obo/' : 'OBO', 
               'http://www.geneontology.org/formats/oboInOwl#' : 'oboInOwl',
               'http://purl.org/obo/owl/UO#' : 'UO',
               'http://www.ifomis.org/bfo/1.1/snap#' : 'SNAP',
               'http://purl.org/obo/owl/PATO' : 'PATO',
               'http://www.ifomis.org/bfo/1.1/span#' : 'SPAN', }
prefixlist = [ 'http://www.ebi.ac.uk/efo/',
               'http://purl.org/obo/owl/GO#',
               'http://purl.org/obo/owl/NCBITaxon#',
               'http://purl.org/obo/owl/CL#',
               'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=',
               'http://purl.obolibrary.org/obo/',
               'http://www.geneontology.org/formats/oboInOwl#', 
               'http://purl.org/obo/owl/UO#',
               'http://www.ifomis.org/bfo/1.1/snap#',
               'http://purl.org/obo/owl/PATO',
               'http://www.ifomis.org/bfo/1.1/span#', ]
srclist = [ 'EFO', 'GO', 'NCBITaxon', 'CL', 'CHEBI', 'OBO', 'oboInOwl',
            'UO', 'SNAP', 'PATO', 'SPAN']
semtypes = [('T045','Genetic Function','genf'),
            ('T028','Gene or Genome','gegm'),
             ('T116','Amino Acid, Peptide, or Protein','aapp'),]

def list_id_and_labels(graph):
    for s,p,o in graph:
        if p.__str__ == 'http://www.w3.org/2000/01/rdf-schema#label':
            print((s,p,o))

def query_labels(graph):
    ns = dict(efo=EFO,rdfs=RDFS)
    return graph.query('SELECT ?aname ?bname WHERE { ?a rdfs:label ?b }', 
                       initNs=ns)

def query_efo_type(graph, typename):
    ns = dict(efo=EFO, rdfs=RDFS)
    return graph.query('SELECT ?aname ?bname WHERE { ?a efo:%s ?b }' % typename, 
                       initNs=ns)

def query_efo_concepts(graph):
    ns = dict(owl=OWL, rdf=RDF)
    return graph.query('SELECT ?s { ?s rdf:type owl:Class }', initNs=ns)

def query_efo_concept_labels(graph):
    " return all labels (concepts) from graph (EFO_inferred_v2.18.owl)"
    ns = dict(owl=OWL, rdf=RDF, rdfs=RDFS)
    return graph.query('SELECT ?s ?o { ?s rdf:type owl:Class . ?s rdfs:label ?o }',
                       initNs=ns)

def query_efo_concept_synonyms(graph):
    " return all alternative_terms (synonyms) from graph (EFO_inferred_v2.18.owl)"
    ns = dict(owl=OWL, rdf=RDF, efo=EFO)
    return graph.query('SELECT ?s ?o { ?s rdf:type owl:Class . ?s efo:alternative_term ?o }',
                       initNs=ns)

def escape_re_chars(prefix):
    " escape regular expression special characters in url"
    return prefix.replace('?','\?').replace('#','\#')

def abbrev_uri_original(uri):
    " remove prefix from uri leaving unique part of identifier "
    for prefix in prefixlist:
        m = re.match(r"(%s)(.*)" % escape_re_chars(prefix),uri)
        if m != None:
            return m.group(2).replace(':','_')
    return uri

#def abbrev_uri(uri):
def abbrev_uri(uri_):
    " remove prefix from uri leaving unique part of identifier "
    if not isinstance(uri_, str):
        uri=uri_.decode('utf-8')
        print(f'not-str:{uri}')
    else:
        uri=uri_
        print(f'{uri}')
    for prefix in prefixlist:
        # print('prefix = ''%s''' % prefix)
        print(f'prefix ={prefix}')
        #m = uri.find(prefix)
        m = uri.find(str(prefix))
        if m == 0:
            newuri = uri[len(prefix):].replace(':','_')
            if newuri.find(':') >= 0:
                print(("problem with abbreviated uri: %s" % newuri))
            return newuri
    return uri

def get_source_name_original(uri):
    " derive source name from uri "
    for prefix in list(prefixdict.keys()):
        m = re.match(r"(%s)(.*)" %  escape_re_chars(prefix),uri)
        if m != None:
            return prefixdict[m.group(1)]
    return uri

#def get_source_name(uri):
def get_source_name(buri):
    " derive source name from uri "
    uri=buri.decode("utf-8") 
    for prefix in list(prefixdict.keys()):
        m = uri.find(prefix)
        if m == 0:
            return prefixdict[uri[0:len(prefix)]]
    return uri


def collect_concepts(graph):
    """ 
    Return dictionaries (maps) of concepts and synonyms
    (alternative_terms) from results of SPARQL queries
    """
    cdict = {}
    conceptresult=query_efo_concept_labels(graph)
    serialnum = 1
    for row in conceptresult:
        key = tuple(row)[0].__str__()
        if key in cdict:
            cdict[key].append(row)
        else:
            cdict[key] = [row]
    syndict = {}
    synonymresult = query_efo_concept_synonyms(graph)
    for row in synonymresult:
        key = tuple(row)[0].__str__()
        if key in syndict:
            syndict[key].append(row)
        else:
            syndict[key] = [row]
    return cdict,syndict

def is_valid_cui(cui):
    return re.match(r"[A-Za-z]+[\_]*[0-9]+" , cui)

def gen_mrcon_original(graph,filename):
    """
    Generate UMLS format MRCON table.

    return rows of the form:
    EFO_0003549|ENG|P|L0000001|PF|S0000001|caudal tuberculum|0|
    EFO_0003549|ENG|S|L0000002|SY|S0000002|posterior tubercle|0|
    EFO_0003549|ENG|S|L0000003|SY|S0000003|posterior tuberculum|0|
    """
    conceptresult=query_efo_concept_labels(graph)
    fp = open(filename,'w')
    serialnum = 1
    for row in conceptresult:
        if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
            fp.write("%s|ENG|P|L%07d|PF|S%07d|%s|0|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                          serialnum, serialnum,
                                                          tuple(row)[1].encode(mmencoding, 'replace')))
            serialnum = serialnum + 1
    fp.close()

def gen_mrcon(filename, cdict={}, syndict={}, strdict={}, luidict={}):
    """
    Generate UMLS format MRCON (concepts) table.

    return rows of the form:
    EFO_0003549|ENG|P|L0000001|PF|S0000001|caudal tuberculum|0|
    EFO_0003549|ENG|S|L0000002|SY|S0000002|posterior tubercle|0|
    EFO_0003549|ENG|S|L0000003|SY|S0000003|posterior tuberculum|0|
    """
    fp = open(filename,'w')
    serialnum = 1
    for key in list(cdict.keys()):
        for row in cdict[key]:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                lui = get_lui(luidict,term)
                if lui == None:
                    sys.stderr.write('gen_mrso: LUI missing for prefname %s\n' % (term))
                sui = strdict.get(term)
                if sui == None:
                    sys.stderr.write('gen_mrcon:SUI missing for preferred name %s\n' % (term))
                fp.write("%s|ENG|P|%s|PF|%s|%s|0|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                        lui, sui, term))
                serialnum = serialnum + 1
        if key in syndict:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                for row in syndict[key]:
                    term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                    lui = get_lui(luidict,term)
                    if lui == None:
                        sys.stderr.write('gen_mrso: LUI missing for synonym %s\n' % (term))
                    sui = strdict.get(term)
                    if sui == None:
                        sys.stderr.write('gen_mrcon:SUI missing for synonym %s\n' % (term))
                    fp.write("%s|ENG|S|%s|SY|%s|%s|0|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                            lui, sui, term))
                    serialnum = serialnum + 1
    fp.close()

def gen_mrso(filename, cdict={}, syndict={}, strdict={}, luidict={}):
    """ 
    Generate UMLS format MRSO (sources) table.

    EFO_0003549|L0000001|S0000001|EFO|PT|http://www.ebi.ac.uk/efo/EFO_0003549|0|
    EFO_0003549|L0000002|S0000002|EFO|SY|http://www.ebi.ac.uk/efo/EFO_0003549|0|
    EFO_0003549|L0000003|S0000003|EFO|SY|http://www.ebi.ac.uk/efo/EFO_0003549|0|
   """
    fp = open(filename,'w')
    serialnum = 1
    for key in list(cdict.keys()):
        for row in cdict[key]:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                lui = get_lui(luidict,term)
                if lui == None:
                    sys.stderr.write('gen_mrso: LUI missing for prefname %s\n' % (term))
                sui = strdict.get(term)
                if sui == None:
                    sys.stderr.write('gen_mrso: SUI missing for prefname %s\n' % (term))
                fp.write("%s|%s|%s|%s|PT|%s|0|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                     lui, sui, 
                                                     get_source_name(tuple(row)[0].encode(mmencoding, 'replace')),
                                                     tuple(row)[0].encode(mmencoding, 'replace')))
                serialnum = serialnum + 1
        if key in syndict:
            for row in syndict[key]:
                if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                    term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                    lui = get_lui(luidict,term)
                    if lui == None:
                        sys.stderr.write('gen_mrso: LUI missing for synonym %s\n' % (term))
                    sui = strdict.get(term)
                    if sui == None:
                        sys.stderr.write('SUI missing for synonym %s\n' % (term))
                    fp.write("%s|%s|%s|%s|SY|%s|0|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                         lui, sui, 
                                                         get_source_name(tuple(row)[0].encode(mmencoding, 'replace')),
                                                         tuple(row)[0].encode(mmencoding, 'replace')))
                    serialnum = serialnum + 1
    fp.close()


def gen_mrconso(filename, cdict={}, syndict={}, auidict={}, strdict={}, luidict={}):
    """
    Generate UMLS RRF format MRCONSO (concept+sources) table

    cui|lat|ts|lui|stt|sui|ispref|aui|saui|scui|sdui|sab|tty|code|str|srl|suppress|cvf

    EFO0003549|ENG|P|L0000001|PF|S0000001|Y|A0003549||||EFO|PT|http://www.ebi.ac.uk/efo/EFO_0003549|caudal tuberculum|0|?|N||
    """
    fp = open(filename,'w')
    serialnum = 1
    for key in list(cdict.keys()):
        for row in cdict[key]:
            uri = tuple(row)[0].encode(mmencoding, 'replace').strip()
            if is_valid_cui(abbrev_uri(uri)):
                sab = get_source_name(uri)
                term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                aui = auidict.get((term,sab))
                if aui == None:
                    sys.stderr.write('gen_mrconso:AUI missing for preferred name %s,%s\n' % (term,sab))
                lui = get_lui(luidict,term)
                if lui == None:
                    sys.stderr.write('gen_mrso: LUI missing for prefname %s\n' % (term))
                sui = strdict.get(term)
                if sui == None:
                    sys.stderr.write('gen_mrconso:SUI missing for preferred name %s\n' % (term))
                fp.write("%s|ENG|P|%s|PF|%s|Y|%s||||%s|PT|%s|%s|0|N||\n" % \
                             (abbrev_uri(uri),lui,sui,
                              aui,sab,uri,term))
                serialnum = serialnum + 1
        if key in syndict:
            uri = tuple(row)[0].encode(mmencoding, 'replace').strip()
            if is_valid_cui(abbrev_uri(uri)):
                for row in syndict[key]:
                    sab = get_source_name(uri)
                    term = tuple(row)[1].encode(mmencoding, 'replace').strip()
                    aui = auidict.get((term,sab))
                    if aui == None:
                        sys.stderr.write('gen_mrconso:AUI missing for synonym %s,%s\n' % (term,sab))
                    lui = get_lui(luidict,term)
                    if lui == None:
                        sys.stderr.write('gen_mrso: LUI missing for synonym %s\n' % (term))
                    sui = strdict.get(term)
                    if sui == None:
                        sys.stderr.write('gen_mrconso:SUI missing for synonym %s\n' % (term))
                    fp.write("%s|ENG|S|%s|SY|%s|Y|%s||||%s|PT|%s|%s|0|N||\n" % \
                                 (abbrev_uri(uri),lui,sui,
                                  aui,sab,uri,term))
                    serialnum = serialnum + 1

    fp.close()

def get_semantic_typeid(uri):
    """ return semantic type id for uri, currently all uris belong to
    the unknown semantic type. """
    return 'T205'

def get_semantic_typeabbrev(uri):
    """ return semantic type abbreviation for uri, currently all uris
    belong to the unknown semantic type."""
    return 'unkn'

def get_semantic_typename(uri):
    """ return semantic type name for uri, currently all uris
    belong to the unknown semantic type."""
    return "Unknown"

def get_semantic_typetree_number(uri):
    """ return semantic tree number for uri, currently all uris
    belong to the unknown semantic type."""
    return "A0.0.0.0.0.0"

def get_semantic_typeui(uri):
    """ return semantic tree number for uri, currently all uris
    belong to the unknown semantic type."""
    return "AT0000000"

def gen_mrsty(filename, cdict={}, syndict={}):
    """ Generate UMLS ORF format MRSTY (semantic type) table.  Currently,
    all of the concepts are assigned the semantic type "unkn". """
    fp = open(filename,'w')
    for key in list(cdict.keys()):
        for row in cdict[key]:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                fp.write("%s|%s|%s|\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                          get_semantic_typeid(tuple(row)[0].encode(mmencoding, 'replace')),
                                          get_semantic_typeabbrev(tuple(row)[0].encode(mmencoding, 'replace'))))
    fp.close()

def gen_mrsty_rrf(filename, cdict={}, syndict={}):
    """ Generate UMLS ORF format MRSTY (semantic type) table.  Currently,
    all of the concepts are assigned the semantic type "unkn". 

    MRSTY.RFF contaons lines like
    C0000005|T116|A1.4.1.2.1.7|Amino Acid, Peptide, or Protein|AT17648347||
    C0000005|T121|A1.4.1.1.1|Pharmacologic Substance|AT17575038||
    C0000005|T130|A1.4.1.1.4|Indicator, Reagent, or Diagnostic Aid|AT17634323||
    C0000039|T119|A1.4.1.2.1.9|Lipid|AT17617573|256|
    C0000039|T121|A1.4.1.1.1|Pharmacologic Substance|AT17567371|256|
    """
    fp = open(filename,'w')
    for key in list(cdict.keys()):
        for row in cdict[key]:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                fp.write("%s|%s|%s|%s|%s||\n" % (abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),
                                                get_semantic_typeid(tuple(row)[0].encode(mmencoding, 'replace')),
                                                get_semantic_typetree_number(tuple(row)[0].encode(mmencoding, 'replace')),
                                                get_semantic_typename(tuple(row)[0].encode(mmencoding, 'replace')),
                                                get_semantic_typeui(tuple(row)[0].encode(mmencoding, 'replace'))))
    fp.close()


def gen_mrsat(filename, cdict={}, syndict={}, auidict={}, strdict={}, luidict={}):
    """ Generate UMLS format MRSAT (Simple Concept and String
    Attributes) table.  Currently, empty. """
    fp = open(filename,'w')
    fp.close()

def gen_mrsab(filename,cdict={},syndict={}):
    """ Generate UMLS format MRSAB (Source Informatino) table.
    Currently, empty. """
    cui_index = 4000000
    fp = open(filename,'w')
    for k,v in list(prefixdict.items()):
        rcui=vcui='C%7s' % cui_index
        vsab=rsab=v
        son=k
        sf=vstart=vend=imeta=rmeta=slc=scc=ssn=scit=''
        srl='0'
        if len(cdict) > 0:
            # count concepts that belong to source
            cres=[x for x in list(cdict.items()) if re.match(r"(%s)(.*)" % k,x[0].__str__())]
            cfr='%d' % len(cres)
            if len(syndict) > 0:
                # count synonyms that belong to source
                sres=[x for x in list(syndict.items()) if re.match(r"(%s)(.*)" % k,x[0].__str__())]
                tfr='%d' % (len(cres)+len(sres))
            else:
                tfr='%d' % len(cres)
        else:
            cfr=tfr=''
        cxty=ttyl=atnl=''
        lat='ENG'
        cenc='ascii'
        curver=sabin='Y'
        fp.write('%s\n' % \
                     '|'.join((vcui,rcui,vsab,rsab,son,sf,vstart,vend,
                           imeta,rmeta,slc,scc,srl,tfr,cfr,cxty,
                           ttyl,atnl,lat,cenc,curver,sabin,ssn,scit)))
        cui_index = cui_index + 1
    fp.close()

def gen_mrrank(filename):
    """ Generate UMLS format MRRANK (Concept Name Ranking) table. """
    ttylist = ['PT', 'SY']
    pred = 400
    fp = open(filename, 'w')
    for sab in srclist:
        for tty in ttylist:
            fp.write('%04d|%s|%s|N|\n' % (pred,sab,tty))
            pred = pred - 1
    fp.close()

def print_result(result):
    for row in result:
        print(("%s|%s" % (tuple(row)[0],tuple(row)[1])))

def write_result(result, filename):
    f = open(filename, 'w')
    for row in result:
        f.write(('%s\n' % '|'.join((tuple(row)[0],tuple(row)[1]))).encode(mmencoding, 'replace'))
    f.close()

def gen_mrcon_list(cdict={}, syndict={}):
    """
    return rows of the form:
    EFO_0003549|ENG|P|L0000001|PF|S0000001|caudal tuberculum|0|
    EFO_0003549|ENG|S|L0000002|SY|S0000002|posterior tubercle|0|
    EFO_0003549|ENG|S|L0000003|SY|S0000003|posterior tuberculum|0|
    """
    mrconlist = []
    serialnum = 1
    for key in list(cdict.keys()):
        for row in cdict[key]:
            if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                # "%s|ENG|P|L%07d|PF|S%07d|%s|0|\n"
                mrconlist.append((abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),'ENG','P',
                                  'L%07d' % serialnum, 'PF', 'S%07d' % serialnum,
                                  tuple(row)[1].encode(mmencoding, 'replace'),'0',''))
                serialnum = serialnum + 1
        if key in syndict:
            for row in syndict[key]:
                if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
                    # "%s|ENG|S|L%07d|SY|S%07d|%s|0|\n"
                    mrconlist.append((abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace')),'ENG','P',
                                      'L%07d' % serialnum, 'SY', 'S%07d' % serialnum,
                                      tuple(row)[1].encode(mmencoding, 'replace'),'0',''))
                    serialnum = serialnum + 1
    return mrconlist

def gen_mrconso_list(cdict={}, syndict={}, auidict={}):
    """
    return rows of the form:
    EFO_0003549|ENG|P|L0000001|PF|S0000001||||caudal tuberculum|0|
    EFO_0003549|ENG|S|L0000002|SY|S0000002|posterior tubercle|0|
    EFO_0003549|ENG|S|L0000003|SY|S0000003|posterior tuberculum|0|
    """

    # mrconlist = []
    # serialnum = 1
    # for key in cdict.keys():
    #     for row in cdict[key]:
    #         if is_valid_cui(abbrev_uri(tuple(row)[0].encode(mmencoding, 'replace'))):
    pass

def gen_strdict(cdict, syndict):
    """ Generate dict of concept and synonym triples mapped by string. """
    strdict = {} 
    for triplelist in list(cdict.values()):
        for triple in triplelist:
            strkey = triple[1].__str__()
            if strkey in strdict:
                strdict[strkey].append(triple)
            else:
                strdict[strkey] = [triple]
    for triplelist in list(syndict.values()):
        for triple in triplelist:
            strkey = triple[1].__str__()
            if strkey in strdict:
                strdict[strkey].append(triple)
            else:
                strdict[strkey] = [triple]
    return strdict

def gen_nmstrdict(cdict, syndict):
    """ Generate dict of concept and synonym triples mapped by nomalized string. """
    strdict = {} 
    for triplelist in list(cdict.values()):
        for triple in triplelist:
            strkey = normalize_ast_string(triple[1].__str__())
            if strkey in strdict:
                strdict[strkey].append(triple)
            else:
                strdict[strkey] = [triple]
    for triplelist in list(syndict.values()):
        for triple in triplelist:
            strkey = normalize_ast_string(triple[1].__str__())
            if strkey in strdict:
                strdict[strkey].append(triple)
            else:
                strdict[strkey] = [triple]
    return strdict

def gen_strdict_histogram(strdict):
    """ Generate histrogram of lengths of string dictionary values. """
    histogram = {}
    for v in list(strdict.values()):
        key = '%d' % len(v)
        if key in histogram:
            histogram[key] += 1
        else:
            histogram[key] = 1
    return histogram

def gen_strdict_listsizedict(strdict):
    sizedict = {}
    for k,v in list(strdict.items()):
        key = '%d' % len(v)
        if key in sizedict:
            sizedict[key].append(k)
        else:
            sizedict[key] = [k]
    return sizedict

def gen_aui_dict(cdict=[],syndict=[],auiprefix='A',offset=0):
    """ A simple way to generate atom unique identifiers (AUIS):

    1. Generate list of strings + vocabulary source from ontology.
    2. Sort list
    3. assign auis in descending order of sorted list.


    cdict: concept dictionary
    syndict: synonym dictionary
    auiprefix: prefix for Atom identifiers,
               usually "A" for standalone DataSets, 
               should be "B" for dataset to be used with UMLS.
               A can be used if range new identifier space is outside
               of existing UMLS atom identifier space.
    offset=start of range for identifiers, default is zero
    """
    aset=set([])
    auidict={}
    for cstr in list(cdict.keys()):
        if cstr == 'http://www.ebi.ac.uk/efo/EFO_0000694':
            print(("%s -> %s" % (cstr,'is SARS ')))
        prefterm = cdict[cstr][0][1].strip().encode(mmencoding, 'replace')
        sab = get_source_name(cstr.encode(mmencoding, 'replace'))                             
        if prefterm == 'SARS':
            print(('%s --> pref: %s,%s' % (cstr, prefterm, sab)))
        aset.add((prefterm, sab))
        if cstr in syndict:
            for row in syndict[cstr]:
                synonym = row[1].strip().encode(mmencoding, 'replace')
                if synonym == 'SARS':
                    print(('%s --> syn: %s,%s' % (cstr, synonym, sab)))
                sab = get_source_name(cstr.encode(mmencoding, 'replace'))
                aset.add((synonym, sab))
    alist = [x for x in aset]
    alist.sort()
    i = offset
    for atom in alist:
        auidict[atom] = '%s%08d' % (auiprefix,i)
        i = i + 1
    return auidict

def gen_sui_dict(cdict=[],syndict=[],suiprefix='S',offset=0):
    """ A simple way to generate String Unique Identifiers(SUIS):

    1. Generate list of strings + vocabulary source from ontology.
    2. Sort list
    3. assign auis in descending order of sorted list.

    cdict: concept dictionary
    syndict: synonym dictionary
    suiprefix: prefix for string identifiers,
              usually "S" for standalone DataSets, 
              should be "T" for dataset to be used with UMLS,
              "S" can be used if range new identifier space is outside
              of existing UMLS string identifier space.
    offset=start of range for identifiers, default is zero
    """
    sset=set([])
    suidict={}
    for cstr in list(cdict.keys()):
        if cstr == 'http://www.ebi.ac.uk/efo/EFO_0000694':
            print(("%s -> %s" % (cstr,'is SARS ')))
        prefterm = cdict[cstr][0][1].strip().encode(mmencoding, 'replace')
        sset.add(prefterm)
        if prefterm == 'SARS':
            print(('%s --> pref: %s' % (cstr, prefterm)))
    for cstr in list(syndict.keys()):
        if cstr == 'http://www.ebi.ac.uk/efo/EFO_0000694':
            print(("%s -> %s" % (cstr,'is SARS ')))
        for row in syndict[cstr]:
            synonym = row[1].strip().encode(mmencoding, 'replace')
            sset.add(synonym)
            if synonym == 'SARS':
                print(('%s --> syn: %s' % (cstr, synonym)))
    slist = [x for x in sset]
    slist.sort()
    i = offset
    for mstring in slist:
        suidict[mstring] = '%s%08d' % (suiprefix,i)
        i = i + 1
    return suidict

def gen_lui_dict(cdict=[],syndict=[],luiprefix='L',offset=0):
    """ A simple way to generate Lexical Unique Identifiers(SUIS):

    1. Generate list of strings + vocabulary source from ontology.
    2. Sort list
    3. assign auis in descending order of sorted list.

    cdict: concept dictionary
    syndict: synonym dictionary
    suiprefix: prefix for string identifiers,
              usually "L" for standalone DataSets, 
              should be "M" for dataset to be used with UMLS,
              "L" can be used if range new identifier space is outside
              of existing UMLS string identifier space.
    offset=start of range for identifiers, default is zero
    """
    nasset=set([])
    luidict={}
    for cstr in list(cdict.keys()):
        if cstr == 'http://www.ebi.ac.uk/efo/EFO_0000694':
            print(("%s -> %s" % (cstr,'is SARS ')))
        prefterm = cdict[cstr][0][1].strip().encode(mmencoding, 'replace')
        nasset.add(normalize_ast_string(prefterm))
        if prefterm == 'SARS':
            print(('%s --> pref: %s' % (cstr, prefterm)))
    for cstr in list(syndict.keys()):
        if cstr == 'http://www.ebi.ac.uk/efo/EFO_0000694':
            print(("%s -> %s" % (cstr,'is SARS ')))
        for row in syndict[cstr]:
            synonym = row[1].strip().encode(mmencoding, 'replace')
            nasset.add(normalize_ast_string(synonym))
            if synonym == 'SARS':
                print(('%s --> syn: %s' % (cstr, synonym)))
    naslist = [x for x in nasset]
    naslist.sort()
    i = offset
    for nasstring in naslist:
        luidict[nasstring] = '%s%08d' % (luiprefix,i)
        i = i + 1
    return luidict

def get_lui(luidict, mstring):
    """ get lui for un-normalized string from lui dictionary """
    return luidict.get(normalize_ast_string(mstring), 'LUI unknown')

def print_couples(alist):
    for el in alist:
        print(("%s: %s" % (el[0].__str__(),el[1].__str__())))

def process(rdffilename):
    print(('reading %s' % rdffilename))
    graph=readrdf(rdffilename)
    print('finding concepts and synonyms')
    cdict,syndict = collect_concepts(graph)
    print('Generating Atom Unique Identifier Dictionary')
    auidict = gen_aui_dict(cdict,syndict)
    print('Generating String Unique Identifier Dictionary')
    suidict = gen_sui_dict(cdict,syndict)
    print('Generating Lexical Unique Identifier Dictionary')
    luidict = gen_lui_dict(cdict,syndict)

#rrf
    print('generating MRCONSO.RRF')
    gen_mrconso('MRCONSO.RRF',cdict,syndict,auidict,suidict,luidict)


#orf
    print('generating MRCON')
    gen_mrcon('MRCON',cdict,syndict,suidict,luidict)
    print('generating MRSO')
    gen_mrso('MRSO',cdict,syndict,suidict,luidict)

#both rrf and orf
    print('generating MRSAB')
    gen_mrsab('MRSAB.RRF',cdict,syndict)
    print('generating MRRANK')
    gen_mrrank('MRRANK.RRF')
    print('generating MRSAT')
    gen_mrsat('MRSAT.RRF',cdict,syndict)
    print('generating MRSTY')
    gen_mrsty('MRSTY',cdict,syndict)
    print('generating MRSTY.RRF')
    gen_mrsty_rrf('MRSTY.RRF',cdict,syndict)

if __name__ == "__main__":
    print(('m_reading %s' % efo_datafile))
    process(efo_datafile)
