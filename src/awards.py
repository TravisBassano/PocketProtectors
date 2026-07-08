"""
awards.py

Helper module for determining fun "awards" based on manager statistics.

Usage example:

    awards = Awards()
    awards.run()
"""
import json
import pandas as pd

from collections import defaultdict, Counter
from pathlib import Path


class Awards:
    """
    Core class for determining manager awards.

    """

    PROJ_ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = PROJ_ROOT_DIR / "data"
    WEB_DATA_DIR = PROJ_ROOT_DIR / "_data"

    def __init__(self):
        """
        Initialize Awards class.
        """

        self.df = pd.read_csv(self.DATA_DIR / 'data.csv')

        self.accolades = defaultdict(list)

    def run(self):
        """Determine all awards.

        """

        self.award_best_scores()
        # self.award_favorite_team()
        self.award_champion_records_by_week()

    def award_yearly_champions(self):
        """
        """
        df = pd.read_csv(self.DATA_DIR / 'standings.csv')

        seasons = [int(_) for _ in df['season'].unique()]

        awards = defaultdict(list)

        for season in seasons:

            df_sea = df[df['season'] == season]

            df_slice = df_sea[df_sea['rank'] == 1].reset_index()
            manager = df_slice.loc[0, "manager"]
            awards[manager].append({
                "title": "League Champion",
                "year": season,
                "style": "gold"
                }
            )

            df_slice = df_sea[df_sea['rank'] == 2].reset_index()
            manager = df_slice.loc[0, "manager"]
            awards[manager].append({
                "title": "Runner Up",
                "year": season,
                "style": "silver"
                }
            )

            df_slice = df_sea[df_sea['rank'] == 3].reset_index()
            manager = df_slice.loc[0, "manager"]
            awards[manager].append({
                "title": "Podium Achiever",
                "year": season,
                "style": "bronze"
                }
            )

            df_slice = df_sea[df_sea['rank'] == 7].reset_index()
            manager = df_slice.loc[0, "manager"]
            awards[manager].append({
                "title": "Consolation Bracket Hero",
                "year": season,
                }
            )

        with open(self.WEB_DATA_DIR / "awards.json", "w") as f:
            json.dump(awards, f, indent=3)

    def award_champion_records_by_week(self):
        """Determine the set of records held by the eventual league champion
        week by week.
        """

        df = self.df
        seasons = df["season"].unique()

        standings = pd.read_csv(self.DATA_DIR / 'standings.csv')

        champions = {}
        for season in seasons:
            s = standings[
                (standings["season"] == season) &
                (standings["rank"] == 1)
            ].reset_index()

            champions[int(season)] = s.loc[0, "manager"]

        # print(champions)
        champ_records = defaultdict(lambda: (0, 0))

        WEEKS = range(1, 14)

        champ_record_sets = [set() for _ in WEEKS]
        champ_record_list = [list() for _ in WEEKS]
        # print(champ_record_sets)

        for season in seasons:

            for k, week in enumerate(WEEKS):

                s = df[
                    (df["season"] == season) &
                    (df["manager"] == champions[season]) &
                    (df["week"] == week)
                ].reset_index()

                if s.shape[0] != 1:
                    print("PARSE ERROR")
                    print(season)
                    print(week)
                    exit(1)

                wins = champ_records[season][0]
                losses = champ_records[season][1]

                if (wins, losses) == (1, 3):
                    print(f"{season} - {champions[season]}")

                if s.loc[0, "points"] > s.loc[0, "opp_points"]:
                    wins += 1
                else:
                    losses += 1

                champ_records[season] = (wins, losses)

                champ_record_sets[k].add((wins, losses))
                champ_record_list[k].append((wins, losses))

        for k, week in enumerate(WEEKS):
            print(f"Week {week}: {champ_record_sets[k]}")

            counts = Counter(champ_record_list[k])

            for element, count in counts.items():
                print(f"{element}: {count}")

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

        for manager in managers:
            self.accolades[manager].append(
                {
                    "title": "Single Week Highest Scoring Player",
                    "value": f"{max_scorer[manager]} weeks",
                    "style": "waiver",
                }
            )

            self.accolades[manager].append(
                {
                    "title": "Single Week Lowest Scoring Player",
                    "value": f"{min_scorer[manager]} weeks",
                    "style": "waiver",
                }
            )

    def award_highest_scorer(self):
        """
        """

        df = self.df

        for k, row in df.iterrows():

            roster = eval(row['roster'])

            filt_roster = []

            # Exclude positions (like DEF, or K)
            for player in roster:
                if player[2] not in ["K", "BN", "DEF"]:
                    filt_roster.append(player)

            # Highest scorer
            scorer = max(filt_roster, key=lambda item: item[3])

            df.loc[k, 'min_player_name'] = scorer[0]
            df.loc[k, 'min_player_score'] = scorer[3]

            # Lowest scorer
            scorer = min(filt_roster, key=lambda item: item[3])

            df.loc[k, 'min_player_name'] = scorer[0]
            df.loc[k, 'min_player_score'] = scorer[3]

        for season in df["season"].unique():
            ssn_slice = df[df["season"] == season].reset_index()

            max_score_index = ssn_slice['max_player_score'].idxmax()
            min_score_index = ssn_slice['min_player_score'].idxmin()

            max_score_mgr = ssn_slice.loc[max_score_index, 'manager']
            min_score_mgr = ssn_slice.loc[min_score_index, 'manager']

            max_score_wk = ssn_slice.loc[max_score_index, 'week']
            min_score_wk = ssn_slice.loc[min_score_index, 'week']

            max_score = ssn_slice.loc[max_score_index, 'max_player_score']
            min_score = ssn_slice.loc[min_score_index, 'min_player_score']

            max_scorer = ssn_slice.loc[max_score_index, 'max_player_name']
            min_scorer = ssn_slice.loc[min_score_index, 'min_player_name']

            self.accolades[max_score_mgr].append(
                {
                    "title": f"Highest Single Game Scorer ({season})",
                    "value": f"{max_scorer} / Week {max_score_wk} / {max_score}pts",
                    "style": "waiver",
                }
            )

            self.accolades[min_score_mgr].append(
                {
                    "title": f"Lowest Single Game Scorer ({season})",
                    "value": f"{min_scorer} / Week {min_score_wk} / {min_score}pts",
                    "style": "waiver",
                }
            )

    # def award_favorite_team(self):
    #     """Identify the "favorite" team of each manager.

    #     Each manager's "favorite" team is determined by the total number
    #     of each rostered player's parent team.
    #     """

    def award_all_favorites(self):
        """
        """

        team_counts = dict()

        with open(self.WEB_DATA_DIR / 'team-counts.json', "w") as f:

            for manager in self.df['manager'].unique():
                teams = self.award_favorite_player(manager, f)

                team_counts[manager] = teams

                self.award_manager_mvp(manager)

            json.dump(
                team_counts,
                f,
                indent=3,
            )

    def award_favorite_player(self, manager: str, f):
        """Identify the "favorite" player & team of each manager.

        Each manager's "favorite" is determined by the total number
        of weeks rostered by the manager.
        """

        players = defaultdict(int)
        teams = defaultdict(int)

        df = self.df[self.df['manager'] == manager].reset_index()

        for k, row in df.iterrows():

            roster = eval(row['roster'])

            for r in roster:

                if r[1] == "N/A":
                    continue

                players[r[0]] += 1
                teams[r[1]] += 1

        fav_player = max(players, key=players.get)

        self.accolades[manager].append(
            {
                "title": "Favorite Player",
                "value": f"{fav_player} ({players[fav_player]} starts)",
                "style": "draft",
            }
        )

        fav_team = max(teams, key=teams.get)
        dis_team = min(teams, key=teams.get)

        self.accolades[manager].append(
            {
                "title": "Favorite Team",
                "value": f"{fav_team} ({teams[fav_team]} starts)",
                "style": "draft",
            }
        )

        self.accolades[manager].append(
            {
                "title": "Despised Team",
                "value": f"{dis_team} ({teams[dis_team]} starts)",
                "style": "mvp",
            }
        )

        teams = sorted(teams.items(), key=lambda item: item[1], reverse=True)

        return teams

    def award_manager_mvp(self, manager):
        """
        """

        df = self.df[self.df['manager'] == manager].reset_index()

        all_time_mvps = defaultdict(int)

        for season in df['season'].unique():

            mvps = defaultdict(int)
            lvps = defaultdict(int)
            lvpss = defaultdict(int)

            ssn = df[df['season'] == season]

            for k, row in ssn.iterrows():

                roster = eval(row['roster'])

                for r in roster:

                    if r[2] == "BN":
                        continue

                    mvps[r[0]] += r[3]
                    all_time_mvps[r[0]] += r[3]

                    if r[2] == "DEF" or r[2] == "K":
                        continue

                    lvps[r[0]] += r[3]
                    lvpss[r[0]] += 1

            mvp = max(mvps, key=mvps.get)
            # print(f"{manager} - {season} MVP: ")

            self.accolades[manager].append(
                {
                    "title": f"Most Valuable Player ({season})",
                    "value": f"{mvp} ({mvps[mvp]:0.2f} pts)",
                    "style": "mvp",
                }
            )

            lvp_score = defaultdict(int)

            for key, value in lvps.items():
                lvp_score[k] = lvps[key] / lvpss[key]

            # print(manager)
            # print(lvps)
            # print(lvp_score)
            # exit(0)

            # lvp = min(lvps, key=lvps.get)
            # print(f"{manager} - {season} MVP: ")

            # self.accolades[manager].append(
            #     {
            #         "title": f"Least Valuable Player ({season})",
            #         "value": f"{lvp} ({lvps[lvp]:0.2f} pts)",
            #         "style": "draft",
            #     }
            # )

        mvp = max(all_time_mvps, key=all_time_mvps.get)

        self.accolades[manager].append(
            {
                "title": "All-Time MVP (Cumulative)",
                "value": f"{mvp} ({all_time_mvps[mvp]:0.2f} pts)",
                "style": "waiver",
            }
        )

    def award_rivalries(self):
        """
        """

        df = self.df

        managers = sorted(df['manager'].unique())

        matchup_data = []
        annot_data = []

        for manager in managers:

            win_pct = {}

            for opponent in managers:

                # If self-matchup:
                if manager == opponent:
                    matchup_data.append([manager, opponent, float('nan')])
                    annot_data.append([manager, opponent, ""])
                    continue

                # Filter for the specific manager vs. opponent matchups
                matchup_df = df[
                    (df['manager'] == manager) &
                    (df['opponent'] == opponent)
                ].copy()

                if not matchup_df.empty:
                    wins = len(
                        matchup_df[matchup_df['points'] >
                                   matchup_df['opp_points']]
                        )

                    losses = len(
                        matchup_df[matchup_df['points'] <
                                   matchup_df['opp_points']]
                        )

                    win_pct[opponent] = wins / (wins + losses)

            rival = min(win_pct, key=win_pct.get)
            patsy = max(win_pct, key=win_pct.get)

            # print(manager)
            # print(f"\tRival: {rival} ({win_pct[rival]:0.2f})")
            # print(f"\tPatsy: {patsy} ({win_pct[patsy]:0.2f})")

            self.accolades[manager].append(
                {
                    "title": "League Rival",
                    "value": f"{rival} ({win_pct[rival]:0.2f} win %)",
                    "style": "draft"
                }
            )

            self.accolades[manager].append(
                {
                    "title": "League Patsy",
                    "value": f"{patsy} ({win_pct[patsy]:0.2f} win %)",
                    "style": "draft"
                }
            )

    def award_player_versus(self):
        """
        """

        player_name = "Joe Flacco"

        player_starts = dict()
        player_bench = dict()

        for manager in self.df['manager'].unique():

            num_starts = 0
            total_pts = 0
            num_bench = 0

            s = self.df[self.df['manager'] == manager].reset_index()

            for k, row in s.iterrows():

                roster = eval(row['roster'])

                qb_starter_pts = -1e9
                diff = 0

                for p in roster:
                    if p[2] == "QB":
                        qb_starter_pts = max(qb_starter_pts, p[3])

                for p in roster:
                    if (p[0] == player_name) and (p[2] == "QB"):
                        num_starts += 1
                        total_pts += p[3]
                        print(f"{manager} vs {row['opponent']} - Week {row['week']} {row['season']}")
                    if (p[0] == player_name) and (p[2] == "BN"):
                        num_bench += 1
                        diff += qb_starter_pts - p[3]
                        print(f"{qb_starter_pts} {p[3]}")
                        # print(f"{manager} vs {row['opponent']} - Week {row['week']} {row['season']}\n")

            player_starts[manager] = (num_starts, total_pts)
            player_bench[manager] = (num_bench, diff)

        print(player_starts)
        print(player_bench)


    def award_season_paper_plates(self):
        """
        """

        df = self.df




if __name__ == "__main__":

    awards = Awards()
    # awards.run()

    # awards.award_yearly_champions()
    # awards.award_favorite_team()
    # awards.award_best_scores()
    # awards.award_rivalries()
    # awards.award_all_favorites()
    # awards.award_highest_scorer()

    # with open(awards.WEB_DATA_DIR / "accolades.json", "w") as f:
    #     json.dump(awards.accolades, f, indent=3)

    awards.award_player_versus()
