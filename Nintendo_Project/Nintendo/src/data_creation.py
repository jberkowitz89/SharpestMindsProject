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
import datetime as dt
from sqlalchemy import create_engine
import json
start_time = time.time()

os.chdir("/Users/josephberkowitz/Desktop/SharpestMinds/SharpestMindsProject/Nintendo_Project")

sys.path.append(os.getcwd())

with open("config.JSON") as config_file:
    data = json.load(config_file)

model = str(data["model"])
threads = data["threads"]
param_grid = data["param_grid"]
sql_engine = data["sql_engine"]

print(model)


import Nintendo.src.NintendoLife_utils as Utils


 #Creating Raw DF

raw_df, games_urls_ids, scraper_run = Utils.create_raw_data_and_game_urls(threads)

#Creating Metadata DF
game_metadata = Utils.create_meta_data(games_urls_ids, scraper_run)

#Creating Cleaned DF
cleaned_df = Utils.fill_no_score(raw_df, "rating", "user")

#Creating gs_results df
surprise_data = Utils.create_surprise_dataset(cleaned_df, "user", "game", "rating", (1,10))


gs_results, gs_run, best_params = Utils.run_grid_search(surprise_data, model, param_grid, scraper_run)
print(best_params)

#Creating Predictions df
trainset, testset = Utils.create_train_and_test(surprise_data, 0.25)
predictions, test_rmse = Utils.run_model(model, trainset, testset, best_params)

preds_df, pred_run = Utils.create_preds_df(predictions, gs_results, gs_run)

#Creating Evaluation dict
top_n_predictions = Utils.get_top_n(predictions, 10)
full_testset = Utils.create_testset_dict(testset)
all_items = Utils.all_trainset_items(trainset)
full_item_list, full_predicted_item_list = Utils.get_ordered_items_and_predictions(full_testset, top_n_predictions)

evaluation_metrics = {}
evaluation_metrics["run_time"] = dt.datetime.now()
evaluation_metrics["rmse"] = test_rmse
evaluation_metrics["mapk"] = Utils.get_mapk(top_n_predictions, full_testset)
evaluation_metrics["mark"] = Utils.get_mark(top_n_predictions, full_testset, 10)
evaluation_metrics["coverage"] = Utils.get_coverage_score(full_predicted_item_list, all_items)
evaluation_metrics["personalization"] = Utils.get_personalization_score(full_predicted_item_list)
evaluation_metrics["pred_run"] = pred_run

evaluation_df = pd.DataFrame(evaluation_metrics, index=[0])


#Inserting into DB

engine = create_engine(sql_engine)
 
raw_df.to_sql('raw_data', con=engine, if_exists="append")
 
game_metadata.to_sql('game_metadata', con=engine, if_exists="append")

cleaned_df.to_sql('cleaned_data', con=engine, if_exists="append")
 
gs_results.to_sql('tuning', con=engine, if_exists="append")
 
preds_df.to_sql('predictions', con=engine, if_exists="append")
 
evaluation_df.to_sql('evaluation', con=engine, if_exists="append")

print("--- %s seconds ---" % (time.time() - start_time))

