# Skrypt sprawdzajacy nowe informacje w BIP
# Autor: Marek Szkowron
# marek.szkowron(at)gmail.com
# 
# Skrypt szuka nowych informacji opublikowanych na wybranych stronach:
# https://www.bip.czechowice-dziedzice.pl/
# https://www.czechowice-dziedzice.pl/
# https://eurzad.finn.pl/gmczechowicedziedzice/#!/
#

import sys
import urllib.error
import json
import datetime
from bip_eurzad_utils import get_zamowienia_publiczne, get_rejestry
import bip_utils
import um_page
import ssl
import powiat

ssl._create_default_https_context = ssl._create_unverified_context

NEW_FOUND_FILE = "bip_new_found.txt"
KNOWN_DOCS_FILE = 'bip_docs.txt'

def add_to_bip_if_required(s, bip, print_text):
    if s["id"] not in bip or bip[s["id"]] != s["v"]:
        bip[s["id"]] = s["v"]
        text = print_text(s)
        print(text)
        f = open(NEW_FOUND_FILE, "a+")
        f.write(text)
        f.close()

def section_found(s, bip, href):
    def text_formater(s, href):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        return "{} On page: {} new version:\n{} ({} {})\r\n".format(today_str, href, s["title"], s["id"], s["v"])

    add_to_bip_if_required(s, bip, lambda s: text_formater(s, href))


def powiat_section_found(s, bip, href):
    def text_formater(s, href):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        return "{} On page: {} new version:\n{} ({})\r\n".format(today_str, href, s["title"], s["v"])

    add_to_bip_if_required(s, bip, lambda s: text_formater(s, href))


def new_eurzad_doc_found(doc, bip):
    add_to_bip_if_required(doc, bip,
                           lambda s: "{} On page: {} new version:\n{} ({})\r\n".format(s["data"], s["href"], s["title"], s["id"]))


def new_um_news_found(news, bip, href):
    def text_formater(n):
        today_str = datetime.datetime.now().strftime("%F %X")
        return f"{n['date']} {n['title']}\n{href} - fetched: {today_str}\r\n"

    add_to_bip_if_required(news, bip, text_formater)

def get_eurzad():
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
        f = open(NEW_FOUND_FILE,"a+")
        f.write("Exception during fetch eurzad - {}\n".format(e.reason))
        f.close()

if __name__ == "__main__":
    bip = {}
    try:
        with open(KNOWN_DOCS_FILE, 'r') as f:
            bip = json.load(f)
    except IOError:
        print(f"Could not open {KNOWN_DOCS_FILE}")
        sys.exit(-1)

    um_page.get_um_komunikaty(lambda s, href: new_um_news_found(s, bip, href))
    um_page.get_um_aktualnosci(lambda s, href: new_um_news_found(s, bip, href))
    bip_utils.get_all_bip_links(lambda s, href: section_found(s, bip, href))
    get_eurzad()
    powiat.get_aktualnosci(lambda s, href: powiat_section_found(s, bip, href))
    powiat.get_bip(lambda s, href: powiat_section_found(s, bip, href))

    with open(KNOWN_DOCS_FILE, 'w') as outfile:
        # print(bip)
        json.dump(bip, outfile)