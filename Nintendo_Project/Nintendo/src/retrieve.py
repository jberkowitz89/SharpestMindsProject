#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 11:44:34 2020

@author: josephberkowitz
"""


from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine('postgresql+psycopg2://josephberkowitz:@localhost:5432/nintendo')
conn = engine.connect()

def get_top_10(username):
    '''
    Function for printing the top 10 predictions for a given user.
    Params: username (string)
    returns: list of items (list)
    '''
    query = text('''SELECT game FROM recommendations WHERE username = :username AND 
                 run_time = (SELECT max(run_time) FROM recommendations) ORDER BY predicted_rating DESC LIMIT 10;''')
    results = conn.execute(query, username=username).fetchall()
    return results

silentium_results = get_top_10('silentium')

print("Top 10 Results for silentium")
for item, in silentium_results:
    print(item)
    
