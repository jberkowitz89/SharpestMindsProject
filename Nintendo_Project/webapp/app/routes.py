#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask import render_template, flash, redirect, url_for, jsonify
from app.forms import GamesForm, NL_User_Form
from app.models import Clean_Data
from app import app, db

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NL_User_Form()
    if form.validate_on_submit():
        if form.is_user.data == 'y':
            flash('Great! Please enter your name on the next page: ')
            return redirect(url_for('display_games'))
        else:
            flash('No Worries! Enter in some Switch games you like')
            return redirect(url_for('submit_games'))
    return render_template("index.html", title="User", form=form)


@app.route('/submit_games', methods=['GET', 'POST'])
def submit_games():
    form = GamesForm()
    if form.validate_on_submit():
        flash('Thank you for submitting your games: {}, {}, {}'.format(
            form.game_1.data, form.game_2.data, form.game_3.data))
        #return redirect(url_for('index'))
    return render_template("submit_games.html", title="Submit Games", form=form)

@app.route('/display_games', methods=['GET', 'POST'])
def display_games():
    query = db.session.query(Clean_Data.game).distinct()
    data = query.all()
    list_games = [{'game': item} for item, in data]
    return jsonify(list_games)


        

    
    