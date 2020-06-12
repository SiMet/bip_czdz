# Skrypt sprawdzajacy nowe informacje w BIP
# Autor: Marek Szkowron
# marek.szkowron(at)gmail.com
# 
# Skrypt szuka nowych informacji opublikowanych na wybranych stronach bip.czechowice-dziedzice.pl i gmczechowicedziedzice.peup.pl
#

links = [
'https://www.bip.czechowice-dziedzice.pl/bipkod/19788913',  # Zaproszenia na komisje stale
'https://www.bip.czechowice-dziedzice.pl/bipkod/083/001/001',  # Ogloszenia planowania przestrzennego
'https://www.bip.czechowice-dziedzice.pl/bipkod/19788703',  # interpelacje
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/009/001',  # tomaszowka ogolne
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/009/002',  # tomaszowka protokoly
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/002/001',  # Centrum ogolne
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/002/002',  # Centrum protokoly
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/005/001',  # Lesisko ogolne
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/005/002',  # Lesisko protokoly
'https://www.bip.czechowice-dziedzice.pl/bipkod/070',  # Konsultacje spoleczne
'https://www.bip.czechowice-dziedzice.pl/bipkod/20524865',  # Petycje 2019
'https://www.bip.czechowice-dziedzice.pl/bipkod/22857351',  # Petycje 2020
'https://www.bip.czechowice-dziedzice.pl/bipkod/22097565',  # Protokoly w komisji skarg i wnioskow
'https://www.bip.czechowice-dziedzice.pl/bipkod/008/012',  # Informacje o srodowisku i jego ochronie
'https://www.bip.czechowice-dziedzice.pl/bipkod/008/097', # Obwieszczenia WOJEWODY ŚLĄSKIEGO
'https://www.bip.czechowice-dziedzice.pl/bipkod/008/086', # Obwieszczenia STAROSTY BIELSKIEGO
'https://www.bip.czechowice-dziedzice.pl/bipkod/008/132', # Obwieszczenia PREZYDENTA BIELSKA-BIAŁEJ
]

import urllib.request as urllib2
import urllib.error
#from HTMLParser import HTMLParser
from html.parser import HTMLParser
import unicodedata
import json
import datetime
from bip_eurzad_utils import get_zamowienia_publiczne, get_rejestry
from bip_peup import get_from_peup

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._tag_counter = 0
        self._h2 = False
        self._title = None
        self.section_found = None
        self.section = None

    def get_attr_value(self, attrs, name):
        return next(iter([attr[1] for attr in attrs if attr[0]==name]), None)

    def handle_starttag(self, tag, attrs):
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter + 1
        if tag == "h2":
            self._h2 = True
        _class = self.get_attr_value(attrs, "class")
        if "article-section" == _class:
            id = self.get_attr_value(attrs, "data-announcement-id").encode('ascii','ignore')
            version = self.get_attr_value(attrs, "data-annoucement-version").encode('ascii','ignore')
            self.section = {"id": str(id), "v": str(version), "title": ""}
            self._tag_counter = 1
        if _class and "title" in _class:
            self._title = tag
        

    def handle_endtag(self, tag):
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter - 1
            if self._tag_counter == 0 and self.section_found:
                self.section_found(self.section)
                self.section = None
        if tag == "h2":
            self._h2 = False
        if tag == self._title:
            self._title = None

    def handle_data(self, data):
        if self.section and len(data.strip()) > 0 and (self._h2 or self._title):
            if not self.section["title"]:
                self.section["title"] = str(unicodedata.normalize("NFKD", data.strip()).encode('ascii','ignore'))

def section_found(s, bip, href):
    print(s)
    if s["id"] not in bip or bip[s["id"]] != s["v"]:
        bip[s["id"]] = s["v"]
        #print "On page: {} new version:{}".format(href, s["title"])
        today_str=datetime.datetime.now().strftime("%Y-%m-%d")
        f = open("bip_new_found.txt","a+")
        f.write("{} On page: {} new version:\n{}\r\n".format(today_str, href, s["title"]))
        f.close() 

def new_eurzad_doc_found(doc, bip):
    if doc["id"] not in bip or bip[doc["id"]] != doc["v"]:
        bip[doc["id"]] = doc["v"]
        f = open("bip_new_found.txt","a+")
        f.write("{} On page: {} new version:\n{}\r\n".format(doc["data"], doc["href"], doc["title"]))
        f.close() 
        print("New {} {} {}".format(doc["id"], doc["title"], doc["v"]))


bip = {}
try:
    with open('bip_docs.txt', 'r') as f:
        bip=json.load(f)
except IOError:
    print("Could not open bip_docs.txt")

for href in links:
    continue
    print("GET {}".format(href))
    response = urllib2.urlopen(href)
    html = response.read()
    #print html
    parser = MyHTMLParser()
    parser.section_found = lambda s: section_found(s, bip, href)
    parser.feed(html.decode("utf-8"))

# get_from_peup(section_found, bip)

try:
    get_zamowienia_publiczne(20, lambda d: new_eurzad_doc_found(d, bip))
    get_rejestry(
        {
            "brmrpuVIII": {"count": 1},  # Zaproszenia na RM
            "ua_odecyzj": {"count": 15},  # Obwieszczenia o wydanych decyzjach
            "ua_opostep": {"count": 5},  # Obwieszczenia o wszczętych postępowaniach
            "or_rzb": {"count": 15},  # Rejestr zarządzeń Burmistrza
            "brm_ksipVI": {"count": 2},  # Rejestr protokołów z posiedzeń Komisji Samorządności i Porządku Publicznego
            "brm_krirVI": {"count": 2},  # Rejestr protokołów z posiedzeń Komisji Rozwoju i Rolnictwa
            "brm_krVI": {"count": 2},  #  Rejestr protokołów z posiedzeń Komisji Rewizyjnej
            "brm_kpsVI": {"count": 2},  #  Rejestr protokołów z posiedzeń Komisji Polityki Społecznej
            "brm_kkisVI": {"count": 2},  #  Rejestr protokołów z posiedzeń Komisji Oświaty, Kultury i Sportu
            "brm_kbifVI": {"count": 2},  #  Rejestr protokołów z posiedzeń Komisji Budżetu i Finansów
            "brm_swipVIII": {"count": 2}  #  Rejestr protokołów z Komisji Skarg Wniosków i Petycji - VIII kadencja
        },
        lambda d: new_eurzad_doc_found(d, bip)
    )
except urllib.error.URLError as e:
    print("Exception during fetch eurzad")
    f = open("bip_new_found.txt","a+")
    f.write("Exception during fetch eurzad - {}\n".format(e.reason))
    f.close() 

with open('bip_docs.txt', 'w') as outfile:
    # print(bip)
    json.dump(bip, outfile)