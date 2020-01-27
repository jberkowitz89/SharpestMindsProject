# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

#importing necessary libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup

#Creating Function for getting max pages
def get_max_pages(user_name):
    """
    :params user_name: username
    : return max_page_tag: max numer of pages for user
    """
    
    #Setting parameters and getting soup for our user
    url = "https://www.nintendolife.com/users/" + user_name + "/games"
    r = requests.get(url) 
    html_text = r.text
    soup = BeautifulSoup(html_text, "html.parser")

    #try-except block for if a user only has one page
    try:
        pagination_tags = soup.findAll("a", {"class": "accent accent-bg-hover accent-border"}) #just pagination tags
        page_tag_numbers = []
        for tag in pagination_tags:
            page_tag_numbers.append(int(tag.contents[0]))
        max_page_tag = max(page_tag_numbers)
        return max_page_tag
    
    except:
        max_page_tag = 1
        return max_page_tag
    
#Creating Function for getting games and ratings into dataframe=
def games_ratings_to_df(user_name, max_pages):
    """
    :params user_name: user_name
    :params max_pages: max_pages from function get_max_pages()
    : return df: scraped pandas dataframe for user_name
    """
    
    #Setting up object holders
    cols = ["User", "Game", "Rating"]
    df = pd.DataFrame(columns=cols)
    games = []
    ratings = []
    
    #iterating through pages
    for page in range(1, max_pages+1):
        #Url is different if on first page rather than other pages
        if page == 1:
            #Setting parameters and getting first soup for our user
            url = "https://www.nintendolife.com/users/" + user_name + "/games"
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
            
            #Getting our game tags
            spans = soup.findAll("span")
            for i in range(len(spans)):
                #Try-except block for key-errors when filtering for class
                try:
                    #conditional for just tag types that are holding game titles
                    if spans[i]["class"] == ["title", "accent-hover"]:
                        games.append(spans[i].contents[0])
                        #Conditional for putting rating or no score - can explain how
                        if spans[i+2]["class"] == ["value"]:
                            ratings.append(spans[i+2].contents[0])
                        else:
                            ratings.append("No Score")
                except KeyError:
                    pass
            #appending no score for last game (if last game had no score)
            if len(games) > len(ratings):
                ratings.append("No Score")
        #Adding the rest of the url pages       
        else:
            #Setting parameters and getting first soup for our user
            url = "https://www.nintendolife.com/users/" + user_name + "/games?page=" + str(page)
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
            
            #Getting our game tags
            spans = soup.findAll("span")
            for i in range(len(spans)):
                #Try-except block for key-errors when filtering for class
                try:
                    #conditional for just tag types that are holding game titles
                    if spans[i]["class"] == ["title", "accent-hover"]:
                        games.append(spans[i].contents[0])
                        #Conditional for putting rating or no score - can explain how
                        if spans[i+2]["class"] == ["value"]:
                            ratings.append(spans[i+2].contents[0])
                        else:
                            ratings.append("No Score")
                except KeyError:
                    pass
            #appending no score for last game (if last game had no score)
            if len(games) > len(ratings):
                ratings.append("No Score")
    
    #Adding our games and ratings list to dataframe
    df["Game"] = games
    df["Rating"] = ratings
    df["User"] = user_name
    
    return df