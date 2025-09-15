"""
contentgen.py

Internal module for generating web content (HTML, Markdown, etc.)
as part of the broader project. Not intended as a standalone package.

Usage example:

    gen = ContentGenerator()
    gen.generate_page()
"""

import pandas as pd
import textwrap

from pathlib import Path


class ContentGenerator:
    """
    Core class for generating structured content (HTML, Markdown, etc.).

    """

    DATA_DIR = Path(__file__).parent.parent / "data"
    PAGES_DIR = Path(__file__).parent.parent / "_pages"
    MGR_PAGES_DIR = PAGES_DIR / "manager"

    def __init__(self):

        self.df = pd.read_csv(self.DATA_DIR / 'data.csv')

        self.MGR_PAGES_DIR.mkdir(parents=True, exist_ok=True)

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

            f.write(textwrap.dedent(f"""
                ---
                layout: page
                title: {manager.title()} Profile Page
                permalink: /about/
                ---

                ![Scatter plot]({{ site.baseurl }}/assets/plots/matchup_scatter_{manager.lower()}.png)
                """
            ))

            f.close()


if __name__ == "__main__":
    gen = ContentGenerator()