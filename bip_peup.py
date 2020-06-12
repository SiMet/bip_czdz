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
    "Komisji Samorzadnosci i Porzadku Publicznego": 'https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+protoko%C5%82%C3%B3w+z+posiedze%C5%84+Komisji+Samorz%C4%85dno%C5%9Bci+i+Porz%C4%85dku+Publicznego&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29',
    "Obwieszczenia o wszczetych postepowaniach": "https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Obwieszczenia+o+wszcz%C4%99tych+post%C4%99powaniach&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%283%29",
    "Rejestr zarzadzen burmistrza": "https://gmczechowicedziedzice.peup.pl/eurzad.seam?eurzadNazwa=Rejestr+zarz%C4%85dze%C5%84+Burmistrza&actionMethod=eurzad.xhtml%3ApeupAgent.setEurzadMode%282%29"
}

import urllib.request as urllib2
from html.parser import HTMLParser
import unicodedata
import json
import datetime

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

def get_from_peup(section_found, bip):
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