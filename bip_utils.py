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
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/006/001',  # Południowe protokoly i uchwały zebrania
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/006/002',  # Południowe Sprawozdania 
'https://www.bip.czechowice-dziedzice.pl/bipkod/031/002/006/003',  # Południowe uchwały zarządu
'https://www.bip.czechowice-dziedzice.pl/bipkod/070',  # Konsultacje spoleczne
'https://www.bip.czechowice-dziedzice.pl/bipkod/20524865',  # Petycje 2019
'https://www.bip.czechowice-dziedzice.pl/bipkod/22857351',  # Petycje 2020
'https://www.bip.czechowice-dziedzice.pl/bipkod/25674068',  # Petycje 2021
'https://www.bip.czechowice-dziedzice.pl/bipkod/28537971',  # Petycje 2022
#'https://www.bip.czechowice-dziedzice.pl/bipkod/22097565',  # Protokoly w komisji skarg i wnioskow
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


def get_all_bip_links(section_found):
    for href in links:
        # continue
        print("GET {}".format(href))
        response = urllib2.urlopen(href)
        html = response.read()
        #print html
        parser = MyHTMLParser()
        parser.section_found = lambda s: section_found(s, href)
        parser.feed(html.decode("utf-8"))
