#importing necessary modules
import pandas as pd
import datetime as dt
import numpy as np
#Importing surprise modules
from surprise import Reader, accuracy, Dataset
from surprise import SVD
from surprise.model_selection import train_test_split
#Importing evaluation modules
from collections import defaultdict
from app import app

def add_new_games(df, games):
    global_median = df['rating'].median()

    for i in range(len(games)):
        new_row = pd.Series({'user': 'new_user', 'game': games[i], 'rating': global_median})
        if i == 0:
            new_df = df.append(new_row, ignore_index=True)
        else:
            new_df = new_df.append(new_row, ignore_index=True)

    return new_df

def new_model(df, rating_scale, params):
    reader = Reader(rating_scale=rating_scale)
    surprise_data = Dataset.load_from_df(df[['user', 'game', 'rating']], reader)

    trainset, testset = train_test_split(surprise_data, 0.25)

    algo = SVD(n_factors=params["n_factors"], n_epochs=params["n_epochs"],
               lr_all=params["lr_all"], reg_all=params["reg_all"])
    svd_fit = algo.fit(trainset)

    return svd_fit

def new_user_predictions(df, model):
    interactions = df.groupby(['user', 'game'])['rating'] \
            .sum().unstack().reset_index(). \
            fillna(0).set_index('user')
    user_known = defaultdict(list)
    for index, value in interactions.loc['new_user'].items():
        if value != 0.0:
            user_known['new_user'].append(index)
        else:
            est = model.predict('new_user', index)[3]
            interactions.loc['new_user', index] = est

    top_10_recs = interactions.loc['new_user'].sort_values(ascending=False)[:10].index.tolist()

    return top_10_recs



