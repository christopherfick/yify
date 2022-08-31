from database import MovieTable, href_table, DataBaseManager, DataBase

from tqdm import tqdm

import time

import os
from pathlib import Path

# Create data dir if none exists
data = Path(os.path.realpath(__file__)).parents[0]/'data'
if not os.path.exists(data):
    os.mkdir(data)

# Instantiate objects to help with management of databases
href_table = href_table(data/"href.db", "href")
movie_table = MovieTable(data/"movie.db", "movie")

# # Load initial hrefs from 100 yiffy pages, if href database empty
# href_table.load_hrefs(page_end = 100)

# # Load movie data from hrefs in href database
# hrefs = href_table.fetch_hrefs()
# movie_table.load_movies(hrefs)


# Once databases loaded, Update (if any) with latest released content
manager = DataBaseManager(href_table, movie_table)
manager.update_databases()

# Close database connection
href_table.conn.close()
movie_table.conn.close()