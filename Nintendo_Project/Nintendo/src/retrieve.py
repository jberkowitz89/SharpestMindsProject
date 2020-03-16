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
    query = text('''SELECT iid FROM predictions WHERE uid = :name AND 
                 run_time = (SELECT max(run_time) FROM predictions) ORDER BY est DESC LIMIT 10;''')
    results = conn.execute(query, name=username).fetchall()
    return results

link3710_results = get_top_10('link3710')

print("Top 10 Results for link3710")
for item, in link3710_results:
    print(item)
    
