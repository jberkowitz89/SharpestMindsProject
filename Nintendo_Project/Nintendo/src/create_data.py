#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 15:46:54 2020

@author: josephberkowitz
"""

#Importing necessary modules
import pandas as pd
import datetime as dt
import numpy as np

from Nintendo.src import scraper

def create_raw_data_and_game_urls(threads):
    '''
    Function for creating raw data and game url list.
    Params: list of threads (list)
    : returns raw_df dataframe, games_urls_ids list, scraper_run str
    '''
    raw_df = pd.DataFrame()
    games_and_urls = []

    for thread in threads:

        thread_pages = scraper.get_max_pages_thread(thread)
        thread_users = scraper.get_users(thread, thread_pages)

        for user in thread_users:
            max_pages = scraper.get_max_pages(user)
            user_games_ratings, urls = scraper.games_ratings_to_df(user, max_pages)
            raw_df = raw_df.append(user_games_ratings)
            games_and_urls.extend(urls)
            print("dataframe length: ", len(raw_df))

    raw_df = raw_df.assign(game_id=(raw_df['game']).astype('category').cat.codes)
    raw_df = raw_df.assign(user_id=(raw_df['username']).astype('category').cat.codes)
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
    games_meta = scraper.get_game_metadata(games_urls_ids)
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