#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""


from sqlalchemy import create_engine
from sqlalchemy.sql import text
import random
from flask import render_template

from app import app

@app.route('/')
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    
    engine = create_engine('postgresql+psycopg2://josephberkowitz:@localhost:5432/nintendo')
    conn = engine.connect()

    query1 = text('''SELECT DISTINCT username FROM recommendations''')
    results1 = conn.execute(query1).fetchall()
    random_user = random.choice(results1)[0]
    user = {"username": random_user}
    
    query2 = text('''SELECT game FROM known_items where username = :username AND
                 run_time = (SELECT max(run_time) FROM known_items)''')
    results2 = conn.execute(query2, username=random_user).fetchall()
    known_results = [game for game, in results2]
    
    query3 = text('''SELECT game FROM recommendations WHERE username = :username AND 
                 run_time = (SELECT max(run_time) FROM recommendations) ORDER BY predicted_rating DESC LIMIT 10;''')
    results3 = conn.execute(query3, username=random_user).fetchall()
    game_recs = [rec for rec, in results3]
    
    return render_template("index.html", title='Home', user=user, 
                           rated_games=known_results, recommendations=game_recs)

    
   
        



        

    
    