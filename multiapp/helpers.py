import requests
import datetime

URL = "http://mapit.code4sa.org/address?address=%s&generation=2&type=WD"
URLxy = "http://mapit.code4sa.org/point/4326/%s,%s"

def get_wazi_data(ward):
    url = 'https://www.wazimap.co.za/profiles/ward-%s.json' % ward['ward_id']
    r = requests.get(url)
    js = r.json()

    return {}


def coords_to_ward(lon, lat):
    url = URLxy % (lon, lat)
    r = requests.get(url)
    js = r.json()
    ward_no = None
    ward_id = None

    for key in js:
        if js[key]["type_name"] == 'Ward':
            ward_no = js[key]["name"]
            ward_id = js[key]["codes"]["MDB"]

    return {
        "ward_id": ward_id,
        "ward": ward_no,
        "address": 'Used geolocation data for Latitude: %.4f and Longitude: %.4f' % (float(lat), float(lon))
    }


def address_to_ward(address):
    r = requests.get(URL % address)
    js = r.json()
    ward_no = None
    ward_id = None
    formatted_address = "Unknown"

    for key in js:
        if "type_name" in js[key]:
            ward_no = js[key]["name"]
            ward_id = js[key]["codes"]["MDB"]
            ward_key = key

    for address in js["addresses"]:
        if ward_key in address["areas"]:
            formatted_address = address["formatted_address"]

    return {
        "ward_id": ward_id,
        "ward": ward_no,
        "address": formatted_address
    }


def get_councillor(ward):
    id = ward['ward_id']
    r = requests.get('https://nearby.code4sa.org/councillor/ward-%s.json' % id)
    js = r.json()
    return js
