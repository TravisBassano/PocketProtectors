"""
awards.py

Helper module for determining fun "awards" based on manager statistics.

Usage example:

    awards = Awards()
    awards.run()
"""

import pandas as pd

from collections import defaultdict
from pathlib import Path


class Awards:
    """
    Core class for determining manager awards.

    """

    PROJ_ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = PROJ_ROOT_DIR / "data"

    def __init__(self):
        """
        Initialize Awards class.
        """

        self.df = pd.read_csv(self.DATA_DIR / 'data.csv')

        self.managers = self.df['manager'].unique()


    def run(self):
        """Determine all awards.

        """

        self.award_best_scores()
        self.award_favorite_team()

    def award_best_scores(self):
        """Identify managers that had the best/worst scorers for the week.
        """

        df = self.df

        managers = df["manager"].unique()
        seasons = df["season"].unique()
        weeks = df["week"].unique()

        max_scorer = dict.fromkeys(managers, 0)
        min_scorer = dict.fromkeys(managers, 0)

        for season in seasons:

            for week in weeks:

                slice = df[(df["season"] == season) & (df["week"] == week)]

                if slice.empty:
                    continue

                k_max = slice["max_player_score"].idxmax()
                k_min = slice["max_player_score"].idxmin()

                max_scorer[slice.loc[k_max, "manager"]] += 1
                min_scorer[slice.loc[k_min, "manager"]] += 1

        print(max_scorer)
        print(min_scorer)

    def award_favorite_team(self):
        """Identify the "favorite" team of each manager.

        Each manager's "favorite" team is determined by the total number
        of each rostered player's parent team.
        """
        df = self.df

        managers = df["manager"].unique()
        seasons = df["season"].unique()

        favorite_teams = dict()

        for manager in managers:

            player_teams_total = defaultdict(int)

            for season in seasons:

                slice = df[(df["manager"] == manager) & (df["season"] == season)]

                player_teams = slice["player_teams"]

                for player_team_list in player_teams:

                    for k, v in eval(player_team_list).items():
                        player_teams_total[k] += v

            player_teams_total = sorted(player_teams_total.items(), key=lambda x: x[1], reverse=True)

            favorite_teams[manager] = player_teams_total[0][0]

        print(favorite_teams)


if __name__ == "__main__":

    awards = Awards()