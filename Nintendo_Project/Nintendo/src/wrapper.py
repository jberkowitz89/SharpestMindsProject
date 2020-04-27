#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 17:41:52 2020

@author: josephberkowitz
"""
#Importing necessary modules
from sqlalchemy import create_engine
import datetime as dt
import pandas as pd

#Importing custom modules
from Nintendo.src import create_data, clean_data, modeling, evaluation

def run_scraper(threads, sql_engine):
    '''Wrapper Function for running the scraper portion of my recommender system.
    params: threads (list of threads), sql_engine (sql connectkon engine)
    :returns: raw_df, game_metadata, cleaned_df
    Needs scraper.py module dependency to work correctly
    '''
    engine = create_engine(sql_engine)
    
    raw_df, games_urls_ids, scraper_run = create_data.create_raw_data_and_game_urls(threads)
    
    raw_df.to_sql('raw_data', con=engine, if_exists="append")
    print('raw dataframe loaded to sql')
    
    game_metadata = create_data.create_meta_data(games_urls_ids, scraper_run)
    
    game_metadata.to_sql('game_metadata', con=engine, if_exists="append")
    print('metadata loaded to sql')
    
    return raw_df, scraper_run

def clean_df(raw_df, engine):
    '''Wrapper Function for the data cleaning portion of my recommender system.
    params: raw_df (raw dataframe of user, item, rating data)
    :returns: cleaned_df
    '''
    cleaned_df = clean_data.fill_no_score(raw_df, 'rating', 'username')
    cleaned_df.to_sql('cleaned_data', con=engine, if_exists="append")
    print('cleaned dataframe loaded to sql')
    return cleaned_df

def recommend(cleaned_df, model, param_grid, scraper_run, engine):
    '''
    Wrapper Function for the modeling portion of my recommender system.
    params: cleaned_df (cleaned dataframe of user, item, rating data), model (model name),
    param_grid, scraper run, 
    returns: recommendations (dictionary), predictions (dataframe), fulltrain (full train dataset),
    full_test (full testset), trainset, testset, test_rmse)
    '''
    surprise_data = modeling.create_surprise_dataset(cleaned_df, 'username', 'game', 'rating', (1,10))
    gs_results, gs_run, best_params = modeling.run_grid_search(surprise_data, model, param_grid, scraper_run)
    print(best_params)
    gs_results.to_sql('tuning', con=engine, if_exists="append")
    print('grid search results loaded to sql')
    
    #Creating full train and test
    full_train = modeling.build_full_train(surprise_data)
    full_test = modeling.build_full_testset(surprise_data)
    
    ##Creating Predictions
    trainset, testset = modeling.create_train_and_test(surprise_data, 0.25)
    svd_fit, predictions, test_rmse = modeling.run_model(model, trainset, testset, best_params)
    
    #Creating interaction matrix
    interactions = modeling.create_interaction_matrix(cleaned_df, 'username', 'game', 'rating')
    
    #Creating user and item dicts
    user_dict = modeling.create_user_dict(interactions, full_train)
    item_dict = modeling.create_item_dict(interactions, full_train)
    
    #Filling Interactions df
    interactions, known_items = modeling.fill_interaction_matrix(interactions, full_train, user_dict, item_dict, svd_fit)
    
    #Creating known items dataframe
    known_items_df = modeling.create_known_items_df(known_items, scraper_run)
    known_items_df.to_sql('known_items', con=engine, if_exists="append")
    print('known items loaded to sql')
    
    #Creating recommendations dict
    recommendations = modeling.create_recommendations_dict(interactions, known_items, n=10)
    
    #Creating recommendations df
    recommendations_df, recos_run = modeling.create_recommendations_df(recommendations)
    recommendations_df.to_sql('recommendations', con=engine, if_exists="append")
    print('recommendations loaded to sql')
    
    return recommendations, predictions, full_train, full_test, trainset, testset, test_rmse, recos_run

def evaluate(recommendations, predictions, full_train, testset, test_rmse, recos_run, engine):
    '''
    Wrapper Function for the evaluation portion of the recommendation engine
    '''
    #Creating full recommendations list

    full_recommendations_lst = evaluation.get_full_recommendation_list(recommendations)

    #Creating Evaluation dict
    top_n_predictions = evaluation.get_top_n(predictions, 10)
    full_testset = evaluation.create_testset_dict(testset)
    all_items = evaluation.all_trainset_items(full_train)
    
    evaluation_metrics = {}
    evaluation_metrics["run_time"] = dt.datetime.now()
    evaluation_metrics["rmse"] = test_rmse
    evaluation_metrics["mapk"] = evaluation.get_mapk(top_n_predictions, full_testset)
    evaluation_metrics["mark"] = evaluation.get_mark(top_n_predictions, full_testset, 10)
    evaluation_metrics["coverage"] = evaluation.get_coverage_score(full_recommendations_lst, all_items)
    evaluation_metrics["personalization"] = evaluation.get_personalization_score(full_recommendations_lst)
    evaluation_metrics["recos_run"] = recos_run
    
    evaluation_df = pd.DataFrame(evaluation_metrics, index=[0])
    evaluation_df.to_sql('evaluation', con=engine, if_exists="append")
    print('evaluation dataframe loaded to sql')
    
    return evaluation_df
    
    
    
    
    
    