#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 16:23:36 2020

@author: josephberkowitz
"""
import time
import os
import sys
import pandas as pd

start_time = time.time()

os.chdir("/Users/josephberkowitz/Desktop/SharpestMinds/SharpestMindsProject/Nintendo_Project")

sys.path.append(os.getcwd())
import Nintendo.src.NintendoLife_utils as Utils
from surprise import SVD
import datetime as dt

import psycopg2
import sqlalchemy
from sqlalchemy import create_engine

 #Creating Raw DF
threads = ["the_switch_eshop_recommendations",
           "the_multiplayer_match_organisation_thread", "super_mario_maker_2_level_sharing",
            "friend_exchange_-_share_friend_codes_for_switch_multiplayer_matches",
           "question_about_new_subscrition_system"]


# =============================================================================
# threads = ["the_switch_eshop_recommendations"]
# =============================================================================


raw_df, games_urls_ids, scraper_run = Utils.create_raw_data_and_game_urls(threads)

#Creating Metadata DF
game_metadata = Utils.create_meta_data(games_urls_ids, scraper_run)

#Creating Cleaned DF
cleaned_df = Utils.fill_no_score(raw_df, "Rating", "User")

#Creating gs_results df
surprise_data = Utils.create_surprise_dataset(cleaned_df, "User", "Game", "Rating", (1,10))

param_grid = {"n_factors": [20, 50, 100, 150], "n_epochs": [20, 30, 50],
              "lr_all": [0.002, 0.005, 0.007, 0.01], "reg_all": [0.02, 0.05, 0.1]}

gs_results, gs_run, best_params = Utils.run_grid_search(surprise_data, SVD, param_grid, scraper_run)

#Creating Predictions df
trainset, testset = Utils.create_train_and_test(surprise_data, 0.25)
predictions, test_rmse = Utils.run_svd(trainset, testset, best_params)

preds_df, pred_run = Utils.create_preds_df(predictions, gs_results, gs_run)

#Creating Evaluation dict
top_n_predictions = Utils.get_top_n(predictions, 10)
full_testset = Utils.create_testset_dict(testset)
all_items = Utils.all_trainset_items(trainset)
full_item_list, full_predicted_item_list = Utils.get_ordered_items_and_predictions(full_testset, top_n_predictions)

evaluation_metrics = {}
evaluation_metrics["timestamp"] = dt.datetime.now()
evaluation_metrics["rmse"] = test_rmse
evaluation_metrics["mapk"] = Utils.get_mapk(top_n_predictions, full_testset)
evaluation_metrics["mark"] = Utils.get_mark(top_n_predictions, full_testset, 10)
evaluation_metrics["coverage"] = Utils.get_coverage_score(top_n_predictions, all_items)
evaluation_metrics["personalization"] = Utils.get_personalization_score(full_predicted_item_list)
evaluation_metrics["pred_run"] = pred_run

evaluation_df = pd.DataFrame(evaluation_metrics, index=[0])

print("--- %s seconds ---" % (time.time() - start_time))


#Inserting into DB
engine = create_engine('postgresql+psycopg2://josephberkowitz:@localhost:5432/nintendo')

raw_df.to_sql('raw_data', con=engine, if_exists="append")

game_metadata.to_sql('game_metadata', con=engine, if_exists="append")

cleaned_df.to_sql('cleaned_data', con=engine, if_exists="append")
 
gs_results.to_sql('tuning', con=engine, if_exists="append")
 
preds_df.to_sql('predictions', con=engine, if_exists="append")
 
evaluation_df.to_sql('evaluation', con=engine, if_exists="append")

