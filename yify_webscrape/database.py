import sqlite3 as sql
import webscrape

import warnings

from tqdm import tqdm


class DataBase:
    """
    Base object for database connection and cursor creation.
    
    Attributes:
        conn: sqlite3.Connection 
        cursor: sqlite3.Cursor 
    """
    def __init__(self, database:str):
        self.conn = sql.connect(database)
        self.cursor = self.conn.cursor()

        self.conn.execute('PRAGMA synchronous = 0;')


class Table(DataBase):
    """
    Base object for handling tables within a database, child object of DataBase.

    Attributes:
        name(str): table name
    """
    def __init__(self, database:str, name:str):
        super().__init__(database)
        self.name = name

    def delete_table(self):
        self.cursor.execute(f"""
                DROP TABLE IF EXISTS {self.name};
                """)

    def create_table(self):
        print("original function called 'create table'")
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name}
                (
                    column TEXT
                );
            """
            )
        self.conn.commit()
    
    def re_init(self):
        self.delete_table()
        self.create_table()

    def fetch_hrefs(self):
        try:
            self.cursor.execute(f"""
                SELECT href FROM {self.name}
                """)
            hrefs = [href[0] for href in self.cursor.fetchall()]
            if hrefs:
                return hrefs
            warnings.warn(f"No hrefs found in {self.name}")
            return None
        except sql.OperationalError:
            self.re_init()



class href_table(Table):
    """
    Manages href database, creation, loading, updating

    Attributes:
        name(str): Name of the table

    """
    def __init__(self, database:str, name:str):
        super().__init__(database, name)

    def create_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name}
                (
                href TEXT
                );
            """)
        self.conn.commit()

    def load_hrefs(self, page_end):
        print("\nReloading hrefs from yiffy site")
        self.re_init()
        
        page_range = range(1, page_end + 1)
        for page in tqdm(page_range):
            hrefs = webscrape.MoviesHref(page)
            for href in hrefs.movies_href:
                self.insert_href(href)
    
    def insert_href(self, href):
        self.cursor.execute(f"""
                INSERT INTO {self.name} (href)
                    VALUES ("{href}")
        """)
        self.conn.commit()       

    def update(self, new_hrefs, current_hrefs):
        concat_hrefs = new_hrefs + current_hrefs
        if not concat_hrefs:
            raise ValueError("No href values found")
            
        self.re_init()
        for href in concat_hrefs:
            self.insert_href(href)

    def remove_href(self, href):
        self.cursor.execute(f"""
                DELETE FROM {self.name} WHERE href = "{href}";
        """)
        self.conn.commit()


class MovieTable(Table):
    def __init__(self, database:str, name:str):
        super().__init__(database, name)
        self.broken_hrefs = []

    def create_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name}
                (
                title TEXT, 
                year INT, 
                genre TEXT, 
                rating FLOAT,
                href TEXT
                );
            """)
        self.conn.commit()

    def load_movies(self, hrefs):
        print("\nLoading movies")
        missing_hrefs = self._find_missing_hrefs(hrefs)
        for href in tqdm(missing_hrefs):
            movie = webscrape.Movie(href)
            self.insert_movie(movie)

    def _find_missing_hrefs(self, hrefs):
        movie_hrefs = self.fetch_hrefs()
        if not movie_hrefs:
            return hrefs
        else:
            return [href for href in hrefs if href not in movie_hrefs]
        
    def insert_movie(self, Movie):
        if not Movie.info:
            self.broken_hrefs.append(Movie.href)
            return
        title = Movie.info.get("title")
        year = Movie.info.get("year")
        genre = Movie.info.get("genre")
        rating = Movie.info.get("rating")
        href = Movie.info.get("href")

        self.cursor.execute(f"""
                INSERT INTO movie (title, year, genre, rating, href)
                    VALUES ("{title}", "{year}", "{genre}", "{rating}", "{href}")
        """)
        self.conn.commit()

    def drop_broken_hrefs(self, href_table):
        for broken in self.broken_hrefs:
            href_table.remove_href(broken)

    def update(self, new_hrefs):
        """
        Inserts new movies from hrefs to database
        
        Parameters:
            new_hrefs: list containing new hrefs to insert into database

        Note:
            This method does not check current movie db for copies, if inserting make sure movies
            are not already in database.
        """
        print("Updating movies")
        for href in tqdm(new_hrefs):
            movie = webscrape.Movie(href)
            self.insert_movie(movie)


    
class DataBaseManager:
    """Convient object for managing href and movie tables"""
    def __init__(self, href_table, movie_table):
        self.movie_table = movie_table
        self.href_table = href_table

    def update_databases(self):
        """Append latest movies released from Yify site to databases"""
        pre_loaded_hrefs = self.href_table.fetch_hrefs()
        new_hrefs = self._get_new_hrefs(pre_loaded_hrefs)

        if not new_hrefs:
            warnings.warn("Nothing to update")
        else:
            self.movie_table.update(new_hrefs)
            self.href_table.update(new_hrefs, pre_loaded_hrefs)


    @staticmethod
    def _get_new_hrefs(table_hrefs):
        """Search yify latest until href matches first_href in list"""
        first_href = table_hrefs[0]

        new_hrefs = []
        page = 1
        while True:
            hrefs = webscrape.MoviesHref(page).movies_href
            for href in hrefs:
                if href == first_href:
                    return new_hrefs                 
                else:
                    new_hrefs.append(href)
            page +=1