#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 07:17:21 2020

@author: josephberkowitz
"""

import pandas as pd
import time
import os
import sys

start_time = time.time()

os.chdir("/Users/josephberkowitz/Desktop/SharpestMinds/SharpestMindsProject/Nintendo_Project")

sys.path.append(os.getcwd())

import Nintendo.src.NintendoLife_Scraping as Nintendo

threads = ["the_switch_eshop_recommendations", "what_do_you_think_the_nx_is_poll", 
           "the_multiplayer_match_organisation_thread", "super_mario_maker_2_level_sharing",
           "friend_exchange_-_share_friend_codes_for_switch_multiplayer_matches",
           "question_about_new_subscrition_system"]

df = pd.DataFrame()
games_urls = []

for thread in threads:
    
    thread_pages = Nintendo.get_max_pages_thread(thread)
    thread_users = Nintendo.get_users(thread, thread_pages)

    for user in thread_users:
        max_pages = Nintendo.get_max_pages(user)
        user_games_ratings, urls = Nintendo.games_ratings_to_df(user, max_pages)
        df = df.append(user_games_ratings)
        games_urls.extend(urls)
        print(len(df))
        
games_urls = list(set(games_urls))
#games_meta = Nintendo.get_game_metadata(games_urls)
    
print("--- %s seconds ---" % (time.time() - start_time))