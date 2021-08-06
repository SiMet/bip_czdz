# Skrypt sprawdzajacy nowe informacje na stronie UM
# Autor: Marek Szkowron
# marek.szkowron(at)gmail.com
# 
#

import urllib.request as urllib2
import urllib.error
#from HTMLParser import HTMLParser
from html.parser import HTMLParser
import unicodedata
import json
import datetime


class MyUMPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.page_href = "https://www.czechowice-dziedzice.pl"
        self._tag_counter = 0
        self._date_tag = None
        self._title = None
        self.news_found = None
        self.news = None

    def __call_news_found(self, news):
        if self.news_found:
            news["date"] = news["date"].strip()
            news["title"] = news["title"].strip()
            news["id"] = news["href"]
            self.news_found(news, self.page_href + news["href"])
        
    def get_attr_value(self, attrs, name):
        return next(iter([attr[1] for attr in attrs if attr[0] == name]), None)

    def handle_starttag(self, tag, attrs):
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter + 1
        if tag == "h2":
            self._h2 = True
        _class = self.get_attr_value(attrs, "class")
        if tag == "div" and "col-md-8" == _class:
            self.news = {"id": None, "title": "", "date": "", "v": "1.0"}
            self._tag_counter = 1
        if self.news:
            if _class and "information__date" in _class:
                self._date_tag = tag
            if self._title and tag == "a":
                self.news["href"] = self.get_attr_value(attrs, "href")
            if _class and "featured__title" in _class:
                self._title = tag

    def handle_endtag(self, tag):
        if self._tag_counter > 0:
            self._tag_counter = self._tag_counter - 1
            if self._tag_counter == 0:
                self.__call_news_found(self.news)
                self.news = None
        if self._date_tag == tag:
            self._date_tag = None
        if self._title == tag:
            self._title = None

    def handle_data(self, data):
        if self.news:
            if self._date_tag:
                self.news["date"] += data
            if self._title:
                self.news["title"] += data

def get_page(news_found, href):
    print("GET {}".format(href))
    response = urllib2.urlopen(href)
    html = response.read()
        # print html
    parser = MyUMPageParser()
    parser.news_found = news_found
    parser.feed(html.decode("utf-8"))


def get_um_aktualnosci(news_found):
    links = [f"https://www.czechowice-dziedzice.pl/wszystkie-aktualnosci?page={i}" for i in range(3)]
    for href in links:
        get_page(news_found, href)


def get_um_komunikaty(news_found):
    links = [f"https://www.czechowice-dziedzice.pl/wszystkie-komunikaty?page={i}" for i in range(3)]
    for href in links:
        get_page(news_found, href)

