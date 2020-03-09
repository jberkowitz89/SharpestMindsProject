import pandas as pd
import time
import os
import sys

start_time = time.time()

os.chdir("/Users/josephberkowitz/Desktop/SharpestMinds/SharpestMindsProject/Nintendo_Project")

sys.path.append(os.getcwd())

import Nintendo.src.NintendoLife_Scraping as Nintendo

thread_name = "the_switch_eshop_recommendations"

thread_pages = Nintendo.get_max_pages_thread(thread_name)
thread_users = Nintendo.get_users(thread_name, thread_pages)

df = pd.DataFrame()
games_urls = []

for user in thread_users:
    max_pages = Nintendo.get_max_pages(user)
    user_games_ratings, urls = Nintendo.games_ratings_to_df(user, max_pages)
    df = df.append(user_games_ratings)
    games_urls.extend(urls)
    
games_urls = list(set(games_urls))
games_meta = Nintendo.get_game_metadata(games_urls)
    
print("--- %s seconds ---" % (time.time() - start_time))

#link3710_pages = Nintendo.get_max_pages("link3710")
#link3710_ratings = Nintendo.games_ratings_to_df("link3710", link3710_pages)

#Quarth_pages = Nintendo.get_max_pages("Quarth")
#Quarth_ratings = Nintendo.games_ratings_to_df("Quarth", Quarth_pages)   