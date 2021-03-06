from .models.models import *
from multiapp.app import app
from flask import render_template, request, url_for, redirect
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

    if request.method == 'POST':

        return render_template('home/home.html', form=form)

    else:
        return render_template('home/home.html', title='ODD Multi-App', form=form)


@app.route('/ward_councillor')
def ward_councillor():
    address = request.args.get("address")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    ward = None

    variables = {'missing': False, 'home_screen': True}
    candidates = []
    if address:
        ward = address_to_ward(address)
        variables['home_screen'] = False
    elif lat:
        ward = coords_to_ward(lon, lat)
        variables['home_screen'] = False

    if ward:
        if ward['ward']:
            variables.update(ward)
            councillor = get_councillor(ward)
            variables["councillor"] = councillor
            variables['modals'] = 1

        else:
            variables['missing'] = True

    variables['title'] = 'Ward Councillor'

    return render_template('councillor/councillor.html', **variables)


@app.route('/wazimap')
def wazimap():
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
            return render_template('wazimap/wazimap.html', **variables)

        else:
            variables['missing'] = True

    variables['title'] = 'Wazimap Data'

    return render_template('wazimap/wazimap.html', **variables)


@app.route('/munimoney')
def munimoney():
    address = request.args.get("address")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    muni = None

    variables = {'missing': False}
    candidates = []
    if address:
        muni = address_to_muni(address)
    elif lat:
        muni = coords_to_muni(lon, lat)

    if muni:
        if muni['muni']:
            variables.update(muni)

            cbalance = cash_balance(muni['muni_id'])

            variables['cbalance'] = cbalance

            wasteful = wasteful_exp(muni['muni_id'])

            variables['wasteful'] = wasteful

            spending = spending_capital(muni['muni_id'])

            variables['spending'] = spending

            repair = repairs(muni['muni_id'])

            variables['repair'] = repair

            return render_template('munimoney/munimoney.html', **variables)

        else:
            variables['missing'] = True

    variables['title'] = 'Munimoney Data'

    return render_template('munimoney/munimoney.html', **variables)


@app.route('/medicine_prices')
def medicine_prices():
    product_name = request.args.get("product_name")
    variables = {'missing': False, 'num_results': 0, 'originator': None, 'product_list': None}

    if product_name:
        results = find_medicine(product_name)

        if results:
            variables['product_list'] = results
            variables['num_results'] = len(results)
            variables['product_name'] = product_name
            variables['modals'] = 1

        else:
            variables['missing'] = True

    variables['title'] = 'Medicine Price Registry'

    return render_template('medicine/medicine.html', **variables)


@app.route('/find_related_products/<string:nappi_code>')
def find_related_products(nappi_code):
    product_name = None
    results = None
    originator = None
    variables = {'missing': False, 'no_similar': False, 'originator': None,
                 'is_comparative_search': False, 'product_list': None}

    if nappi_code:
        results = find_related(int(nappi_code))

    if results:
        for i in range(len(results)):
            if results[i]['nappi_code'] == nappi_code:
                product_name = results[i]['name']
                originator = results[i]
                variables['product_name'] = product_name
                break

        results = results[:i] + results[i + 1:]  # remove originator from results list

        if len(results) < 1:
            variables['no_similar'] = True
        else:
            variables['product_list'] = results
            variables['num_results'] = len(results)
            variables['is_comparative_search'] = True
            variables['originator'] = originator
            variables['modals'] = 1

    else:
        variables['no_similar'] = True

    return render_template('medicine/medicine.html', **variables)


@app.route('/find_doctors')
def find_doctors():
    return render_template('doctorsmp/doctorsmp.html', title='Find Doctors')


@app.route('/find_clinic')
def find_clinic():
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
            print ward
            variables.update(ward)
            print variables
            clinic = get_clinic(ward)
            variables["clinics"] = clinic
            print variables
            variables["modals"] = 1

        else:
            variables['missing'] = True

    variables['title'] = 'Find Clinic'

    return render_template('clinics/clinic.html', **variables)
