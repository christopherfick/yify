from bs4 import BeautifulSoup

import requests

import warnings


class MoviesHref:
    "Scrapes a list of movie hrefs from given page on Yify site"
    def __init__(self, page=1):
        self.page = page
        self.movies_href = self._load_movies_href()

    def _load_movies_href(self):
        page_url = f'https://yts.mx/browse-movies?page={self.page}'

        page_text = requests.get(page_url).text
        soup_page = BeautifulSoup(page_text, features="lxml")

        movies_href_on_page = [
            div.find("a")["href"]
            for div in 
            soup_page.find_all("div", class_="browse-movie-bottom")] 
        
        if not movies_href_on_page:
            warnings.warn("No movie hrefs on specified page")
        return movies_href_on_page


class Movie:
    """Scrapes information about movie, given movie href"""
    def __init__(self, href):
        if not isinstance(href, str):
            raise ValueError(f"Expected a string but got href of type '{type(href)}' instead")
        self.href = href
        self.info = self._get_info()
        

    def _get_info(self):
        movie_page_text = requests.get(self.href).text
        soup_movie = BeautifulSoup(movie_page_text, features="lxml")

        movie_info = soup_movie.find_all("div", id="movie-info")
        movie_info_dict = {}
        for info in movie_info:
            title_year_genre = [info.text.strip() for info in info.find("div", class_="hidden-xs") if info.text.strip()]
            rating = [float(rating.text.strip()) for rating in info.find("span", itemprop="ratingValue")][0]

            try:
                try:
                    movie_info_dict["year"] = int(title_year_genre[1].split()[0])
                except ValueError:
                    movie_info_dict["year"] = None
                    
                movie_info_dict["title"] = title_year_genre[0]
                movie_info_dict["genre"] = title_year_genre[2]

            except IndexError:
                warnings.warn(f"{self.href}Index Error Raised \ntitle_year_genre:{title_year_genre}")

            movie_info_dict["rating"] = rating
            movie_info_dict["href"] = self.href

        for key, value in movie_info_dict.items():
            if not value:
                if value is None:
                    warnings.warn(f"Values missing for key:'{key}' -- \n {movie_info_dict}")

        if not movie_info_dict:
            warnings.warn(f"{self.href} \n --broken href-- \n")
            return None 
        return movie_info_dict