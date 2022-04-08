#call mm_flask.py server, to get the examples returned in it's comments
import requests
import urllib.parse
URL="http://10.0.0.5:12345/mm/"

def qry2url(qry):
    return URL + urllib.parse.quote(qry)

def qry_mm(qry):
    url_q=qry2url(qry)
    print(url_q)
    r=requests.get(url_q)
    print(r)
    print(r.json())
    return r.json()

txt_list=["heart", "heart attack"]
print(list(map(qry_mm,txt_list)))
