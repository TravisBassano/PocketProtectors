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

        self.MGR_PAGES_DIR.mkdir(parents=True, exist_ok=True)

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
                "manager" : manager,
                "playoff_appearances" : int(playoff_appearances),
                "playoff_byes" : int(playoff_byes),
                "championship_appearances" : int(champ_appearances),
                "championships" : int(champs),
            })

        with open(self.WEB_DATA_DIR / "playoffs.json", 'w') as f:
            json.dump(data, f, indent=3)


    def generate_page(self):
        """
        Generate a full page.

        Args:


        Returns:

        """

        managers = self.df["manager"].unique()

        for manager in managers:

            manager_page_path = (
                self.MGR_PAGES_DIR / f"{manager.lower()}.md"
            )

            f = open(manager_page_path, "w")

            f.write(textwrap.dedent(f"""\
                ---
                layout: page
                title: {manager.title()} Profile Page
                permalink: /manager/{manager.lower()}/
                ---

                ![Scatter plot]({{{{ site.baseurl }}}}/assets/plots/matchup_scatter_{manager.lower()}.png)
                """
            ))

            f.close()


if __name__ == "__main__":
    gen = ContentGenerator()