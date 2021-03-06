import requests
import datetime

URL = "http://mapit.code4sa.org/address?address=%s&generation=2&type=WD"
URL_mun = "http://mapit.code4sa.org/address?address=%s&generation=2&type=MN"
URLxy = "http://mapit.code4sa.org/point/4326/%s,%s"
med_search_URLxy = "https://mpr.code4sa.org/api/v2/search?q=%s"
med_related_URLxy = "https://mpr.code4sa.org/api/v2/related?nappi=%s"

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


''' Clinic Finder'''


def get_clinic(ward):
    id = ward['ward_id']
    r = requests.get('http://data.opendata.durban/api/action/datastore_search?resource_id=8db5e4df-0e24-477a-ba9c-1efe63910586&q=%s' % id)
    js = r.json()
    return js['result']


''' Municipal Money'''


def coords_to_muni(lon, lat):
    url = URLxy % (lon, lat)
    r = requests.get(url)
    js = r.json()
    muni = None

    for key in js:
        if js[key]["type_name"] == 'Municipality':
            muni_name = js[key]["name"]
            muni_id = js[key]["codes"]["MDB"]

    return {
        "muni_id": muni_id,
        "muni": muni_name,
        "address": 'Used geolocation data for Latitude: %.4f and Longitude: %.4f' % (float(lat), float(lon))
    }


def address_to_muni(address):
    r = requests.get(URL_mun % address)
    js = r.json()
    muni_name = None
    muni_id = None
    formatted_address = "Unknown"

    for key in js:
        if "type_name" in js[key]:
            print js[key]
            muni_name = js[key]["name"]
            muni_id = js[key]["codes"]["MDB"]
            ward_key = key

    for address in js["addresses"]:
        if ward_key in address["areas"]:
            formatted_address = address["formatted_address"]

    return {
        "muni_id": muni_id,
        "muni": muni_name,
        "address": formatted_address
    }


def cash_balance(muni_code):
    data = None
    r = requests.get('https://municipaldata.treasury.gov.za/api/cubes/cflow/facts?cut=item.code:"4200"'
                     '|demarcation.code:"%s"|amount_type.code:"AUDA"|'
                     'period_length.length:"year"' % muni_code).json()

    if 'data' in r.keys():
        data = {}
        values = None
        series = None
        colours = None

        for row in r['data']:
            if row['financial_period.period'] > 2012:
                data[row['financial_period.period']] = [float(row['amount']), '#4caf50' if int(row['amount']) > 0 else '#f44336']

        values = [['Year', 'Value', {'role': "annotation"}, {'role': "style"}]]
        series = {}
        colours = []
        for ind, i in enumerate(sorted(data.keys())):
            val = float(data[i][0])
            values.append([str(i), val, ' '.join(['%i' % (val/1000000), 'M']), '#4caf50' if val > 0 else '#f44336'])
            colours.append('#4caf50' if val > 0 else '#f44336')
            series[ind] = {'color': '#4caf50' if val > 0 else '#f44336'}

        data['data'] = values
        data['series'] = series
        data['max'] = max([i[1] for i in values[1:]]) * 1.15
        data['recent'] = values[-1][2]
        data['date'] = int(values[-1][0])
        data['color'] = colours[-1]

    return data


def wasteful_exp(muni_code):
    data = {}
    values = None
    series = None
    colours = None

    data1 = {}
    for y in range(2013, 2017):

        r1 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/incexp/aggregate?cut=item.code:"4600"'
                                 '|demarcation.code:"%s"|amount_type.code:"AUDA"|financial_year_end.year:%s|'
                                 'period_length.length:"year"&aggregates=amount.sum' % (muni_code, y)).json()

        if 'summary' in r1.keys():
            if r1['summary']['amount.sum'] is not None:
                data1[y] = int(r1['summary']['amount.sum'])

    r2 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/uifwexp/facts?cut=demarcation.code:"%s"'
                      % muni_code).json()

    if 'data' in r2.keys():
        data2 = {}
        for row in r2['data']:
            if row['financial_year_end.year'] > 2012:
                if row['financial_year_end.year'] not in data2.keys():
                    data2[row['financial_year_end.year']] = 0
                else:
                    if row['amount'] is not None:
                        data2[row['financial_year_end.year']] += int(row['amount'])

    if len(data1) != 0 and len(data2) != 0:
        values = [['Year', 'Value', {'role': "annotation"}, {'role': "style"}]]
        series = {}
        colours = []
        for ind, i in enumerate(sorted(set(data1.keys()).intersection(set(data2.keys())))):
            val = 100.0 * float(data2[i]) / float(data1[i])
            values.append([str(i), val, ''.join(['%.1f' % val, '%']), '#f44336' if val > 0 else '#4caf50'])
            colours.append('#f44336' if round(val) > 0. else '#4caf50')
            series[ind] = {'color': '#f44336' if round(val) > 0. else '#4caf50'}

    data['data'] = values
    data['series'] = series
    data['max'] = max([i[1] for i in values[1:]]) * 1.15
    data['recent'] = values[-1][2]
    data['date'] = int(values[-1][0])
    data['color'] = colours[-1]

    return data


