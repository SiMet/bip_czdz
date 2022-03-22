# Skrypt sprawdzajacy nowe informacje na stronie UM
# Autor: Marek Szkowron
# marek.szkowron(at)gmail.com
# 
#

import urllib.request as urllib2
import urllib.error
from html.parser import HTMLParser
import unicodedata
import json
import datetime


class PowiatPetcjePageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.page_href = "https://powiat.bielsko.pl"
        self._tag_counter = 0
        self._date_tag = None
        self._title = None
        self.news_found = None
        self.last_open_tag = None
        self.xpath = ""
        self.is_in_tresc = False
        self.is_in_p = False
        self.is_in_href = False
        self.news = None

    def __call_news_found(self, news):
        if self.news_found:
            news["date"] = news["date"].strip()
            news["title"] = news["title"].strip()
            news["id"] = "Powiat-" + news["title"]
            news["v"] = news["href"]
            news["href"] = self.page_href + news["href"]
            self.news_found(news, news["href"])
        
    def get_attr_value(self, attrs, name):
        return next(iter([attr[1] for attr in attrs if attr[0] == name]), None)

    def handle_starttag(self, tag, attrs):
        self.xpath += f"/{tag}"
        self.last_open_tag = tag
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter + 1
        if tag == "div" and self.get_attr_value(attrs, "class") == "tresc":
            self.is_in_tresc = True
            self._tag_counter = 1
        if not self.is_in_tresc:
            return

        if tag == "p":
            self.news = {"id": None, "title": "", "date": "", "v": "1.0", "href": ""}
            self.is_in_p = True
        if tag == "a":
            self.is_in_href = True
            self.news["href"] = self.get_attr_value(attrs, "href")
        return
        if tag == "tr":
            self.petycja = {"id": None, "title": "", "date": "", "v": "1.0", "href": ""}
            self.odpowiedz = {"id": None, "title": "Odpowiedź na:", "date": "", "v": "1.0", "href": ""}
            self._tag_counter = 1
            self._td_count = 0
        if tag == "td":
            self._td_count += 1

        if self._tag_counter > 0:
            if self._td_count == 2 and tag == "a" and not self.petycja["href"]:
                self.petycja["href"] = self.get_attr_value(attrs, "href")
            if self._td_count == 3 and tag == "a" and not self.odpowiedz["href"]:
                self.odpowiedz["href"] = self.get_attr_value(attrs, "href")

    def handle_endtag(self, tag):
        if self.xpath.endswith(f"/{tag}"):
            self.xpath = self.xpath[0:len(self.xpath)-len(f"/{tag}")]
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter - 1
        else:
            self.is_in_tresc = False

        if self.is_in_tresc:
            if tag == "p":
                self.is_in_p = False
            if tag == "a":
                self.is_in_href = False
                self.__call_news_found(self.news)

    def handle_data(self, data):
        if self.is_in_tresc:
            if self.is_in_p:
                data_strip = data.strip()
                if data_strip.startswith("Data odpowiedzi") or data_strip.startswith("Data złożenia"):
                    self.news["date"] += data_strip[data_strip.find(":") + 1:]
                else:
                    if not data_strip.startswith("Imię i nazwisko/nazwa podmiotu"):
                        self.news["title"] += data_strip
            if self.is_in_href:
                data_strip = data.strip()
                self.news["title"] += data_strip

class PowiatBIPPageParser(HTMLParser):

    def __init__(self):
        self.page_href = "https://bip.powiat.bielsko.pl/"
        HTMLParser.__init__(self)
        self._tag_counter = 0
        self._date_tag = None
        self.news = None
        self.xpath = ""

    def __call_news_found(self, news):
        if self.news:
            news["date"] = news["date"].strip()
            news["title"] = news["title"].strip()
            news["id"] = news["title"]
            news["v"] = news["href"]
            news["href"] = self.page_href + news["href"]
            self.news_found(news, news["href"])
        
    def get_attr_value(self, attrs, name):
        return next(iter([attr[1] for attr in attrs if attr[0] == name]), None)

    def handle_starttag(self, tag, attrs):
        self.xpath += f"/{tag}"
        class_value = self.get_attr_value(attrs, "class")
        if tag == "div":
            if class_value and "list" in class_value:
                self.news = {"id": None, "title": "", "date": "", "v": "1.0", "href": ""}
                self._tag_counter = 0
            if class_value and "date_sym" in class_value:
                self._date_tag = self._tag_counter
        if self.news and tag == "a" and attrs:
            if class_value and "router_link" in class_value:
                self.news["href"] = self.get_attr_value(attrs, "href")
        self._tag_counter += 1


    def handle_endtag(self, tag):
        if self.xpath.endswith(f"/{tag}"):
            self.xpath = self.xpath[0:len(self.xpath)-len(f"/{tag}")]
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter - 1
            if self._date_tag == self._tag_counter:
                self._date_tag = None
            if self._tag_counter == 0:
                if self.news and self.news["href"]:
                    self.__call_news_found(self.news)
                self.news = None

    def handle_data(self, data):
        if self._tag_counter > 0 and self.news:
            if self._date_tag is not None:
                self.news["date"] += data.strip()
            else:
                self.news["title"] += data.strip()


                
def get_page(news_found, href, parser):
    print("GET {}".format(href))
    response = urllib2.urlopen(href)
    html = response.read()
        # print html
    parser.news_found = lambda obj, _: news_found(obj, href)
    parser.feed(html.decode("utf-8"))

def get_aktualnosci(news_found):
    links = ["https://powiat.bielsko.pl/strona-81-wykaz_petycji.html"]
    for href in links:
        get_page(news_found, href, PowiatPetcjePageParser())

def get_bip(news_found):
    links = ["https://bip.powiat.bielsko.pl/9901", # Ogłoszenia
             "https://bip.powiat.bielsko.pl/9370", #Interpelacje
             "https://bip.powiat.bielsko.pl/9406" #Odp na interpelacje
            ]
    for href in links:
        get_page(news_found, href, PowiatBIPPageParser())

