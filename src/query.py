#!/usr/bin/env python3

import json
import pandas as pd

from collections import defaultdict
from pathlib import Path
from time import sleep

from yfpy.query import YahooFantasySportsQuery
from yfpy.models import Team


class Query:
    """Encapsulates creating a YahooFantasySportsQuery and parsing the
    response.

    Generates a YahooFantasySportsQuery on a season-by-season basis,
    and extracts relevant weekly matchup information, season standings,
    and other league metadata.
    """

    SEASONS_RANGE = range(2018, 2024+1)
    DATA_DIR = Path(__file__).parent.parent / "data"

    def __init__(self):
        """Initializes a new instance of Query.
        """

        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open('league_ids.json', 'r') as f:
            self.league_ids = json.load(f)

        self.managers_record_map = defaultdict(  # season
            lambda: defaultdict(  # week
                lambda: defaultdict(dict)  # manager -> data entries
            )
        )

        self.winners_map = defaultdict(  # season
                lambda: defaultdict(dict)  # winners
        )

        self.standings_map = defaultdict(  # season
                lambda: defaultdict(dict)  # manager -> data entries
        )

        self.league_name = None

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
            # league_id=self.league_ids[f"{season}"],
            league_id="######",
            game_code="nfl"
            )
        game_id = query.get_game_key_by_season(season)

        leagues = query.get_user_leagues_by_game_key(game_id)

        if self.league_name is None:
            if len(leagues) > 1:
                print(leagues)
                raise NotImplementedError(
                    f"Unable to determine league for season {season}."
                    )

            self.league_name = leagues[0].name

        league_id = None

        for league in leagues:
            if league.name == self.league_name:
                league_id = league.league_id

        if league_id is None:
            raise ValueError(f"No league_id found for {season}")

        # Reduce API rate
        sleep(1)

        query = YahooFantasySportsQuery(
                # league_id=self.league_ids[f"{season}"],
                league_id=league_id,
                game_id=game_id,
                game_code="nfl",
                all_output_as_json_str=False
            )

        # Reduce API rate
        sleep(1)

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

        season = league_info.season

        standings = query.get_league_standings().teams

        self.winners_map[season]["1st"] = standings[0].managers[0].nickname
        self.winners_map[season]["2nd"] = standings[1].managers[0].nickname
        self.winners_map[season]["3rd"] = standings[2].managers[0].nickname

        for team in standings:

            manager = team.managers[0].nickname

            self.standings_map[season][manager]["pf"] = team.points_for
            self.standings_map[season][manager]["pa"] = team.points_against
            self.standings_map[season][manager]["rank"] = team.rank
            self.standings_map[season][manager]["seed"] = team.playoff_seed
            self.standings_map[season][manager]["wins"] = team.wins
            self.standings_map[season][manager]["losses"] = team.losses

        # Dynamically loop over both 17 and 18 week seasons
        for week in range(1, league_info.current_week+1):

            scoreboard = query.get_league_scoreboard_by_week(week)

            if scoreboard is None:
                print(f"No scoreboard data for Week {week} in {season}.")
                continue

            for matchup_data in scoreboard.matchups:

                team1_data = matchup_data.teams[0]
                team2_data = matchup_data.teams[1]

                team1_manager = team1_data.managers[0].nickname
                team2_manager = team2_data.managers[0].nickname

                if matchup_data.is_tied:
                    print("TIE")
                    print(season)
                    print(week)
                    print(team1_manager)
                    print(team2_manager)
                    exit(2)

                mrm = self.managers_record_map[season][week]

                self.extract_matchup_data(mrm, team1_data, team2_data)
                self.extract_matchup_data(mrm, team2_data, team1_data)

    def extract_matchup_data(self,
                             mrm_stub: defaultdict,
                             team1: Team,
                             team2: Team
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
        mrm_stub[team1_manager]["faab_balance"] = team1.faab_balance
        mrm_stub[team1_manager]["moves"] = team1.number_of_moves
        mrm_stub[team1_manager]["rank"] = team1.rank

        mrm_stub[team1_manager]["opp_points"] = team2.team_points.total
        mrm_stub[team1_manager]["opp_proj_points"] = team2.projected_points
        mrm_stub[team1_manager]["opponent"] = team2_manager

    def query_seasons(self):
        """Run and parse YahooFantasySportsQuery for all seasons.

        Queries are made indvidually across each season, and built into
        a local database. Databases are then saved the disk.
        """

        for season in self.SEASONS_RANGE:
            print(f"Querying {season} season...")
            query = self.run_query(season)
            self.parse_query(query)

        self.save_data()

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

    def save_data(self):
        """Save results from YahooFantasySportsQuery to local files.
        """

        # with open(self.DATA_DIR / 'matchups_data.json', 'w') as f:
        #     json.dump(self.managers_record_map, f, indent=3)

        # with open(self.DATA_DIR / 'winners.json', 'w') as f:
        #     json.dump(self.winners_map, f, indent=3)

        # with open(self.DATA_DIR / 'standings.json', 'w') as f:
        #     json.dump(self.standings_map, f, indent=3)

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

        # Convert the list of records to a DataFrame
        df = pd.DataFrame(records)

        print(df.columns)

        self.apply_manager_aliases(df)

        df.to_csv(self.DATA_DIR / 'data.csv')

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

        print(df.columns)

        df.to_csv(self.DATA_DIR / 'standings.csv')
