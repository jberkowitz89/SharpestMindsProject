#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GamesForm(FlaskForm):
    game_1 = StringField('Game #1', validators=[DataRequired()])
    game_2 = StringField('Game #2', validators=[DataRequired()])
    game_3 = StringField('Game #3', validators=[DataRequired()])

    submit = SubmitField('Submit Games')