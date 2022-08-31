# Data collection phase

- main.py:    
"Fine-tune data collection from yts site"


- database.py:  
"Main objects for DataBase creation, updating and maintenance"


- webscrape.py:  
"Responsible for accessing online site and scraping data from each page"

---

## DataBase format once extracted from yts site:

- title: Names of movies (duplicates and errors)
- genre: **List** of genre for each title
- year: Release year for movie
- rating: Overall rating for each movie 
- href: URL to movie on yts site (duplicates with slight variations in names)
  
Note:  
- Some movies contain the same title, year, and rating but share different hrefs