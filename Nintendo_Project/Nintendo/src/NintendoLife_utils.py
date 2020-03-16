#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 16:11:06 2020

@author: josephberkowitz
"""
#Importing necessary modules
import pandas as pd
import datetime as dt
import numpy as np
#Importing surprise modules
from surprise import Reader, accuracy, Dataset
from surprise.model_selection import train_test_split, GridSearchCV
from surprise import SVD
#Importing evaluation modules
from collections import defaultdict
from ml_metrics import average_precision
import recmetrics

import Nintendo.src.NintendoLife_Scraping as Nintendo

def create_raw_data_and_game_urls(threads):
    '''
    Function for creating raw data and game url list.
    Params: list of threads (list)
    : returns raw_df dataframe, games_urls_ids list, scraper_run str
    '''
    raw_df = pd.DataFrame()
    games_and_urls = []

    for thread in threads:

        thread_pages = Nintendo.get_max_pages_thread(thread)
        thread_users = Nintendo.get_users(thread, thread_pages)

        for user in thread_users:
            max_pages = Nintendo.get_max_pages(user)
            user_games_ratings, urls = Nintendo.games_ratings_to_df(user, max_pages)
            raw_df = raw_df.append(user_games_ratings)
            games_and_urls.extend(urls)
            print("dataframe length: ", len(raw_df))

    raw_df = raw_df.assign(game_id=(raw_df['game']).astype('category').cat.codes)
    raw_df = raw_df.assign(user_id=(raw_df['user']).astype('category').cat.codes)
    raw_df["run_time"] = dt.datetime.now()
    raw_df["record_id"] = raw_df["user_id"].astype(str) + "_" + raw_df["game_id"].astype(str) + "_" + raw_df["run_time"].dt.date.astype(str)
    scraper_run = str(np.random.randint(1,100000000))
    raw_df["scraper_run"] = scraper_run
    games_urls_ids = [game_url + (game_id,) for game_url, game_id in zip(games_and_urls, raw_df["game_id"])]
    raw_df.reset_index(drop=True, inplace=True)
    
    
    return raw_df, games_urls_ids, scraper_run

def create_meta_data(games_urls_ids, scraper_run):
    '''
    Function for creating game metadata.
    Params: games_urls_ids (list of tuples), scraper_run (string)
    :returns games_meta dataframe
    '''
    games_urls_ids = list(set(games_urls_ids))
    games_meta = Nintendo.get_game_metadata(games_urls_ids)
    games_meta["scraper_run"] = scraper_run
    games_meta['developer'] = games_meta['developer'].astype(str)
    games_meta['game'] = games_meta['game'].astype(str)
    games_meta['genre'] = games_meta['genre'].astype(str)
    games_meta['platform'] = games_meta['platform'].astype(str)
    games_meta['price'] = games_meta['price'].astype(str)
    games_meta['publisher'] = games_meta['publisher'].astype(str)
    games_meta['release_date'] = games_meta['release_date'].astype(str)
    games_meta['scraper_run'] = games_meta['scraper_run'].astype(str)

    return games_meta

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
    return df

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
    :returns predictions (defaultdict), test_rmse (float)
    '''
    if model == "SVD":
        algo = SVD(n_factors = best_params["n_factors"], n_epochs=best_params["n_epochs"], 
                   lr_all = best_params["lr_all"], reg_all = best_params["reg_all"])
        svd_fit = algo.fit(trainset)
        predictions = svd_fit.test(testset)
        test_rmse = accuracy.rmse(predictions)
     
    return predictions, test_rmse

    
def create_preds_df(predictions, gs_results, gs_run):
    '''
    Function for creating predicrtions dataframe from predictions object.
    params: predictions (prediction object), gs_results (gs_results dataframe), gs_run (string)
    :returns df (prediction dataframe), pred_run (string)
    '''
    df = pd.DataFrame(predictions, columns=['uid', 'iid', 'rui', 'est', 'details'])
    df['err'] = abs(df.est - df.rui)
    df["run_time"] = dt.datetime.now()
    df["gs_id"] = gs_results[(gs_results["gs_run"] == gs_run) & (gs_results["rank_test_rmse"] == 1)].index[0]
    pred_run = str(np.random.randint(1,100000000))
    df["pred_run"] = pred_run
    df['details'] = df['details'].astype(str)
    return df, pred_run

#Function for getting top n predictions for each user from a set of predictions
def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    '''

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

#Function for getting a sorted dictionary of top rated items from a user's testset
def create_testset_dict(testset):
    '''
    Return the items rated by a given user within the testset, sorted in descending order.
    
    :params: testset: A testset generated via Surprise
    : returns testset_dict: a collection of users, items which they rated and the given rating
    '''
    testset_dict = defaultdict(list)
    
    for row in testset:
        uid, iid, gt_rating = row
        testset_dict[uid].append((iid, gt_rating))
        
    for uid, user_ratings in testset_dict.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        testset_dict[uid] = user_ratings
        
    return testset_dict

#Function for getting all items from surprise trainset
def all_trainset_items(trainset):
    '''
    Function for creating a list of all trainset items
    params: trainset (surprise trainset object)
    :returns all_items (list)
    '''
    all_items = [trainset.to_raw_iid(item_id) for item_id in trainset.all_items()]
    return all_items

#Function for getting full list of predicted items and testset items
def get_ordered_items_and_predictions(testset, predictions):
    '''
    Function for creating list of ordered testset and predictions.
    params: testset (surprise testset object), predictions (prediction object)
    :returns full_item_list (list), full_predicted_item_list (list)
    '''
    #Sort prediction and testset alphabetically
    ordered_predictions = sorted(predictions)
    ordered_testset = sorted(testset)
    #Instantiate lists
    full_item_list = []
    full_predicted_item_list = []
    #for each user in the prediction users
    for user in ordered_predictions:
        user_item_list = []
        user_predicted_item_list = []
        #if the user is in the testset
        if user in ordered_testset:
            #add the item to the user_item list
            for ir in testset[user]:
                item, rating = ir
                user_item_list.append(item)
            #add the item to the prediction user list
            for ir in predictions[user]:
                item, rating = ir
                user_predicted_item_list.append(item)
            #add the list to the full list
            full_item_list.append(user_item_list)
            full_predicted_item_list.append(user_predicted_item_list)
            
    return full_item_list, full_predicted_item_list

#function for getting MAP@K
def get_mapk(predictions, actuals):
    '''
    Function for calculating mean average precision @ k.
    params: predictions (predicted item list), actuals (full item list)
    :returns mean_apk (float)
    '''
    mean_apk = average_precision.mapk(actual=actuals, predicted=predictions)
    return mean_apk

def get_mark(predictions, actuals, k):
    '''
    Function for calculating mean average recall @ k. 
    params: predictions (predicted item list), actuals (full item list), k (int)
    :returns mean_ark (float)
    '''
    mean_ark = recmetrics.mark(actual=actuals, predicted=predictions, k=k)
    return mean_ark

#Function for getting coverage
def get_coverage_score(predicted_items, trainset_items):
    '''
    Function for calculating coverage score. 
    params: predicted_items (predicted item list), trainset_items (full)
    :returns cov (float)
    '''
    cov = recmetrics.coverage(predicted=predicted_items, catalog=trainset_items)
    return cov

#Function for getting personalization score
def get_personalization_score(predicted_items):
    '''
    Function for calculating personalization score.
    params: predicted_items (predicted item list)
    :returns pers (float)
    '''
    pers = recmetrics.personalization(predicted_items)
    return pers
