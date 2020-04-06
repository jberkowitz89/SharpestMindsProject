#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 15:42:15 2020

@author: josephberkowitz
"""
import pandas as pd
import datetime as dt
import numpy as np

#Function for imputing missing ratings with median
def fill_no_score(df, rating_column, user_column):
    '''
    Function for cleaning raw_df dataframe - filling in No Score values.
    Params: df (dataframe of raw data), rating_column (string denoting rating column),
    user_column (string denoting user column)
    :returns df (cleaned dataframe)
    '''
    #Creating full dataframe
    df_full = df[df[rating_column] != "No Score"]
    df_full[rating_column] = pd.to_numeric(df_full[rating_column])
    
    #Creating pivot by user
    user_pivot = pd.pivot_table(df_full, values=rating_column, index=[user_column],
                                aggfunc=(np.mean, 'count', np.median))
    
    #Find overall median
    ovr_median = df_full[rating_column].median()
    
    #Impute no score values with either user median or global median
    for index, row in df.iterrows():
        if row[rating_column] == "No Score":
            if user_pivot.index.contains(row[user_column]):
                df.loc[index, rating_column] = round(user_pivot.loc[row[user_column]]["median"], 0)
            else:
                df.loc[index, rating_column] = ovr_median
    
    df["run_time"] = dt.datetime.now()
    df = df.drop_duplicates()
    df[rating_column] = df[rating_column].astype(int)
    return df