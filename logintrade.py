import urllib.request as urllib2
from pyquery import PyQuery

def get_przetarg(href, znak_sprawy, title, callback):
    print(f"Fetch przetarg: {title}")
    response = urllib2.urlopen(href)
    html = response.read().decode("utf-8")
    container = html[html.find('<div id="container">'):]
    pq = PyQuery(container)
    zalaczniki = pq("ul.zalaczniki a")
    for zalacznik in zalaczniki:
        print(f"{title}:\n{znak_sprawy} {zalacznik.text}")
        zalacznik_href = zalacznik.get('href')
        if callback is not None:
            callback({"order_id": znak_sprawy, "order_title": title.strip(), "title": zalacznik.text.strip(), "id": zalacznik_href, "v": zalacznik_href}, href)

def get_zamowienia(href, file_found):
    get_entries(href, "ustawowe.html", file_found)

def get_przetargi(href, file_found):
    get_entries(href, "przetargi.html", file_found)

def get_entries(href, page, file_found):
    full_url = f"{href}/rejestracja/{page}"
    print(f"Fetch {full_url}")
    response = urllib2.urlopen(full_url)
    html = response.read().decode("utf-8")
    container = html[html.find('<div id="container">'):]
    pq = PyQuery(container)
    przetargi = pq('table.przetargi tr')
    inactive_counter = 0
    print(f"Found {len(przetargi)} entries")
    for przetarg in przetargi:
        if len(przetarg.findall("td")) == 0:
            continue
        if not "inactive" not in przetarg.findall("td")[-1].find("span").get("class"):
            inactive_counter += 1
        if inactive_counter <= 3:
            td = przetarg.findall("td")
            znak_sprawy = td[2].text
            a = td[1].find("a")
            get_przetarg(a.get("href"), znak_sprawy, a.text, file_found)
        else:
            pass
