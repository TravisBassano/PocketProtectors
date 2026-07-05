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

        js_script_str = (
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
            title: {manager.title()} Profile Page
            permalink: /manager/{manager.lower()}/
            manager: {manager}
            ---

            {css_style_str}

            <script id="awards-data" type="application/json">
               {{{{ site.data.awards | jsonify }}}}
            </script>

            <div id="banner-wall" data-manager="{{{{ page.manager }}}}"></div>

            {js_script_str}

            {scatter_plot_str}
            """
        ))

        f.close()


if __name__ == "__main__":
    gen = ContentGenerator()
    gen.generate_all_manager_pages()
