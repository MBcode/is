#mm_request.py  #also w/changes
#call mm_flask.py server, to get the examples returned in it's comments
import requests
import urllib.parse
#URL="http://10.0.0.5:12345/mm/"
URL="http://ideational.ddns.net:12345/mm/"
import json

def qry2url(qry):
    return URL + urllib.parse.quote(qry)

def qry_mm(qry):
    url_q=qry2url(qry)
    print(url_q)
    r=requests.get(url_q)
    print(r)
    rj= r.json()
    print(rj)
    return r.json()

txt_list=["heart", "heart attack"]
#print(list(map(qry_mm,txt_list)))
#==below: janinaj/semrep-py/metamaplite.py
# but edited to start to use rest client code above
#from socketclient import SocketClient

#class MetamapLite:
class Metamap:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'{host}:{port}/mm/' 
        print(f'URL={self.url}')

    def annotate(self, text):
        import json
        #socket_client = SocketClient(self.host, self.port)
        #annotations = socket_client.send(text)
        #print(list(map(qry_mm,text))) #will send url next
        annotations = qry_mm(text)     # ' '
        # print(annotations)
        print(f'annotate:{type(annotations)}')
        #annotations.replace(';;',';\n;') #1st step to being more comparable ;AttributeError: 'list' object has no attribute 'replace'
        print(f'annotate:{annotations}')
        with open("an.tmp", 'a') as f:
            #f.write(annotations)
            #f.write('\n')
            for a in annotations:
                #f.write(a)
                print(a)
            #ad=eval(annotations)
            #annotations2=json.dumps(ad,indent=2)
            #f.write(annotations2)
        #return self.parse_annotations(annotations)
        return annotations  #will need a different parser

    #see if AnthonyMRios/pymetamap mm setting are compatible w/the parse below

    def parse_annotations(self, annotations):
        # format: {(start, length) : list<ScoredUMLSConcept>}
        parsed_annotations = {}

        field_names = ['cui', 'name', 'concept_string', 'score', 'semtypes', 'semgroups']

        # fields that contain a list of strings
        field_list_objs = ['semtypes', 'semgroups']
        for annotation in annotations.split(";;"):
            if annotation.endswith(',,'):
                annotation = annotation[:-2]

            # if string is empty, skip annotation (should only happen at end of annotations string)
            if annotation.strip() == '':
                continue

            field_values = annotation.split(',,')

            # span of entity in annotations string
            span = (int(field_values[0]), int(field_values[1]))

            # parse all matched concepts
            concepts = []
            for index in range(2, len(field_values), len(field_names)):
                concept = dict(zip(field_names, field_values[index: index + len(field_names) + 1]))
                for field_name in field_list_objs:
                    concept[field_name] = concept[field_name].split('::')
                concepts.append(concept)

            parsed_annotations[span] = concepts

        return parsed_annotations

#new:
def test(text=None):
    #mm = Metamap('host' : 'http://ideational.ddns.net', 'port' : '12345')
    mm = Metamap('http://ideational.ddns.net',  '12345')
    if(not text):
        text = "heart attack"
    val = mm.annotate(text)
    print(f'test:text={text},giving:{val}')

