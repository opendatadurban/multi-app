from .models.models import *
from multiapp.app import app
from flask import render_template, request
from helpers import *
import urllib2
import json
# from .models.articles import SearchForm
from spellcheck import correction
from sqlalchemy_searchable import search
import re


@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()

    # url = 'http://data.opendata.durban/api/action/'
    # req = urllib2.Request(url)
    # req.add_header('Authorization')
    # resp = urllib2.urlopen(req)
    # content = json.loads(resp.read())

    if request.method == 'POST':

        return render_template('home/home.html', form=form)

    else:
        return render_template('home/home.html', title='App 1', form=form)


@app.route('/ward_councillor')
def ward_councillor():
    address = request.args.get("address")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    ward = None

    variables = {'missing': False}
    candidates = []
    if address:
        ward = address_to_ward(address)
    elif lat:
        ward = coords_to_ward(lon, lat)

    if ward:
        if ward['ward']:
            variables.update(ward)
            councillor = get_councillor(ward)
            variables["councillor"] = councillor
            print councillor

        else:
            variables['missing'] = True

    return render_template('councillor/councillor.html', **variables)