def spending_capital(muni_code):
    data = {}
    values = None
    series = None
    colours = None
    data1 = {}
    for y in range(2013, 2017):

        r1 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/capital/aggregate?cut=item.code:"4100"'
                          '|demarcation.code:"%s"|amount_type.code:"AUDA"|financial_year_end.year:%s|'
                          'period_length.length:"year"&aggregates=total_assets.sum' % (muni_code, y)).json()

        if 'summary' in r1.keys():
            if r1['summary']['total_assets.sum'] is not None:
                data1[y] = int(r1['summary']['total_assets.sum'])

    data2 = {}
    for y in range(2013, 2017):

        r2 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/capital/aggregate?cut=item.code:"4100"'
                          '|demarcation.code:"%s"|amount_type.code:"ADJB"|financial_year_end.year:%s|'
                          'period_length.length:"year"&aggregates=total_assets.sum' % (muni_code, y)).json()

        if 'summary' in r2.keys():
            if r2['summary']['total_assets.sum'] is not None:
                data2[y] = int(r2['summary']['total_assets.sum'])

    if len(data1) != 0 and len(data2) != 0:
        values = [['Year', 'Value', {'role': "annotation"}, {'role': "style"}]]
        series = {}
        colours = []
        for ind, i in enumerate(sorted(set(data1.keys()).intersection(set(data2.keys())))):
            val = 100 * (float(data1[i]) - float(data2[i])) / float(data2[i])
            values.append([str(i), val, ''.join(['%.1f' % val, '%']), '#4caf50' if round(val) >= -5 else '#ff9800' if round(val) >= -15 else '#f44336'])
            colours.append('#4caf50' if round(val) >= -5 else '#ff9800' if round(val) >= -15 else '#f44336')
            series[ind] = {'color': '#4caf50' if round(val) >= -5 else '#f44336' if round(val) >= -15 else '#ff9800'}

    data['data'] = values
    data['series'] = series
    data['min'] = min([i[1] for i in values[1:]]) * 1.15
    data['recent'] = values[-1][2]
    data['date'] = int(values[-1][0])
    data['color'] = colours[-1]

    return data


def repairs(muni_code):
    data = {}
    values = None
    series = None
    colours = None
    data1 = {}
    for y in range(2013, 2017):

        r1 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/capital/aggregate?cut=item.code:"4100"'
                          '|demarcation.code:"%s"|amount_type.code:"AUDA"|financial_year_end.year:%s|'
                          'period_length.length:"year"&aggregates=repairs_maintenance.sum' % (muni_code, y)).json()

        if 'summary' in r1.keys():
            if r1['summary']['repairs_maintenance.sum'] is not None:
                data1[y] = int(r1['summary']['repairs_maintenance.sum'])

    data2 = {}
    for y in range(2013, 2017):

        r2 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/bsheet/aggregate?cut=item.code:"1300"'
                          '|demarcation.code:"%s"|amount_type.code:"AUDA"|financial_year_end.year:%s|'
                          'period_length.length:"year"&aggregates=amount.sum' % (muni_code, y)).json()

        if 'summary' in r2.keys():
            if r2['summary']['amount.sum'] is not None:
                data2[y] = int(r2['summary']['amount.sum'])

    data3 = {}
    for y in range(2013, 2017):

        r3 = requests.get('https://municipaldata.treasury.gov.za/api/cubes/bsheet/aggregate?cut=item.code:"1401"'
                          '|demarcation.code:"%s"|amount_type.code:"AUDA"|financial_year_end.year:%s|'
                          'period_length.length:"year"&aggregates=amount.sum' % (muni_code, y)).json()

        if 'summary' in r3.keys():
            if r3['summary']['amount.sum'] is not None:
                data3[y] = int(r3['summary']['amount.sum'])

    if len(data1) != 0 and len(data2) != 0 and len(data3) != 0:
        values = [['Year', 'Value', {'role': "annotation"}, {'role': "style"}]]
        series = {}
        colours = []
        for ind, i in enumerate(sorted(set.intersection(set(data1.keys()), set(data2.keys()), set(data3.keys())))):
            val = 100 * float(data1[i]) / (float(data2[i]) + float(data3[i]))
            values.append([str(i), val, ''.join(['%.1f' % val, '%']), '#4caf50' if val > 8 else '#f44336'])
            colours.append('#4caf50' if val > 8 else '#f44336')
            series[ind] = {'color': '#4caf50' if val > 8 else '#f44336'}

    data['data'] = values
    data['series'] = series
    data['max'] = max([i[1] for i in values[1:]])*1.15
    data['recent'] = values[-1][2]
    data['date'] = int(values[-1][0])
    data['color'] = colours[-1]

    return data


''' Find Medicine Prices'''


def find_medicine(name):
    url = med_search_URLxy % (name)
    r = requests.get(url)
    js = r.json()

    if js:
        return js

    return None


def find_related(id):
    url = med_related_URLxy % (id)
    r = requests.get(url)
    js = r.json()

    if js:
        return js

    return None
