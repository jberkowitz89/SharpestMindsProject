#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 19:59:08 2020

@author: josephberkowitz
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from surprise import Reader, Dataset
from surprise.model_selection import train_test_split
from surprise import SVD
from collections import defaultdict
from mlmetrics import average_precision
import recmetrics

#Function for imputing missing ratings with median
def fill_no_score(df, rating_column, user_column):
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
                row[rating_column] = round(user_pivot.loc[row[user_column]]["median"], 0)
            else:
                row["Rating"] = ovr_median
    return df

#Function for plotting ratings histogram
def plt_ratings(df, rating_column):
    #Function for plotting rating histogram
    plt.xlabel('Rating Value')
    plt.ylabel('Count of Ratings')
    plt.title('Histogram of Ratings Distribution')
    plt.grid(True)
    plt.hist(df[rating_column], alpha=0.75, bins=10, edgecolor='black')
    plt.show()
    
#Function for creating surprise dataset
def create_surprise_dataset(df, user_col, item_col, rating_col, rating_scale):
    reader = Reader(rating_scale=rating_scale)
    surprise_data = Dataset.load_from_df(df[[user_col, item_col, rating_col]], reader)
    return surprise_data

#Function for creating surprise train and testset
def create_train_and_test(surprise_data, test_size):
    trainset, testset = train_test_split(surprise_data, test_size)
    return trainset, testset

#Function for running simple implementation of SVD
def run_svd(trainset, testset):
    algo = SVD()
    svd_fit = algo.fit(trainset)
    predictions = svd_fit.test(testset)
    return predictions

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
    all_items = [trainset.to_raw_iid(item_id) for item_id in trainset.all_items()]
    return all_items

#Function for getting full list of predicted items and testset items
def get_ordered_items_and_predictions(testset, predictions):
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
    mean_apk = average_precision.mapk(actual=actuals, predicted=predictions)
    return mean_apk

#Function for getting coverage
def get_coverage_score(predicted_items, trainset_items):
    cov = recmetrics.coverage(predicted=predicted_items, catalog=trainset_items)
    return cov

#Function for getting personalization score
def get_personalization_score(predicted_items):
    pers = recmetrics.personalization(predicted_items)
    return pers