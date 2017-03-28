# from .models.articles import *
from multiapp.app import app
from flask import render_template, request
# from .models.articles import SearchForm
from spellcheck import correction
from sqlalchemy_searchable import search
import re


@app.route('/', methods=['GET', 'POST'])
def home():
    # form =SearchForm()

    if request.method == 'POST':

        return render_template('results/results.html')
    else:
        return render_template('home/home.html')


