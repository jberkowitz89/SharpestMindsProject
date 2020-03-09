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
    query = text("SELECT iid FROM predictions WHERE uid = :name ORDER BY est DESC LIMIT 10;")
    results = conn.execute(query, name=username).fetchall()
    return results

grumble_results = get_top_10('Grumblevolcano')
print("Top 10 Results for Grumble Volcano")
for item, in grumble_results:
    print(item)
    
