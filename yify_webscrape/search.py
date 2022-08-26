import pandas as pd
import numpy as np


class BasicSearch:
    """
    Fillters content based on symmetric defference between strings
    Note:
        Works well for small databases, effictivness drops as size increases.
    """

    def __init__(self, query):
        self.query = query

    def search_dataframe(self, dataframe, column):
        correlation = "correlation"
        dataframe[correlation] = [
            self.calc_correlation(self.query, row) for row in dataframe[column]
        ]
        dataframe.sort_values(correlation, inplace=True)
        return dataframe.drop(correlation, axis=1)

    @staticmethod
    def calc_correlation(seq_1, seq_2):
        seq_1, seq_2 = set(seq_1.lower()), set(seq_2.lower())
        return len(seq_1.symmetric_difference(seq_2))
