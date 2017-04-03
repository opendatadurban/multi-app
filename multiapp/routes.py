from .models.models import *
from multiapp.app import app
from flask import render_template, request
import urllib2
import json
# from .models.articles import SearchForm
from spellcheck import correction
from sqlalchemy_searchable import search
import re


@app.route('/', methods=['GET', 'POST'])
def home():
    form =SearchForm()

    # url = 'http://data.opendata.durban/api/action/'
    # req = urllib2.Request(url)
    # req.add_header('Authorization')
    # resp = urllib2.urlopen(req)
    # content = json.loads(resp.read())

    if request.method == 'POST':

        return render_template('home/home.html', form=form)
    else:
        return render_template('home/home.html', title='App 1', form=form)


