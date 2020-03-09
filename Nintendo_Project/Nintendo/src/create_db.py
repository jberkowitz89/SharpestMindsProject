#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 19:25:11 2020

@author: josephberkowitz
"""

import psycopg2

conn = psycopg2.connect(user="josephberkowitz")
conn.autocommit = True
cur = conn.cursor()

#Creating Nintendo 
create_db = '''CREATE DATABASE nintendo OWNER josephberkowitz;'''

cur.execute(create_db)