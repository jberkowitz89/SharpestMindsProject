# Building a Nintendo Switch Game Recommender From Scratch

In this project, I used Python to build an end-to-end recommender system for Nintendo Switch games.

With over 2300 games available to download on the current Nintendo Switch eShop, finding a new game to play and download can be overwhelming. While the eShop does have a few easy methods for finding new games, unless you are searching for something specific, it may be difficult for some to find games to play in the current iteration of the eShop. The current eShop home page layout is depicted below:
![](images/eshop_home.png)
As you can see, while there are ways to find featured games, recent releases, best sellers and games on sale, the eShop page is very generic. There are no elements of personalization recommendation besides what is popular, new or on sale. 
I believe that adding game recommendations to the Switch eShop can help Switch owners find more to play.

## Data Collection
As Nintendo themselves doesn't offer any data around users and their gaming habits, I looked to NintendoLife.com, a popular Nintendo fan website, to find data to build my recommender system. NintendoLife's site offers Nintendo news, game reviews, opinion articles, as well as the ability for users to rate games, create a profile displaying their game collection, and interact with other users on forums. 
To begin the data collection process, we start by scraping NintendoLife's forums for usernames. The forums contain thousands of posts from different users:
![](images/nintendolife_forum2.png)
Once users are collected, we scrape games and ratings from each user's page. An example of a user page is shown here:
![](images/nintendolife_user.png)
This scraping process provides us with a robust dataset of users, games and ratings, which we can use to train our recommender system model. We also collect metadata about each game, including the game's genre, price, developer and release date. Game metadata may be used in a future implementation of the recommender system model that includes features about our content (in this case, games).

