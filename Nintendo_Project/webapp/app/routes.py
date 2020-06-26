#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask import render_template, flash, redirect, url_for, jsonify, session
from app.forms import GamesForm, NL_User_Form, Username_Form
from app.models import Clean_Data, Recommendations, Known_Items, Tuning
from app import app, db
from ast import literal_eval
import pandas as pd
from app.utils import add_new_games, new_model, new_user_predictions


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
        return redirect(url_for('new_user_recommendations'))
    return render_template("submit_games.html", title="Submit Games", form=form)

@app.route('/new_user_recommendations', methods=['GET', 'POST'])
def new_user_recommendations():
    games = session.get('games', None)
    games_max_runtime = db.session.query(db.func.max(Clean_Data.run_time)).first()[0]
    tuning_max_runtime = db.session.query(db.func.max(Tuning.run_time)).first()[0]
    params = literal_eval(Tuning.query.filter_by(run_time=tuning_max_runtime, rank_test_rmse=1).with_entities(Tuning.params).first()[0])

    all_games = Clean_Data.query.filter_by(run_time=games_max_runtime,).with_entities(Clean_Data.username,
                                                                                     Clean_Data.game,
                                                                                     Clean_Data.rating).all()
    all_games_df = pd.DataFrame(all_games, columns=['user', 'game', 'rating'])

    new_df = add_new_games(all_games_df, games)
    model = new_model(new_df, (1,10), params)
    recs = new_user_predictions(new_df, model)

    return render_template("new_user_recommendations.html", title="New User Recommendations", games=games, recs=recs)

@app.route('/display_games', methods=['GET', 'POST'])
def display_games():
    query = db.session.query(Clean_Data.game).distinct()
    data = query.all()
    list_games = [{'game': item} for item, in data]
    return jsonify(list_games)




    
    