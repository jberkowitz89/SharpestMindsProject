import os
import sys

sys.path.append(os.getcwd())

import Nintendo.src.NintendoLife_Scraping as Nintendo

link3710_pages = Nintendo.get_max_pages("link3710")
link3710_ratings = Nintendo.games_ratings_to_df("link3710", link3710_pages)

Quarth_pages = Nintendo.get_max_pages("Quarth")
Quarth_ratings = Nintendo.games_ratings_to_df("Quarth", Quarth_pages)   
