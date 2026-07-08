#!/usr/bin/env python3

import json
import pandas as pd
import nflreadpy

from collections import defaultdict
from pathlib import Path
from random import uniform
from time import sleep
from tqdm import tqdm

from yfpy.query import YahooFantasySportsQuery
from yfpy.models import Team, Player


def query_delay():
    # sleep(random()*Query.API_DELAY_SLEEP_MAX_SEC)
    sleep(uniform(1.0, Query.API_DELAY_SLEEP_MAX_SEC))


class Query:
    """Encapsulates creating a YahooFantasySportsQuery and parsing the
    response.

    Generates a YahooFantasySportsQuery on a season-by-season basis,
    and extracts relevant weekly matchup information, season standings,
    and other league metadata.
    """

    API_DELAY_SLEEP_MAX_SEC = 2.0255

    SEASONS_RANGE = range(2018, 2024+1)

    # Define the desired width for the tqdm description strings
    TQDM_WIDTH = 12

    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / "data"
    CACHE_DIR = DATA_DIR / "cache"

    def __init__(self):
        """Initializes a new instance of Query.
        """

        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # TODO: Remove in favor of the caching approach
        self.managers_record_map = defaultdict(  # season
            lambda: defaultdict(  # week
                lambda: defaultdict(dict)  # manager -> data entries
                )
            )

        self.standings_map = defaultdict(  # season
                lambda: defaultdict(dict)  # manager -> data entries
            )

        self.transactions_map = defaultdict(list)

        self.draft_results = []

        self.query_draft_flag = False
        self.query_matchups_flag = False
        self.query_transactions_flag = False

        self.league_name = None
        self.season = None

    def run_query(self, season: int):
        """Initializes and returns a Yahoo Fantasy Sports API query object for
        a specific season (year).

        This method creates an instance of the `YahooFantasySportsQuery` class,
        configuring it with the league and game IDs corresponding to the
        specified NFL season.

        Args:
            season (int): The NFL season for which to generate the query.

        Returns:
            YahooFantasySportsQuery: An initialized query object.
        """

        query = YahooFantasySportsQuery(
            league_id="######",
            game_code="nfl"
            )

        game_id = query.get_game_key_by_season(season)

        leagues = query.get_user_leagues_by_game_key(game_id)
        query_delay()

        if self.league_name is None:
            if len(leagues) > 1:
                print()
                for k, league in enumerate(leagues):
                    print(f"[{k}] {league.name}")
                league_k = int(
                    input(f"Select league name to query for {season}: ")
                    )

                self.league_name = leagues[league_k].name

                # raise NotImplementedError(
                #     f"Unable to determine league for season {season}."
                #     )
            else:
                self.league_name = leagues[0].name

        league_id = None

        for league in leagues:
            if league.name == self.league_name:
                league_id = league.league_id

        if league_id is None and len(leagues) > 1:
            for k, league in enumerate(leagues):
                print(f"[{k}] {league.name}")
            league_k = int(
                input("Select league name to query for {season}: ")
            )
            league_id = league[league_k].league_id
            # raise ValueError(f"No league_id found for {season}")

        query = YahooFantasySportsQuery(
                league_id=league_id,
                game_id=game_id,
                game_code="nfl",
                all_output_as_json_str=False
            )
        query_delay()

        return query

    def parse_query(self, query: YahooFantasySportsQuery):
        """Extracts desired statistics and information from a completed
        YahooFantasySportsQuery object.


        Using an instance of the `YahooFantasySportsQuery` class, the
        method extracts seasonal, weekly matchup results, and other
        manager data to store in local databases.

        Args:
            query (YahooFantasySportsQuery): The YahooFantasySportsQuery query
        """

        league_info = query.get_league_metadata()
        query_delay()

        season = league_info.season

        if league_info.season != self.season:
            raise RuntimeError("Season mismatch")

        standings = query.get_league_standings().teams
        query_delay()

        if self.query_draft_flag:
            self.parse_draft_results(query)

        if self.query_transactions_flag:
            # self.parse_transactions(query)
            raise NotImplementedError("Transaction parsing not implemented.")

        for team in standings:

            manager = team.managers[0].nickname

            if manager == "--hidden--":
                print(team)
                raise RuntimeError("Manager nickname not found.")

            self.standings_map[season][manager]["pf"] = team.points_for
            self.standings_map[season][manager]["pa"] = team.points_against
            self.standings_map[season][manager]["rank"] = team.rank
            self.standings_map[season][manager]["seed"] = team.playoff_seed
            self.standings_map[season][manager]["wins"] = team.wins
            self.standings_map[season][manager]["losses"] = team.losses

        # Get the season-long player roster for additional player metrics
        # not available through YFPY
        self.weekly_roster = nflreadpy.load_rosters_weekly(season)
        self.weekly_roster = self.weekly_roster.to_pandas()

        self.sched = nflreadpy.load_schedules(season).to_pandas()

        # Dynamically loop to the most recent week of the season
        # i.e. championship week for completed seasons, and
        # current week for present season
        for week in tqdm(range(1, league_info.current_week+1),
                         desc="Week".ljust(self.TQDM_WIDTH),
                         leave=False,
                         position=1):

            scoreboard = query.get_league_scoreboard_by_week(week)
            query_delay()

            if scoreboard is None:
                raise RuntimeError(
                    f"No scoreboard data for Week {week} {season}."
                    )

            for matchup_data in tqdm(scoreboard.matchups,
                                     leave=False,
                                     desc="Matchup".ljust(self.TQDM_WIDTH),
                                     position=2):

                team1_data = matchup_data.teams[0]
                team2_data = matchup_data.teams[1]

                if matchup_data.is_tied:
                    raise NotImplementedError("Tie handling not implemented.")

                mrm = self.managers_record_map[season][week]

                t1_mgr = team1_data.managers[0].nickname
                t2_mgr = team2_data.managers[0].nickname

                mrm[t1_mgr]["is_playoffs"] = matchup_data.is_playoffs
                mrm[t1_mgr]["is_consolation"] = matchup_data.is_consolation

                mrm[t2_mgr]["is_playoffs"] = matchup_data.is_playoffs
                mrm[t2_mgr]["is_consolation"] = matchup_data.is_consolation

                self.extract_matchup_data(
                    mrm, team1_data, team2_data, query, week
                    )
                self.extract_matchup_data(
                    mrm, team2_data, team1_data, query, week
                    )

    def extract_matchup_data(self,
                             mrm_stub: defaultdict,
                             team1: Team,
                             team2: Team,
                             query: YahooFantasySportsQuery,
                             week: int
                             ):
        """Extracts information for a given weekly matchup.

        A weekly matchup consists of team1 vs. team2. This function extracts
        the information for the "manager" (team1) vs. their opponent (team2).
        This method supports abstraction because each matchup is effectively
        captured as team1 vs. team2 and team2 vs. team1.

        Args:
            mrm_stub (defaultdict): Object to store the extracted data in
            team1 (yfpy.models.Team): Manager's team data object
            team2 (yfpy.models.Team): Opponent's team data object
        """

        team1_manager = team1.managers[0].nickname
        team2_manager = team2.managers[0].nickname

        mrm_stub[team1_manager]["points"] = team1.team_points.total
        mrm_stub[team1_manager]["proj_points"] = team1.projected_points

        mrm_stub[team1_manager]["opp_points"] = team2.team_points.total
        mrm_stub[team1_manager]["opp_proj_points"] = team2.projected_points
        mrm_stub[team1_manager]["opponent"] = team2_manager

        players = query.get_team_roster_player_stats_by_week(
            team1.team_id,
            week,
            )
        query_delay()

        roster = []

        for player in players:

            pts = player.player_points.total

            # YFPY does not provide a player's team for a given season,
            # so use a separate dB for a lookup
            player_team, player_pos = self.get_player_team(week, player)

            player_team_tmp = player_team

            if self.season < 2020 and player_team == "LV":
                player_team_tmp = "OAK"

            if player_team == "LAR":
                player_team_tmp = "LA"

            if player_team == "N/A":
                week_day = "N/A"

            else:
                teams = pd.concat(
                    [self.sched["home_team"], self.sched["home_team"]],
                    )
                teams = teams.unique()

                week_slice = self.sched[self.sched["week"] == week]
                week_slice = week_slice.drop(
                    columns=["game_id", "week", "season", "game_type"],
                    )

                if player_team_tmp not in teams:
                    print("\n\n\n")
                    print(week)
                    print(team1_manager)
                    print(week_slice)
                    print(player.full_name)
                    print(player_team)
                    print(player)
                    raise RuntimeError(
                        "Failed to identify player-team schedule."
                        )

                sched_slice = week_slice[
                    (week_slice["home_team"] == player_team_tmp) |
                    (week_slice["away_team"] == player_team_tmp)
                ].reset_index()

                # Bye week
                if sched_slice.shape[0] == 0:
                    week_day = "BYE"
                elif sched_slice.shape[0] == 1:
                    week_day = sched_slice.loc[0, "weekday"]
                else:
                    print("\n\n\n")
                    print(week)
                    print(team1_manager)
                    print(week_slice)
                    print(player.full_name)
                    print(player_team)
                    print(player)
                    raise RuntimeError(
                        "Multipe player-teams found."
                        )

            roster.append(
                (
                    player.full_name,
                    player_team,
                    player.selected_position.position,
                    pts,
                    player_pos,
                    week_day,
                )
            )

        mrm_stub[team1_manager]["roster"] = roster

    def get_player_team(self, week: int, player: Player):
        """Perform a secondary lookup to get a player's team for a past season.

        YFPY is unable to provide a player's team for historical seasons. The
        team returned is the player's most recent team. This function hooks in
        a secondary library to provide a lookup for a player's team for a
        given season.
        """

        wkly_rstr = self.weekly_roster

        if player.display_position == "DEF":
            player_team = player.editorial_team_abbr
            player_pos = "DEF"

        else:

            # Use Yahoo ID first
            player_slice = wkly_rstr[
                (wkly_rstr["yahoo_id"] == f"{player.player_id}")
                ].reset_index()

            # Else, fallback to str match on full name
            if player_slice.empty:
                player_slice = wkly_rstr[
                    (wkly_rstr["full_name"] == f"{player.full_name}")
                    ].reset_index()

            first_name = player.first_name
            last_name_trim = player.last_name.split()[0]

            # Else, fallback to partial match on first and last name
            if player_slice.empty:
                player_slice = wkly_rstr[
                    (wkly_rstr["first_name"] == f"{first_name}") &
                    (wkly_rstr["last_name"] == f"{last_name_trim}")
                    ].reset_index()

            # Else, fallback to last name and first initial
            if player_slice.empty:
                player_slice = wkly_rstr[
                    (wkly_rstr["first_name"].str.startswith(
                        first_name[0])) &
                    (wkly_rstr["last_name"] == f"{last_name_trim}")
                    ].reset_index()

            # Else, last name only and position
            if player_slice.empty:
                player_slice = wkly_rstr[
                    (wkly_rstr["position"] == player.primary_position) &
                    (wkly_rstr["last_name"] == f"{last_name_trim}")
                    ].reset_index()

            # Retired players that managers drafted anyway
            known_exceptions = [
                ("Rob Gronkowski", "TE"),
                ("Ryan Fitzpatrick", "QB"),
                ("Tim Tebow", "QB"),
                ("Odell Beckham Jr.", "WR"),
                ("Ray Rice", "RB"),
                ]

            # Expectation at this point is that any database mismatches
            # have been resolved, and the current `player` is one of the
            # known exceptions of not having an identifiable team.
            if player_slice.empty:
                player_team = "N/A"

                found = False
                for ke_name, ke_pos in known_exceptions:

                    if ke_name == player.full_name:
                        found = True
                        player_pos = ke_pos
                        break

                if not found:
                    raise RuntimeWarning(
                        f"{player.full_name} -- team not found.\n"
                        f"{self.season} - {week}"
                        )

            else:
                closest_week_index = (
                    player_slice['week'] - week
                    ).abs().idxmin()

                player_team = player_slice.loc[
                    closest_week_index, "team"]

                player_pos = player_slice.loc[
                    closest_week_index, "position"]

                # print(player_slice)
                # for x in player_slice.columns:
                #     print(x)
                # exit(0)

        if player_team == "OAK":
            player_team = "LV"

        return (player_team.upper(), player_pos)

    def parse_transaction(self, query: YahooFantasySportsQuery):
        """Parse out trade and other player transactions for all managers.
        """

        return NotImplemented

        # for transaction in query.get_league_transactions():
        #     query_delay()

        #     if transaction.type == "trade":
        #         tk0 = int(transaction.tradee_team_key.rsplit('.')[-1])-1
        #         tk1 = int(transaction.trader_team_key.rsplit('.')[-1])-1

        #         self.transactions_map[season].append((
        #             teams[tk0].managers[0].nickname,
        #             teams[tk1].managers[0].nickname,
        #         ))

    def parse_draft_results(self, query: YahooFantasySportsQuery):
        """"""

        teams = query.get_league_teams()
        query_delay()

        draft_results_query = query.get_league_draft_results()

        for drft_rslt in draft_results_query:

            team_k = int(drft_rslt.team_key.split(".")[-1])-1
            manager = teams[team_k].managers[0].nickname

            player = query.get_player_stats_for_season(drft_rslt.player_key)
            query_delay()

            self.draft_results.append(
                {
                    "season": self.season,
                    "manager": manager,
                    "player_name": player.full_name,
                    "player_pos": player.primary_position,
                    "player_key": player.player_key,
                    "player_cost": drft_rslt.cost,
                }
            )

        with open(self.CACHE_DIR / f'temp_draft_{self.season}.json', 'w') as f:
            json.dump(self.draft_results, f)

    def query_seasons(self):
        """Run and parse YahooFantasySportsQuery for all seasons.

        Queries are made indvidually across each season, and built into
        a local database. Databases are then saved the disk.
        """
        for season in tqdm(self.SEASONS_RANGE,
                           desc="Season".ljust(self.TQDM_WIDTH)):
            self.season = season
            query = self.run_query(self.season)
            self.parse_query(query)

            fn_path = self.CACHE_DIR / f"temp_data_{self.season}.json"
            with open(fn_path, "w") as f:
                json.dump(self.managers_record_map[self.season], f)

    def apply_manager_aliases(self, df: pd.DataFrame):
        """Apply an alias to manager nicknames.

        This method will replace any matched manager nicknames with a desired a
        lias. The intention is to modify dynamically pulled manager nicknames
        for consistency, or public distribution.
        """

        manager_aliases_path = Path('manager_aliases.json')

        if not manager_aliases_path.exists:
            return

        with open(manager_aliases_path, 'r') as f:
            manager_aliases = json.load(f)

        for manager, alias in manager_aliases.items():
            df['manager'] = df['manager'].str.replace(manager, alias)

            if 'opponent' in df.columns:
                df['opponent'] = df['opponent'].str.replace(manager, alias)

    def save_weekly_matchups_data(self):
        """Convert the multi-level weekly manager matchups data
        dictionary into a Pandas dataframe. Then save the dataframe
        to disk.
        """
        # Flatten the nested dictionary into a list of records
        records = []
        for season in list(self.managers_record_map.keys()):

            for week in list(self.managers_record_map[season].keys()):

                mrm = self.managers_record_map[season][week]

                for manager in list(mrm.keys()):

                    manager_stats = mrm[manager]

                    record = {
                        "season": season,
                        "week": week,
                        "manager": manager,
                        **manager_stats
                    }
                    records.append(record)

        df = pd.DataFrame(records)
        self.apply_manager_aliases(df)
        df.to_csv(self.DATA_DIR / 'data.csv')

    def save_data(self):
        """Save results from YahooFantasySportsQuery to local files.
        """

        # df = pd.DataFrame(self.draft_results)
        # df = self.apply_manager_aliases(df)
        # df.to_csv(self.DATA_DIR / "draft_results.csv")

        self.save_weekly_matchups_data()

        manager_aliases_path = Path('manager_aliases.json')
        with open(manager_aliases_path, 'r') as f:
            manager_aliases = json.load(f)

        # Flatten the nested dictionary into a list of records
        records = []
        for season in list(self.managers_record_map.keys()):

            print(season)

            for trade in self.transactions_map[season]:

                if trade[0] in manager_aliases:
                    m0 = manager_aliases[trade[0]]
                else:
                    m0 = trade[0]

                if trade[1] in manager_aliases:
                    m1 = manager_aliases[trade[1]]
                else:
                    m1 = trade[1]

                record = {
                        "season": season,
                        "trader": m0,
                        "tradee": m1,
                    }

                records.append(record)

        df = pd.DataFrame(records)
        df.to_csv(self.DATA_DIR / 'transactions.csv')

        # Flatten the nested dictionary into a list of records
        records = []
        for season in list(self.standings_map.keys()):

            for manager in list(self.standings_map[season].keys()):

                manager_stats = self.standings_map[season][manager]

                record = {
                    "season": season,
                    "manager": manager,
                    **manager_stats
                }
                records.append(record)

            # Convert the list of records to a DataFrame
        df = pd.DataFrame(records)

        self.apply_manager_aliases(df)
        df.to_csv(self.DATA_DIR / 'standings.csv')

    def combine(self, season_range: range = range(2018, 2025+1)):
        """Helper function to combine partial (cached) weekly matchup
        data files into a complete database.
        """

        for season in season_range:

            with open(self.CACHE_DIR / f"temp_data_{season}.json", "r") as f:
                data = json.load(f)

            self.managers_record_map[season] = data

        self.save_weekly_matchups_data()

    def combine_draft(self):
        """Helper function to combine partial (cached) season draft results
        data files into a complete database.
        """

        self.draft_results = []

        for season in range(2024, 2024+1):

            with open(self.CACHE_DIR / f"temp_draft_{season}.json", "r") as f:
                data = json.load(f)

            self.draft_results += data

        df_drft = pd.DataFrame(self.draft_results)
        self.apply_manager_aliases(df_drft)
        df_drft.to_csv(self.DATA_DIR / "draft_results.csv")

    def save_draft_results(self):
        """Helper function to process draft results into a full,
        usable database.
        """

        df = pd.read_csv(self.DATA_DIR / 'data.csv')
        df_drft = pd.read_csv(self.DATA_DIR / 'draft_results.csv')

        for k, row in df_drft.iterrows():

            season = row['season']
            manager = row['manager']
            player_name = row['player_name']
            pts = 0.0

            df1 = df[
                (df['manager'] == manager) &
                (df['season'] == season)
            ]

            for week in df1['week'].unique():

                df2 = df1[df1['week'] == week].reset_index()
                roster = eval(df2.loc[0, 'roster'])

                for r in roster:

                    if r[0] == player_name and r[2] != "BN":
                        pts += r[3]

            df_drft.loc[k, 'points'] = pts

        df_drft = df_drft.drop(
            ['Unnamed: 0', 'player_key'],
            axis=1,
            )
        df_drft.to_csv(self.DATA_DIR / "draft_results.csv")
        df_drft.to_json(
            self.ROOT_DIR / '_data' / 'draft-results.json',
            orient='records',
            indent=3,
            )


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv()

    q = Query()
    # q.combine_draft()
    # q.save_draft_results()

    r = range(2025, 2025+1)
    q.SEASONS_RANGE = r
    q.query_seasons()

    # r = range(2018, 2025+1)
    # q.combine(r)

    # q.SEASONS_RANGE = range(2016, 2017+1)
    # q.query_seasons()
