import urllib.request
import json
from datetime import datetime, timedelta


def make_request(method, params):
    url = "https://eurzad.finn.pl/gmczechowicedziedzice/"+method
    body = {"id":1,"method": method, "params": params, "jsonrpc":"2.0"}
    req = urllib.request.Request(url)

    jsondata = json.dumps(body)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    f = urllib.request.urlopen(req, jsondataasbytes, timeout=5)
    response = f.read()
    f.close()
    return response.decode('utf8')

def get_from_result(data):
    try:
        return json.loads(json.loads(data)["result"])
    except TypeError as e:
        print("\n\nException while parse response: \n{}\n".format(data))
        raise e

def get_from_lista(data):
    return get_from_result(data)["lista"]

def get_zamowienie(id, tytul, callback):
    method = "/kv/routeZamowieniaServiceManager1"
    response = make_request(method, [str(id)])
    data = get_from_result(response)
    for zal in data["zalaczniki"]:
        print("    Załącznik {}".format(zal["nazwa"]))
        zal_id = "/pobierz.seam?zbior=3&plikId={}&zalId={}".format(id, zal["id"])
        callback({"id": zal_id, "v": zal_id, "title": tytul +"\n"+zal["nazwa"], "data": zal["data"], "href": "https://eurzad.finn.pl/gmczechowicedziedzice/#!/zamowienie/"+str(id)})

def get_zamowienia_publiczne(count, callback):
    def_filter = json.dumps({"szukaj":None,"rodzaj":None,"dataOd":None,"dataDo":None,"terminOd":None,"terminDo":None,"dodatkowe":[],"skorowidz":None})
    def_param = [str(count), "1", "\"DEFAULT\"", def_filter]

    method = "/kv/routeZamowieniaServiceManager0"
    response = make_request(method, def_param)
    zamowienia_publiczne = get_from_lista(response)

    for z in zamowienia_publiczne:
        print("{} {}".format(z["id"], z["temat"]))
        get_zamowienie(z["id"], z["temat"], callback)

def get_rejestr_entry(id, tytul, callback):
    method = "/kv/routeRejestryServiceManager2"
    response = make_request(method, [str(id)])
    data = get_from_result(response)
    for zal in data["zalaczniki"]:
        print("    Załącznik {}".format(zal["nazwa"]))
        zal_id = "/pobierz.seam?zbior=1&plikId={}&zalId={}".format(id, zal["id"])
        callback({"id": zal_id, "v": zal_id, "title": tytul +"\n"+zal["nazwa"], "data": zal["data"], "href": "https://eurzad.finn.pl/gmczechowicedziedzice/#!/rejestr/"+str(id)})

def get_rejestry(przegladane_rejestry, callback):
    method = "/kv/routeRejestryServiceManager0"
    rejestry = get_from_result(make_request(method, []))
    print("Found rejestry")
    visited = []
    for rej in rejestry:
        if rej["symbol"] not in przegladane_rejestry:
            continue
        count = przegladane_rejestry[rej["symbol"]]["count"]
        print(rej["symbol"] + " "+ rej["nazwa"])
        tomorrow = datetime.now()+ timedelta(weeks=3)
        tomorrow_str = tomorrow.strftime("%Y-%m-%dT00:00:00.000+01:00")
        def_filter = json.dumps({"szukaj":None,"prawo":None,"realizacja":None,"dataWydOd":None,"dataWydDo":tomorrow_str,"dataOglOd":None,"dataOglDo":None,"dataWOd":None,"dataWDo":None,"dodatkowe":[],"skorowidz":None})
        def_filter = json.dumps({"dataWydDo":tomorrow_str})

        response = json.loads(make_request("/kv/routeRejestryServiceManager1", ["\"{}\"".format(rej["symbol"]), str(count), "1", "\"DEFAULT\"", def_filter]))

        result = json.loads(response["result"])
        for r in result["lista"]:
            print("{} {} {}".format(r["id"], r["dataW"], r["temat"]))
            get_rejestr_entry(r["id"], r["temat"], callback)

        print("  ")
        visited.append(rej["symbol"])

    for r in przegladane_rejestry:
        if r not in visited:
            date = datetime.today().strftime('%Y-%m-%d %H:%M')
            callback({"id": "invalid_" + r, "v": date, "title": "Nie można znaleźć rejestru: " + r, "data": date, "href": "None"})