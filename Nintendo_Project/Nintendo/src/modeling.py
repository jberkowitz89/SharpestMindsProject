#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 18:21:34 2020

@author: josephberkowitz
"""
#importing necessary modules
import pandas as pd
import datetime as dt
import numpy as np
#Importing surprise modules
from surprise import Reader, accuracy, Dataset
from surprise.model_selection import train_test_split, GridSearchCV
from surprise import SVD
#Importing evaluation modules
from collections import defaultdict


def create_surprise_dataset(df, user_col, item_col, rating_col, rating_scale):
    '''
    Function for creating surprise dataset out of pandas dataframe.
    Params: df (cleaned dataframe), user_col (string denoting user column), item_col (string denoting 
    item column), rating_col (string denoting rating column), rating_scale (tuple with rating scale)
    :returns surprise_data (surprise dataset object)
    '''
    reader = Reader(rating_scale=rating_scale)
    surprise_data = Dataset.load_from_df(df[[user_col, item_col, rating_col]], reader)
    return surprise_data


def run_grid_search(surprise_data, model, param_grid, scraper_run):
    '''
    Function for running GridSearchCV algorithm tuning. 
    params: surprise_data (surprise dataset), algo (surprise recommender algorithm), 
    param_grid (dictionary, tuning parameters), scraper_run (string)
    :returns gs_results (dataframe), gs_run (string), best_params (dictionary)
    '''
    if model == "SVD":
        gs = GridSearchCV(SVD, param_grid, measures=["rmse"], cv=3)

        gs.fit(surprise_data)
    
        gs_results = pd.DataFrame(gs.cv_results)
        
        gs_results["run_time"] = dt.datetime.now()
        gs_results["algo"] = gs.algo_class
        gs_run = str(np.random.randint(1,100000000))
        gs_results["gs_run"] = gs_run
        gs_results["scraper_run"] = scraper_run
        best_params = gs.best_params["rmse"]
        gs_results['params'] = gs_results['params'].astype(str)
        gs_results['algo'] = gs_results['algo'].astype(str)
    
    else:
        print("No Model, Stop")
    
    return gs_results, gs_run, best_params

def build_full_train(surprise_data):
    '''
    Function for creating a full trainset object from surprise data.
    params: surprise_data (surprise dataset)
    :returns full_train (a full trainset)
    '''
    full_train = surprise_data.build_full_trainset()
    return full_train

def build_full_testset(surprise_data):
    '''
    Function for creating a full testset object from surprise data
    params: surprise data (surprise dataset)
    :returns full_test (a full testet)
    '''
    raw_ratings = surprise_data.raw_ratings
    full_test = surprise_data.construct_testset(raw_ratings)
    return full_test

#Function for creating surprise train and testset
def create_train_and_test(surprise_data, test_size):
    '''
    Function for creating a training and testing dataset from surprise data.
    params: surprise_data (surprise dataset), test_size (float)
    :returns trainset (surprise trainset object), testset (surprise testset object)
    '''
    trainset, testset = train_test_split(surprise_data, test_size)
    return trainset, testset

#Function for running simple implementation of SVD
def run_model(model, trainset, testset, best_params):
    '''
    Function for running surprise's SVD algorithm
    params: trainset (surprise trainset), testset (surprise testset), best_params (dict)
    :returns svd_fit (fitted SVD model), predictions (defaultdict), test_rmse (float)
    '''
    if model == "SVD":
        algo = SVD(n_factors = best_params["n_factors"], n_epochs=best_params["n_epochs"], 
                   lr_all = best_params["lr_all"], reg_all = best_params["reg_all"])
        svd_fit = algo.fit(trainset)
        predictions = svd_fit.test(testset)
        test_rmse = accuracy.rmse(predictions)
     
    return svd_fit, predictions, test_rmse

#Start by creating the interaction matrix
def create_interaction_matrix(df,user_col, item_col, rating_col, norm= False, threshold = None):
    '''
    Function to create an interaction matrix dataframe from transactional type interactions
    Required Input -
        - df = Pandas DataFrame containing user-item interactions
        - user_col = column name containing user's identifier
        - item_col = column name containing item's identifier
        - rating col = column name containing user feedback on interaction with a given item
        - norm (optional) = True if a normalization of ratings is needed
        - threshold (required if norm = True) = value above which the rating is favorable
    Expected output - 
        - Pandas dataframe with user-item interactions ready to be fed in a recommendation algorithm
    '''
    interactions = df.groupby([user_col, item_col])[rating_col] \
            .sum().unstack().reset_index(). \
            fillna(0).set_index(user_col)
    if norm:
        interactions = interactions.applymap(lambda x: 1 if x > threshold else 0)
    return interactions

def create_user_dict(interactions, train):
    '''Function for creating a dictionary of inner and raw ids for users.
    params: interactions (interaction matrix df), train (corresponding surprise trainset)
    :returns user_dict (dictionary of inner and raw user ids)
    '''
    user_dict = {}
    for user in interactions.index:
        user_dict[train.to_inner_uid(user)] = user
    return user_dict

def create_item_dict(interactions, train):
    '''
    Function for creating a dictionary of inner and raw ids for items.
    params: interactions (interaction matrix df), train (corresponding surprise trainset)
    :returns item_dict (dictionary of inner and raw item ids)
    '''
    item_dict = {}
    for item in interactions.columns:
        item_dict[train.to_inner_iid(item)] = item
    return item_dict

def fill_interaction_matrix(interactions, train, user_dict, item_dict, model):
    '''
    Function for filling sparse interaction matrix and getting list of known items for users.
    params: interactions (interaction matrix), train (corresponding trainset), model (surprise model),
    user_dict (user dictionary with inner and raw ids), item_dict (item dictionary with inner and raw ids)
    :returns interactions (filled interaction matrix), known_items (defaultdict of users and their known items)
    '''
    known_items = defaultdict(list)
    for i in train.all_items():
        for j in train.all_users():
            if interactions.loc[user_dict[j], item_dict[i]] != 0:
                known_items[user_dict[j]].append(item_dict[i])
            else:
                interactions.loc[user_dict[j], item_dict[i]] = model.predict(user_dict[j], item_dict[i])[3]
    
    return interactions, known_items

def create_known_items_df(known_items, scraper_run):
    df_lst = []
    for user in known_items.keys():
        for item in known_items[user]:
            row_lst = [user, item]
            df_lst.append(row_lst)
    known_items_df = pd.DataFrame(df_lst, columns=['username', 'game'])
    known_items_df['scraper_run'] = scraper_run
    known_items_df['run_time'] = dt.datetime.now()
    return known_items_df

def create_recommendations_dict(interactions, known_items, n=10):
    '''
    Function for creating a dictionary from interaction matrix dataframe.
    params: interactions (interaction matrix), known_items (dictionary of user's known items),
    n (number of recommendations, default is 10)
    :returns recommendations (dictionary of top n recommendations for each user)
    '''
    recommendations = defaultdict(list)
    for user in interactions.index:
        sorted_games = interactions.loc[user].sort_values(ascending=False)
        for item in sorted_games.index:
            if item not in known_items[user]:
                recommendations[user].append((item, sorted_games[item]))
                if len(recommendations[user]) >= n:
                    break
    
    return recommendations

def create_recommendations_df(recommendations):
    '''
    Function for creating a dataframe of all user recommendations.
    params: recommendations (dictionary of users and their recommendations)
    :returns recommendations_df (organized dataframe of user | recommended_game| predicted_rating ),
    '''
    df_lst = []
    for user in recommendations.keys():
        for item, rating in recommendations[user]:
            row_lst = [user, item, rating]
            df_lst.append(row_lst)
    recommendations_df = pd.DataFrame(df_lst, columns=['username', 'game', 'predicted_rating'])
    recos_run = str(np.random.randint(1,100000000))
    recommendations_df['recommendations_run'] = recos_run
    recommendations_df["run_time"] = dt.datetime.now()
    return recommendations_df, recos_run


