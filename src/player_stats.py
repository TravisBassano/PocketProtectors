#!/usr/bin/env python3

import pandas as pd
import nflreadpy
from pathlib import Path


def build_weekly_player_stats(season: int) -> pd.DataFrame:
    """Build a DataFrame of weekly player stats for a single season.

    Each row represents one player for one week, with game-level
    stats aggregated to the weekly level. The resulting DataFrame
    includes the Yahoo ID for each player, which is pulled from the
    db_playerids.csv file that maps player names to their respective
    Yahoo IDs. This mapping allows for proper identification and
    tracking of players across different data sources and seasons.
    Args:
        season: The NFL season year (e.g. 2024).

    Returns:
        pandas.DataFrame with columns for player metadata and weekly stats.
    """

    # Load game-level player stats from nflreadpy
    player_stats = nflreadpy.load_player_stats(seasons=season).to_pandas().copy()

    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / "data"
    df_player_ids = pd.read_csv(DATA_DIR / "db_playerids.csv")

    # Filter to regular season only (values: 'REG', 'POST')
    player_stats = player_stats[player_stats["season_type"] == "REG"].copy()

    # Identify numeric stat columns to aggregate
    stat_columns = [
        col for col in player_stats.columns
        if pd.api.types.is_numeric_dtype(player_stats[col])
        and col not in ("player_id", "week", "season")
    ]

    # Build aggregation dictionary: numeric stats -> sum, metadata -> first
    agg_dict = {col: "sum" for col in stat_columns}
    agg_dict["player_name"] = "first"
    agg_dict["position"] = "first"
    agg_dict["team"] = "first"

    # Aggregate game-level stats to weekly level.
    # Some players may appear multiple times in a week if their team played
    # on different days; collapse those into a single row.
    weekly_stats = player_stats.groupby(
        ["player_id", "week", "season"]
    ).agg(agg_dict).reset_index()

    # Rename player_id column to gsis_id
    weekly_stats = weekly_stats.rename(columns={"player_id": "gsis_id"})

    # Join with player IDs to add yahoo_id
    weekly_stats = weekly_stats.merge(df_player_ids[['gsis_id', 'yahoo_id']], left_on="gsis_id", right_on="gsis_id", how="left")

    return weekly_stats


def save_weekly_player_stats(season: int, output_path: Path = None) -> Path:
    """Build and save weekly player stats to a CSV file.

    Args:
        season: The NFL season year.
        output_path: Optional path to save the CSV. If not provided, saves
            to data/player_stats_{season}.csv in the project root.

    Returns:
        Path to the saved CSV file.
    """

    weekly_stats = build_weekly_player_stats(season)

    if output_path is None:
        ROOT_DIR = Path(__file__).parent.parent
        DATA_DIR = ROOT_DIR / "data"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DATA_DIR / f"player_stats_{season}.csv"

    weekly_stats.to_csv(output_path, index=False)
    print(f"Saved {weekly_stats.shape[0]} rows to {output_path}")

    return output_path


if __name__ == "__main__":
    import time

    for season in range(2018,2018+1):
        save_weekly_player_stats(season)
        time.sleep(10)




