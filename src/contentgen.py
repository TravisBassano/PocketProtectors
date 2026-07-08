"""
contentgen.py

Internal module for generating web content (HTML, Markdown, etc.)
as part of the broader project. Not intended as a standalone package.

Usage example:

    gen = ContentGenerator()
    gen.generate_page()
"""

import json
import pandas as pd
import textwrap

from pathlib import Path


class ContentGenerator:
    """
    Core class for generating structured content (HTML, Markdown, etc.).

    """

    DATA_DIR = Path(__file__).parent.parent / "data"
    WEB_DATA_DIR = Path(__file__).parent.parent / "_data"
    PAGES_DIR = Path(__file__).parent.parent / "_pages"
    SUBPAGES_DIR = Path(__file__).parent.parent / "_subpages"
    MGR_PAGES_DIR = SUBPAGES_DIR / "manager"

    def __init__(self):

        self.df = pd.read_csv(self.DATA_DIR / 'data.csv')
        self.df_standings = pd.read_csv(self.DATA_DIR / 'standings.csv')

        self.MGR_PAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def generate_overall_standings(self):
        """Create a JSON output file of overall manager standings
        """

        average_stats_by_season = self.df_standings.groupby(
            'season')[['pf', 'pa']].mean()
        avg_pf = average_stats_by_season['pf'].to_list()
        avg_pa = average_stats_by_season['pa'].to_list()

        # Group by 'manager' and sum the 'wins' and 'losses'
        manager_stats = self.df_standings.groupby('manager')[
            ['wins',
             'losses',
             'pf',
             'pa',
             ]].sum().reset_index()

        manager_stats['win_pct'] = round(
            manager_stats['wins'] / (
                manager_stats['wins'] + manager_stats['losses']
                ) * 100.0,
            1
            )

        manager_stats = manager_stats.rename(columns={'manager': 'name'})
        manager_stats = manager_stats.round(1)

        p = self.WEB_DATA_DIR / "overall.json"

        with open(p, "w") as f:
            manager_stats.to_json(f, orient='records', indent=3)

        # Group the data by 'manager' and calculate the totals
        manager_stats = self.df_standings.groupby('manager').agg(
            playoff_appearances=('seed', lambda x: (x <= 6).sum()),
            championship_appearances=('rank', lambda x: (x <= 2).sum()),
            championships=('rank', lambda x: (x == 1).sum())
        )

        manager_stats = manager_stats.rename(columns={'manager': 'name'})
        manager_stats = manager_stats.reset_index()

        grouped = self.df_standings.groupby('manager')

        # Create a dictionary to hold the final output
        json_output = {}

        # Iterate through each manager's group
        for manager, group_df in grouped:
            # For each manager, create a dictionary to store their stats
            manager_stats = {}

            columns_to_include = ['pf', 'pa', 'rank', 'seed', 'wins', 'losses']

            # Iterate through each column and convert the series to a list
            for col in columns_to_include:
                manager_stats[col] = group_df[col].tolist()

            for k, _ in enumerate(manager_stats['pf']):
                manager_stats['pf'][k] -= avg_pf[k]
                manager_stats['pa'][k] -= avg_pa[k]

            # Add the manager's stats to the main output dictionary
            json_output[manager] = manager_stats

        p = self.WEB_DATA_DIR / "seasons.json"

        with open(p, "w") as f:
            json.dump(json_output, f, indent=3)

    def generate_chart_data(self):
        """Output _data/ assets
        """

        df = pd.read_csv(self.DATA_DIR / "standings.csv")

        managers = sorted(df["manager"].unique())

        data = []

        for manager in managers:

            df_slice = df[df["manager"] == manager]

            playoff_appearances = (df_slice["seed"] <= 6).sum()
            playoff_byes = (df_slice["seed"] <= 2).sum()
            champ_appearances = (df_slice["rank"] <= 2).sum()
            champs = (df_slice["rank"] == 1).sum()

            data.append({
                "manager": manager,
                "playoff_appearances": int(playoff_appearances),
                "playoff_byes": int(playoff_byes),
                "championship_appearances": int(champ_appearances),
                "championships": int(champs),
            })

        with open(self.WEB_DATA_DIR / "playoffs.json", 'w') as f:
            json.dump(data, f, indent=3)

    def generate_all_manager_pages(self):
        """
        Generate the profile page for all managers in the league dataset.

        Loops over every manager found in the dataset, and creates a
        custom manager profile page under the web _subpage assets.

        """

        managers = self.df["manager"].unique()

        for manager in managers:
            # if manager == "Travis":
            #     continue
            self.generate_manager_page(manager)

    def generate_manager_page(self, manager: str):
        """
        Generates a manager profile page for the specified manager.

        Using the league historical database, generate the profile
        page for the manager provided by an argument.

        Args:
            manager (str): Name of the manager
        """

        css_style_str = (
            "<link rel=\"stylesheet\" "
            "href=\"{{ '/assets/css/awards.css' | relative_url }}\">"
            )

        scatter_plot_str = (
            "![Scatter plot]({{ site.baseurl }}"
            f"/assets/plots/matchup_scatter_{manager.lower()}.png)"
            )

        awards_js_str = (
            "<script src=\"{{ '/assets/js/manager-awards.js' | relative_url }}"
            "\"></script>"
        )

        manager_page_path = (
            self.MGR_PAGES_DIR / f"{manager.lower()}.md"
        )

        f = open(manager_page_path, "w")

        f.write(textwrap.dedent(f"""\
            ---
            layout: page
            title: {manager}
            permalink: /manager/{manager.lower()}/
            manager: {manager}
            ---

            {css_style_str}

            <script id="awards-data" type="application/json">
               {{{{ site.data.awards | jsonify }}}}
            </script>

            <script id="accolades-data" type="application/json">
               {{{{ site.data.accolades | jsonify }}}}
            </script>

            <script id="counts-data" type="application/json">
                {{{{ site.data.team-counts | jsonify }}}}
            </script>

            <div id="banner-wall" data-manager="{{{{ page.manager }}}}"></div>
            <div id="accolades-wall"></div>

            {awards_js_str}

            <canvas id="favoriteTeams"></canvas>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="{{{{ '/assets/js/team-counts.js' | relative_url }}}}"></script>

            {scatter_plot_str}
            """
        ))

        f.close()


if __name__ == "__main__":
    gen = ContentGenerator()
    gen.generate_overall_standings()
    gen.generate_all_manager_pages()
