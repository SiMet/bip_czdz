import urllib.request
import xml.etree.ElementTree as ET

def make_request():
    url = "http://www.czechowice-dziedzice.pl/www_3.0/aktualnosci.xml"
    req = urllib.request.Request(url)

    f = urllib.request.urlopen(req, None, timeout=5)
    response = f.read()
    f.close()
    return response.decode('utf8')

def get_entries(entry_found):
    root = ET.fromstring(make_request())
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        id = entry.find("{http://www.w3.org/2005/Atom}id").text
        date = entry.find("{http://www.w3.org/2005/Atom}updated").text
        entry_found({"title": title, "v": date, "id": id, "data": date, "href": id})
