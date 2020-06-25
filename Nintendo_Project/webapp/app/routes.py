#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask import render_template, flash, redirect, url_for, jsonify, session
from app.forms import GamesForm, NL_User_Form, Username_Form
from app.models import Clean_Data, Recommendations, Known_Items
from app import app, db

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NL_User_Form()
    if form.validate_on_submit():
        if form.is_user.data == 'y':
            flash('Great! Please enter your name:')
            return redirect(url_for('username'))
        else:
            flash('No Worries! Enter in some Switch games you like:')
            return redirect(url_for('submit_games'))
    return render_template("index.html", title="Switch Recommender System", form=form)

@app.route('/username', methods=['GET', 'POST'])
def username():
    form = Username_Form()
    if form.validate_on_submit():
        session['username'] = form.username.data
        return redirect(url_for('user_recommendations'))
    return render_template("username.html", title="Enter Username", form=form)

@app.route('/user_recommendations', methods=['GET', 'POST'])
def user_recommendations():
    user = session.get('username', None)
    known_max_runtime = db.session.query(db.func.max(Known_Items.run_time)).first()[0]
    known_games = Known_Items.query.filter_by(username=user, run_time=known_max_runtime).with_entities(
                                                                                Known_Items.game).all()
    known_game_lst = [item for item, in known_games]

    reco_max_runtime = db.session.query(db.func.max(Recommendations.run_time)).first()[0]
    recommended_games = Recommendations.query.filter_by(username=user, run_time=reco_max_runtime).with_entities(Recommendations.game).all()
    reco_game_lst = [item for item, in recommended_games]

    if not known_game_lst:
        flash("Looks like we couldn't find you! No Worries, just enter some Switch games you like below")
        return redirect(url_for('submit_games'))

    return render_template('user_recommendations.html', title="Recommendations - {}".format(user),
                           user=user, known_game_lst=known_game_lst, reco_game_lst=reco_game_lst)

@app.route('/submit_games', methods=['GET', 'POST'])
def submit_games():
    form = GamesForm()
    if form.validate_on_submit():
        flash('Thank you for submitting your games: {}, {}, {}'.format(
            form.game_1.data, form.game_2.data, form.game_3.data))
        games = [form.game_1.data, form.game_2.data, form.game_3.data]
        session['games'] = games
        return redirect(url_for('display_games'))
    return render_template("submit_games.html", title="Submit Games", form=form)
3
@app.route('/display_games', methods=['GET', 'POST'])
def display_games():
    query = db.session.query(Clean_Data.game).distinct()
    data = query.all()
    list_games = [{'game': item} for item, in data]
    return jsonify(list_games)




    
    