#!/usr/bin/env python3

"""Pocket Protectors Fantasy Football Leage History

Leverages the YFPY (Yahoo Fantasy Sports API Wrapper) to read in league history
 and generate interesting historical plots from the data.

"""

__author__ = "Travis Bassano"
__copyright__ = "Copyright 2025, Pocket Protectors"
__license__ = "MIT"

from dotenv import load_dotenv

from src.awards import Awards
from src.contentgen import ContentGenerator
from src.query import Query
from src.plotting import Plotting

load_dotenv()


def main():
    q = Query()
    q.query_seasons()
    q.save_data()

    a = Awards()
    a.run()

    p = Plotting()
    p.run()

    c = ContentGenerator()
    c.generate_chart_data()
    c.generate_all_manager_pages()


if __name__ == "__main__":
    main()
