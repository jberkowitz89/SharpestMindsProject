#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:38:18 2020

@author: josephberkowitz
"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config(['SQLALCHEMY_DATABASE_URI'] = "postgresql://josephberkowitz:@localhost:5432/nintendo")
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

from app import routes, models