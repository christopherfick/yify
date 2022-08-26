from database import MovieTable, href_table, DataBaseManager, DataBase

from tqdm import tqdm

import time



href_table = href_table("data/href.db", "href")
movie_table = MovieTable("data/movie.db", "movie")


## Update databases with latest released content
manager = DataBaseManager(href_table, movie_table)
manager.update_databases()

href_table.conn.close()
movie_table.conn.close()
