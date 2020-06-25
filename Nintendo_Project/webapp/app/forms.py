#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 07:41:11 2020

@author: josephberkowitz
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextField, StringField
from wtforms.validators import DataRequired

class NL_User_Form(FlaskForm):
    is_user = SelectField(
        'Do you have a username on NintendoLife.com?',
        choices=[('y', 'Yes'), ('n', 'No')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')


class GamesForm(FlaskForm):
    game_1 = TextField('Game #1', validators=[DataRequired()])
    game_2 = TextField('Game #2', validators=[DataRequired()])
    game_3 = TextField('Game #3', validators=[DataRequired()])

    submit = SubmitField('Submit Games')

class Username_Form(FlaskForm):
    username = StringField('NintendoLife Username', validators=[DataRequired()])

    submit = SubmitField('Submit')