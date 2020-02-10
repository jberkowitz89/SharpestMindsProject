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
    
#Creating Function for getting games and ratings into dataframe
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

#Function for getting the max number of pages for a thread
def get_max_pages_thread(thread_name):
    """
    :params thread_name: thread_name
    : return max_page_tag: max number of pages for thread
    """
    
    #Setting parameters and getting soup for our thread
    url = "https://www.nintendolife.com/forums/nintendo-switch/" + thread_name
    r = requests.get(url) 
    html_text = r.text
    soup = BeautifulSoup(html_text, "html.parser")

    #try-except block for if a thread only has one page
    try:
        pagination_tags = soup.findAll("a", {"class": "accent-border accent-bg-hover accent"}) #just pagination tags
        page_tag_numbers = []
        for tag in pagination_tags:
            page_tag_numbers.append(int(tag.contents[0]))
        max_page_tag = max(page_tag_numbers)
        return max_page_tag
    
    except:
        max_page_tag = 1
        return max_page_tag
    
#Function for getting all of the users from a thread
def get_users(thread_name, max_pages):
    '''Function for collecting all users from a thread. 
    Params: thread name (string), max number of pages
    : returns deduped_users: De-duplicated list of users'''
    
    users = []
    for i in range(max_pages):
        n_posts = i * 20
        if n_posts == 0:            
            #Setting parameters 
            url = "https://www.nintendolife.com/forums/nintendo-switch/" + thread_name
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
            
            #Getting user tags
            user_names = soup.findAll("a", {"class": "accent username"})
            for user in user_names:
                users.append(user.contents[0])

        else:           
            #Setting parameters 
            url = "https://www.nintendolife.com/forums/nintendo-switch/" + thread_name + "?start=" + str(n_posts)
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
            
            #Getting user tags
            user_names = soup.findAll("a", {"class": "accent username"})
            for user in user_names:
                users.append(user.contents[0])
                
    #Deduplicating List
    deduped_users = list(set(users))
    return deduped_users

#Function for getting max pages from the games page
def get_max_pages_gamepage(url):
    """
    Function for getting max number of pages from a game page
    :params url: url for games page
    : returns max_page_tag: max numer of pages for games page
    """

    r = requests.get(url) 
    html_text = r.text
    soup = BeautifulSoup(html_text, "html.parser")

    #first pass
    pagination_tags = soup.findAll("a", {"class": "accent accent-bg-hover accent-border"}) #just pagination tags
    page_tag_numbers = [1]
    for tag in pagination_tags:
        page_tag_numbers.append(int(tag.contents[0]))
    max_page_tag = max(page_tag_numbers)

    #Every pass therafter
    empty_checker = []
    while not empty_checker:
        new_url = url + "&page=" + str(max_page_tag)
        r = requests.get(new_url) 
        html_text = r.text
        soup = BeautifulSoup(html_text, "html.parser")

        pagination_tags = soup.findAll("a", {"class": "accent accent-bg-hover accent-border"})
        empty_checker = soup.findAll("li", {"class": "empty"})

        for tag in pagination_tags:
            if int(tag.contents[0]) not in page_tag_numbers:
                page_tag_numbers.append(int(tag.contents[0]))
        max_page_tag = max(page_tag_numbers)
    
    return max_page_tag

#Function for getting URLs for each game
def get_game_urls(url, max_pages):
    '''Function for getting list of game urls from games page on Nintendolife.com
    params: url: URL of games page - can be filtered for specific system
    params: max_pages: maximum number of pages for games page
    : returns: list of urls for each game
    '''
    game_urls = []

    for page in range(1, max_pages+1):
        if page == 1:
            url = url
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
    
            #Getting Game Tags
            game_tags = soup.findAll("a", {"class": "title accent-hover"})
            for game in game_tags:
                game_link = game.attrs["href"]
                if game_link[0:5] == "games":
                    game_urls.append(game_link)
                else:
                    pass
        else:
            url = url + "&page=" + str(page) 
            r = requests.get(url) 
            html_text = r.text
            soup = BeautifulSoup(html_text, "html.parser")
    
            #Getting Game Tags
            game_tags = soup.findAll("a", {"class": "title accent-hover"})
            for game in game_tags:
                game_link = game.attrs["href"]
                if game_link[0:5] == "games":
                    game_urls.append(game_link)
                else:
                    pass
    return game_urls

def get_game_metadata(games_list):
    '''Function for getting metadata for games.
    :params game_list: list of game urls
    : returns: dataframe with game metadata
    '''
    #List for appending game metadata
    game_metadata = []

    for game in games_list:
        url = "http://www.nintendolife.com/" + game
        r = requests.get(url)
        html_text = r.text
        soup = BeautifulSoup(html_text, "html.parser")

        #Getting Game Name
        game_tags = soup.findAll("h1")
        for tag in game_tags:
            game_title = tag.contents[0].contents[0]

        #Gets us platform, developer, publisher, number of players
        info = soup.findAll("dd", {"class": "first"})
        info_list=[]
        for tag in info:
            if len(tag.contents) == 1:
                info_list.append(tag.contents[0])
        try:
            platform = info_list[0]
            developer = info_list[1]
            publisher = info_list[2]
        except:
            publisher = "N/A"

        #Getting genre
        genre_tags = soup.findAll("a")
        genre_list = []
        for element in genre_tags:
            if "genre" in element.attrs["href"]:
                genre_list.append(element.contents[0])

        keys = ["game_title", "platform", "developer", "publisher", "genre"]
        values = [game_title, platform, developer, publisher, genre_list]

        game_dict = dict(zip(keys, values))
        game_metadata.append(game_dict)
        
        if len(game_metadata) % 50 == 0:
            print(len(game_metadata))
        
    df = pd.DataFrame(game_metadata)
    return df

