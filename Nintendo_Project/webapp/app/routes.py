#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask import render_template, flash, redirect, url_for, jsonify
from app.forms import GamesForm
from app.models import Clean_Data
from app import app

@app.route('/')
@app.route('/submit_games', methods=['GET', 'POST'])
def submit_games():
    form = GamesForm()
    if form.validate_on_submit():
        flash('Thank you for submitting your games: {}, {}, {}'.format(
            form.game_1.data, form.game_2.data, form.game_3.data))
        return redirect(url_for('retrieve'))
    return render_template("submit_games.html", title="Submit Games", form=form)

@app.route('/display_games')
def display_games():
    data = Clean_Data.query.with_entities(Clean_Data.game).distinct()
    list_games = [d.as_dict() for d in data]
    return jsonify(list_games)

        

    
    