import os
import sys
import pandas as pd

sys.path.append(os.getcwd())

import Nintendo.src.NintendoLife_Scraping as Nintendo

thread_pages = Nintendo.get_max_pages_thread("the_switch_eshop_recommendations")
thread_users = Nintendo.get_users("the_switch_eshop_recommendations", thread_pages)

df = pd.DataFrame()

for user in thread_users:
    max_pages = Nintendo.get_max_pages(user)
    user_games_ratings = Nintendo.games_ratings_to_df(user, max_pages)
    df = df.append(user_games_ratings)

#link3710_pages = Nintendo.get_max_pages("link3710")
#link3710_ratings = Nintendo.games_ratings_to_df("link3710", link3710_pages)

#Quarth_pages = Nintendo.get_max_pages("Quarth")
#Quarth_ratings = Nintendo.games_ratings_to_df("Quarth", Quarth_pages)   
