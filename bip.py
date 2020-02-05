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
'https://www.bip.czechowice-dziedzice.pl/bipkod/070',  # Konsultacje spoleczne
'https://www.bip.czechowice-dziedzice.pl/bipkod/008/012',  # Informacje o srodowisku i jego ochronie
'https://www.bip.czechowice-dziedzice.pl/bipkod/20524865',  # Petycje
'https://www.bip.czechowice-dziedzice.pl/bipkod/22097565'  # Protokoly w komisji skarg i wnioskow
]

epuap = {
    "zaproszenia na RM": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+projekt%C3%B3w+uchwa%C5%82+Rady+Miejskiej&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Zamowienia publiczne": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%284%29',
    "Zamowienia publiczne do 30k EUR": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+zam%C3%B3wie%C5%84+publicznych+do+30+000+EURO&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%283%29',
    "Komisja skarg": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+Komisji+Skarg+Wniosk%C3%B3w+i+Petycji+-+VIII+kadencja&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisja Budzetu i finansow": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Bud%C5%BCetu+i+Finans%C3%B3w&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisja Oswiaty, kultury i sportu": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+O%C5%9Bwiaty%2C+Kultury+i+Sportu&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisji Polityki Spolecznej": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Polityki+Spo%C5%82ecznej&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisji Rewizyjnej": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Rewizyjnej&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisji Rozwoju i Rolnictwa": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Rozwoju+i+Rolnictwa&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Komisji Samorzadnosci i Porzadku Publicznego": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Samorz%C4%85dno%C5%9Bci+i+Porz%C4%85dku+Publicznego&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29'
}

import urllib.request as urllib2
#from HTMLParser import HTMLParser
from html.parser import HTMLParser
import unicodedata
import json
import datetime

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

class TableParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.tr = False
        self.td = False
        self.begin_of_td_data = ""
        self.begin_of_td_data_finished = False
        self.table = False
        self.a = False
        self.section = None
        self.section_found = None

    def get_attr_value(self, attrs, name):
        return next(iter([attr[1] for attr in attrs if attr[0]==name]), None)

    def handle_starttag(self, tag, attrs):
        _class =self.get_attr_value(attrs, "class")
        if tag == "table" and _class and "rich-table" in _class:
            self.table = True
        if tag == "tr":
            self.tr = True
        if tag == "td":
            self.td = True
        if tag == "a":
            href = self.get_attr_value(attrs, "href")
            self.begin_of_td_data_finished = True
            if "zalId" in href:
                self.section = {"id": str(href), "title": str(self.begin_of_td_data+": \n"), "v": str(href)}
                self.a = True

    def handle_endtag(self, tag):
        if tag == "tr":
            self.tr = False
        if tag == "td":
            self.td = False
            self.begin_of_td_data_finished = False
            self.begin_of_td_data = ""
        if tag == "table":
            self.table = False
        if tag == "a":
            self.a = False
            if self.section:
                self.section_found(self.section)
                self.section = None

    def handle_data(self, data):
        if self.table and self.tr and data.strip():
            if self.td and not self.begin_of_td_data_finished:
                self.begin_of_td_data += str(unicodedata.normalize("NFKD", data.strip()).encode('ascii','ignore'))
            if self.section:
                if self.a:
                    #print data
                    self.section["title"] += str(unicodedata.normalize("NFKD", data.strip()).encode('ascii','ignore'))
def section_found(s, bip, href):
    print(s)
    if s["id"] not in bip or bip[s["id"]] != s["v"]:
        bip[s["id"]] = s["v"]
        #print "On page: {} new version:{}".format(href, s["title"])
        today_str=datetime.datetime.now().strftime("%Y-%m-%d")
        f = open("bip_new_found.txt","a+")
        f.write("{} On page: {} new version:\n{}\r\n".format(today_str, href, s["title"]))
        f.close() 

bip = {}
try:
    with open('bip_docs.txt', 'r') as f:
        bip=json.load(f)
except IOError:
    print("Could not open bip_docs.txt")

for href in links:
    #continue
    print("GET {}".format(href))
    response = urllib2.urlopen(href)
    html = response.read()
    #print html
    parser = MyHTMLParser()
    parser.section_found = lambda s: section_found(s, bip, href)
    parser.feed(html.decode("utf-8"))

response = urllib2.urlopen('https://gmczechowicedziedzice.peup.pl/eurzad.seam')
html = response.read()
cookie = response.headers.get('Set-Cookie')

for title, href in epuap.items():
    print("GET {} {}".format(title, href))
    request = urllib2.Request(href)
    request.add_header("cookie", cookie)
    response = urllib2.urlopen(request)
    html = response.read()
    #print html
    parser = TableParser()
    parser.section_found = lambda s: section_found(s, bip, title+" "+href)
    parser.feed(html.decode("utf-8"))

with open('bip_docs.txt', 'w') as outfile:
    print(bip)
    json.dump(bip, outfile)