#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 15:42:24 2020

@author: josephberkowitz
"""
from collections import defaultdict
from ml_metrics import average_precision
import recmetrics

def get_full_recommendation_list(recommendations):
    '''
    Function for creating a full list of all user recommendations.
    params: recommendations (dictionary of users and their recommendations)
    :returns recommendations_lst (list of list of all recommendations)
    '''
    recommendations_lst = []
    for user in recommendations.keys():
        user_item_lst = []
        for ir in recommendations[user]:
            item, rating = ir
            user_item_lst.append(item)
        recommendations_lst.append(user_item_lst)
    return recommendations_lst

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
    cov = recmetrics.prediction_coverage(predicted=predicted_items, catalog=trainset_items)
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

