#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:43:51 2020

@author: josephberkowitz
"""
import json
import Nintendo.src.wrapper as wrapper

with open("config.JSON") as config_file:
    data = json.load(config_file)

model = str(data["model"])
threads = data["threads"]
param_grid = data["param_grid"]
sql_engine = data["sql_engine"]

raw_df, scraper_run = wrapper.run_scraper(threads, sql_engine)
cleaned_df = wrapper.clean_df(raw_df, sql_engine)

(recommendations, 
 predictions, 
 full_train, 
 full_test, 
 trainset, 
 testset, 
 test_rmse,
 recos_run) = wrapper.recommend(cleaned_df, model, param_grid, scraper_run, sql_engine)

evaluation_df = wrapper.evaluate(recommendations, predictions, full_train, 
                                 testset, test_rmse, recos_run, sql_engine)


