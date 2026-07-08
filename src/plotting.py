#!/usr/bin/env python3

import inspect
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns
import networkx as nx
import numpy as np

from adjustText import adjust_text
from pathlib import Path
from matplotlib.lines import Line2D
from statsmodels.formula.api import ols
from collections import defaultdict


class Plotting:
    """Create plots using data extracted via Query. Save plot artifacts to the
    project data directory.

    """

    PLOTS_DIR = Path(__file__).parent.parent / "assets" / "plots"
    DATA_DIR = Path(__file__).parent.parent / "data"

    def __init__(self):
        """Initializes and instance of the Plotting class.

        Loads in all the data from the data directory
        """

        self.PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        self.df = pd.read_csv(self.DATA_DIR / 'data.csv')
        self.df['point_diff'] = self.df['points'] - self.df['proj_points']

        self.df_standings = pd.read_csv(self.DATA_DIR / 'standings.csv')

        self.df_trades = pd.read_csv(self.DATA_DIR / 'transactions.csv')

        min_season = min(self.df["season"].unique())
        max_season = max(self.df["season"].unique())
        self.PLT_HEADER = f"MVKC\nSeaons {min_season}-{max_season}\n"

    def plot_scorigami(self):
        """DEPRECATED Since most matches are scorigami
        Create a heatmap based on matchup scores. Unique scores only
        occuring once are a 'scorigami'
        """
        df = self.df

        # Round scores
        df["points_r"] = df["points"].round().astype(int)
        df["opp_points_r"] = df["opp_points"].round().astype(int)

        # Keep only winning matchups
        winners = df[df["points"] > df["opp_points"]]

        # Count frequency of each (losing, winning) pair
        pair_counts = winners.groupby(
            ["points_r", "opp_points_r"]).size().reset_index(name="count")

        # Merge counts back onto winners
        winners = winners.merge(
            pair_counts, on=["points_r", "opp_points_r"], how="left")
        ties = df[df["points_r"] == df["opp_points_r"]]

        # How many scorigamis happened more than once?
        duplicates = pair_counts[pair_counts["count"] > 1]

        print("Number of scorigamis repeated:", len(duplicates))
        print(duplicates.sort_values("count", ascending=False))

        # Percentage of games with duplicate scorigami
        duplicate_games = (winners["count"] > 1).sum()
        pct_duplicates = duplicate_games / len(winners) * 100

        print(f"Total games: {len(winners)}")
        print(f"Games with duplicate scorigami: {duplicate_games}")
        print(f"Percentage: {pct_duplicates:.2f}%")

        print(f"Total ties: {len(ties)}")
        if len(ties):
            print(ties[["season", "week", "manager", "points_r", "opponent"]])

        # Build a 2D frequency table (winning vs losing scores)
        heatmap_data = winners.groupby(
            ["opp_points_r", "points_r"]).size().unstack(fill_value=0)

        exit(0)

        # Plot
        plt.figure(figsize=(12, 8))
        plt.imshow(heatmap_data, origin="lower", cmap="Blues", aspect="auto")

        # Axes labels
        plt.xticks(
            range(len(heatmap_data.columns)),
            heatmap_data.columns,
            rotation=90,
            )
        plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)

        plt.xlabel("Losing Score (rounded)")
        plt.ylabel("Winning Score (rounded)")
        plt.title("Fantasy League Scorigami (Winning vs Losing Scores)")

        # Optional: add counts as text
        for (y, x), value in np.ndenumerate(heatmap_data.values):
            if value > 0:
                plt.text(x, y, str(value),
                         ha="center", va="center", color="black", fontsize=7)

        plt.colorbar(label="Number of Occurrences")
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / "scorigami.png")
        plt.close()

    def plot_proj(self):
        """Plot projected points vs. actual points scored per manager.

        Create plots showing actual points scored vs. projected
        points scored per manager, using both bar plot and box plot.
        """

        # Calculate the average difference per manager
        avg_diff_sorted = (
            self.df.groupby('manager')['point_diff']
            .mean()
            .reset_index()
            .sort_values(by='point_diff', ascending=False)
        )

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(
            x='manager',
            y='point_diff',
            data=avg_diff_sorted,
            palette='viridis',
            hue='manager',
            legend=False
        )
        plt.grid(True, axis='y')
        ax.set_axisbelow(True)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Average Projected Points vs. Actual Points Difference',
            fontsize=12,
            )
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel(r'$\Delta$ Projected vs. Actual Points', fontsize=12)

        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.tight_layout()

        plt.savefig(self.PLOTS_DIR / "projected_pts_diff_bar.png")
        plt.close()

        # Sort the managers alphabetically for the box plot order
        manager_order = sorted(self.df['manager'].unique())

        # Create a box plot for the spread of those values.
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(
            x='manager',
            y='point_diff',
            data=self.df,
            palette='magma',
            hue='manager',
            legend=False,
            order=manager_order,
            hue_order=manager_order
        )
        plt.grid(True, axis='y')
        ax.set_axisbelow(True)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Spread of Projected vs. Actual Points Differences by Manager',
            fontsize=12,
            )
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel(r'$\Delta$ Projected vs. Actual Points', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / "projected_pts_diff_box.png")
        plt.close()

    def plot_proj_heatmap(self):
        """Create a heatmap for the win-loss record and average point delta
        across all weekly head-to-head matchups.
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

                    record = f"({wins}-{losses})"

                    win_pct[opponent] = wins / (wins + losses)

                    avg_delta = matchup_df['point_diff'].mean()

                    # Annotations info
                    matchup_data.append([manager, opponent, avg_delta])
                    annot_data.append(
                        [manager, opponent, f"{record}\n{avg_delta:.2f}"]
                        )
                else:
                    matchup_data.append([manager, opponent, float('nan')])
                    annot_data.append([manager, opponent, ""])

            rival = min(win_pct, key=win_pct.get)
            patsy = max(win_pct, key=win_pct.get)

            print(manager)
            print(f"\tRival: {rival} ({win_pct[rival]:0.2f})")
            print(f"\tPatsy: {patsy} ({win_pct[patsy]:0.2f})")

        # Create DataFrames and pivot for the heatmap
        matchup_df_for_heatmap = pd.DataFrame(
            matchup_data, columns=['Manager', 'Opponent', 'Avg. Delta']
            )
        heatmap_data = matchup_df_for_heatmap.pivot(
            index='Manager', columns='Opponent', values='Avg. Delta'
            )

        annot_df_for_heatmap = pd.DataFrame(
            annot_data, columns=['Manager', 'Opponent', 'Annotation']
            )
        annot_data_pivoted = annot_df_for_heatmap.pivot(
            index='Manager', columns='Opponent', values='Annotation'
            )

        # Calculate the largest absolute delta to set vmin and vmax
        max_abs_delta = heatmap_data.abs().max().max()

        plt.figure(figsize=(10, 8))
        ax = sns.heatmap(
            heatmap_data,
            annot=False,
            fmt="",  # Using our own annotations
            cmap='coolwarm',
            center=0,
            linewidths=.5,
            linecolor='black',
            cbar_kws={'label': 'Average Point Delta (Points - Projected)'},
            vmin=-max_abs_delta,
            vmax=max_abs_delta,
        )

        # Manually add annotations
        for i, row in enumerate(annot_data_pivoted.index):
            for j, col in enumerate(annot_data_pivoted.columns):
                annotation = annot_data_pivoted.loc[row, col]
                if annotation:

                    record, delta = annotation.split('\n')

                    # Annotate win-loss reocrd in bold
                    ax.text(
                        x=j + 0.5,
                        y=i + 0.35,
                        s=record,
                        ha='center',
                        va='center',
                        fontweight='bold',
                        fontsize=10,
                        color='black'
                        )

                    # Add the regular points delta on the bottom
                    ax.text(
                        x=j + 0.5,
                        y=i + 0.65,
                        s=delta,
                        ha='center',
                        va='center',
                        fontsize=10,
                        color='black'
                        )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Head-to-Head Record and Projected vs. Actual Points Delta',
            fontsize=16
            )
        plt.xlabel('Opponent', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Manager', fontsize=12)
        plt.yticks(rotation=0, ha='right')
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'head_to_head_heatmap.png')
        plt.close()

    def plot_weekly_scatter(self):
        """Generate scatter plots of each manager's weekly scores.

        Show each manager's weekly scores on a scatter plot vs. each
        matchup's point differential. These plots highlight good wins,
        bad losses, and other fluky outcomes.
        """

        df = self.df

        league_avg_points = df['points'].mean()

        xlim = (
            round(df['points'].min()-0, -0),
            round(df['points'].max()+0, -0)
        )

        ylim = (
            round(df['point_diff'].min()-0, -0),
            round(df['point_diff'].max()+0, -0)
        )

        managers = df['manager'].unique()

        df = df.sort_values('points')

        # Fit the linear regression model using statsmodels
        model = ols('point_diff ~ points', data=df).fit()
        predictions = (
            model.get_prediction(df['points']).summary_frame(alpha=0.05)
        )

        fmls = {name: 0 for name in managers}

        # Create a separate scatter plot for each manager
        for manager in managers:
            # Filter the DataFrame for the current manager
            manager_df = df[df['manager'] == manager].copy()

            manager_df['win'] = (
                manager_df['point_diff'] > 0
            )

            manager_df = manager_df.reset_index(drop=True)

            # Separate wins and losses
            wins_df = manager_df[manager_df['win']]
            losses_df = manager_df[~manager_df['win']]

            fml = (
                # (manager_df['point_diff'] < fml_preds['obs_ci_lower']) &
                (manager_df['point_diff'] < 0) &
                (manager_df['points'] > league_avg_points)
            )

            fmls[manager] = int(fml.sum())

            plt.figure(figsize=(10, 7))

            # Plot wins
            ax = sns.scatterplot(
                x='points',
                y='point_diff',
                data=wins_df,
                s=150,
                edgecolor='black',
                marker='o',
                color='green',
                label='Win'
            )

            # Plot losses
            sns.scatterplot(
                x='points',
                y='point_diff',
                data=losses_df,
                s=150,
                edgecolor='black',
                marker='X',
                color='red',
                label='Loss'
            )

            # Plot the prediction interval
            plt.fill_between(
                x=df['points'],
                y1=predictions['obs_ci_lower'],
                y2=predictions['obs_ci_upper'],
                color='gray',
                alpha=0.1,
                label='95% Prediction Interval'
                )

            # Plot the regression line
            plt.plot(
                df['points'],
                predictions['mean'],
                c='black',
                linestyle='--',
                label='Regression Line',
                zorder=4
                )

            plt.axhline(0, color='gray', linestyle='--')
            plt.axvline(league_avg_points, color='gray', linestyle='--')

            plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
            plt.title(f'Weekly Matchup Performance for {manager}', fontsize=16)
            plt.xlabel('Manager Points Scored', fontsize=12)
            plt.ylabel(
                'Point Differential (Manager Points - Opponent Points)',
                fontsize=12
                )

            plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
            plt.xlim(xlim)
            plt.ylim(ylim)

            # Add quadrant labels
            ax.text(
                xlim[1]*0.22,
                ylim[0]*0.95,
                'Bad Loss',
                ha='left',
                va='center',
                fontsize=12,
                )
            ax.text(
                xlim[1]*0.98,
                ylim[0]*0.95,
                'F My Life',
                ha='right',
                va='center',
                fontsize=12,
                )
            ax.text(
                xlim[1]*0.22,
                ylim[1]*0.94,
                'Bad Victory',
                ha='left',
                va='center',
                fontsize=12,
                )
            ax.text(
                xlim[1]*0.98,
                ylim[1]*0.94,
                'Good Victory',
                ha='right',
                va='center',
                fontsize=12,
                )

            plt.grid(True, which='both', linestyle='--', linewidth=0.5)
            plt.tight_layout()

            # Save the figure with a descriptive filename
            manager_str = f'{manager.lower().replace(" ", "_")}'
            plt.savefig(self.PLOTS_DIR / f'matchup_scatter_{manager_str}.png')
            plt.close()

        # Create the bar plot
        plt.figure(figsize=(10, 6))
        ax = plt.bar(fmls.keys(), fmls.values(), color='skyblue')

        # Add labels and a title
        plt.xlabel('Manager', fontsize=12)
        plt.ylabel('FML Games', fontsize=12)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Total \'F My Life\' Outcomes (All FML Quadrant)',
            fontsize=16,
            )

        # Rotate the x-axis labels for better readability if needed
        plt.xticks(rotation=45, ha='right')

        # Add a grid for easier reading of the values
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.grid(axis='x', visible=False)

        # Display the plot
        plt.ylim(0, max(fmls.values())+3)
        # Set the y-axis ticks to display only integers
        plt.locator_params(axis='y', integer=True)

        # Add annotations to each bar
        for bar in ax:
            yval = bar.get_height()
            # Only add annotation if the value is not zero
            if yval > 0:
                plt.text(
                    bar.get_x() + bar.get_width()/2,
                    yval,
                    int(yval),
                    va='bottom',
                    ha='center',
                    )

        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'outlier_losses.png')
        plt.close()

    def plot_points_against(self):
        """Plot points against for each manager across all seasons.

        For each season, the winner of that year will be highlighted.
        """

        # Calculate the league average points against for each season
        league_avg = (
            self.df_standings.groupby('season')['pa']
            .transform('mean')
            .rename('league_avg')
        )
        df = pd.concat([self.df_standings, league_avg], axis=1)

        # Calculate the difference from the league average
        df['diff_from_avg'] = df['pa'] - df['league_avg']

        # Create the line plot
        plt.figure(figsize=(10, 7))
        sns.lineplot(
            x='season',
            y='diff_from_avg',
            hue='manager',
            style='manager',
            data=df,
            markers=True,
            markersize=8,
            linewidth=2.5
        )

        # Identify the league winners for each season
        winners_df = df[df['rank'] == 1]

        # Plot the league winners with a distinct marker
        plt.scatter(
            winners_df['season'],
            winners_df['diff_from_avg'],
            s=200,
            marker='*',
            color='gold',
            edgecolor='black',
            zorder=10,
            label='League Winner'
        )

        # Add a horizontal line at y=0
        plt.axhline(0, color='gray', linestyle='--', linewidth=1.5)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)

        plt.title(
            'Manager Points Against vs. League Average by Season',
            fontsize=16
            )
        plt.xlabel('Season', fontsize=12)
        plt.ylabel('Points Against - League Average', fontsize=12)
        plt.legend(title='Manager', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()

        # Set integer ticks for the x-axis
        plt.xticks(df['season'].unique())

        plt.savefig(self.PLOTS_DIR / 'seasonal_points_against_line_plot.png')
        plt.close()

        # Calculate the cumulative points for and against for each manager
        cumulative_df = df.groupby('manager').agg(
            cumulative_pf=('pf', 'sum'),
            cumulative_pa=('pa', 'sum')
        ).reset_index()

        # Calculate the cumulative league average for points for and against
        league_avg_pf = (
            df['pf'].sum() / len(df['manager'].unique())
        )
        league_avg_pa = (
            df['pa'].sum() / len(df['manager'].unique())
        )

        # Add the cumulative differences to the DataFrame
        cumulative_df['pf_diff'] = (
            cumulative_df['cumulative_pf'] - league_avg_pf
        )

        cumulative_df['pa_diff'] = (
            cumulative_df['cumulative_pa'] - league_avg_pa
        )

        # Restructure the DataFrame for grouped bar plotting
        plot_df = pd.melt(
            cumulative_df,
            id_vars=['manager'],
            value_vars=['pf_diff', 'pa_diff'],
            var_name='metric',
            value_name='diff_from_avg'
        )
        plot_df['metric'] = plot_df['metric'].map({
            'pf_diff': 'Points For',
            'pa_diff': 'Points Against'
        })

        # Create the grouped bar plot
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(
            x='manager',
            y='diff_from_avg',
            hue='metric',
            data=plot_df,
            palette={'Points For': 'blue', 'Points Against': 'red'}
        )

        # Add annotations to the bars
        for p in ax.patches:
            if p.get_height() == 0.0:
                continue
            ax.annotate(f'{p.get_height():.1f}',
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center',
                        xytext=(0, 10 if p.get_height() >= 0 else -15),
                        textcoords='offset points',
                        fontsize=10,
                        fontweight='bold')

        plt.grid(True, axis='y')
        ax.set_axisbelow(True)

        # Add a horizontal line at y=0
        plt.axhline(0, color='black', linewidth=1)

        plt.ylim(
            (
                round(min(plot_df['diff_from_avg'])-200, -2),
                round(max(plot_df['diff_from_avg'])+200, -2),
             )
        )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Cumulative Points For/Against vs. League Average',
            fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Difference from Cumulative League Average', fontsize=12)
        plt.legend(title='Metric', loc='lower right')
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'cumulative_performance_bar_plot.png')
        plt.close()

    def plot_winnings(self):
        """Plot the total winnings of each manager.

        Account for the annual dues of each manager, and their total winnings
        based on each manager's final rank.
        """

        with open('league_dues.json', 'r') as f:
            league_dues = json.load(f)

        df = self.df_standings

        total_winnings = dict.fromkeys(df['manager'].unique(), 0)

        for season in df['season'].unique():

            for manager in df['manager'].unique():

                rank = (
                    df.loc[(df['season'] == season) &
                           (df['manager'] == manager), 'rank'].item()
                )

                total_winnings[manager] += (
                    league_dues[f'{season}']["payouts"][rank-1] -
                    league_dues[f'{season}']["dues"]
                )

        total_winnings = pd.DataFrame.from_dict(
            total_winnings,
            orient='index',
            columns=['total_winnings'],
            )

        # Rename columns for clarity
        total_winnings = (
            total_winnings.reset_index().rename(columns={'index': 'manager'})
        )

        # Sort the DataFrame by total winnings in descending order
        total_winnings = total_winnings.sort_values(
            by='total_winnings',
            ascending=False
            )

        # Create the bar chart
        plt.figure(figsize=(10, 7))
        ax = sns.barplot(
            x='manager',
            y='total_winnings',
            data=total_winnings,
            palette='viridis',
            hue='manager',
            legend=False,
            order=total_winnings['manager']
        )
        plt.grid(True, axis='y')
        ax.set_axisbelow(True)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title('Total Fantasy League Winnings by Manager', fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Total Winnings ($)', fontsize=12)

        # Add value labels on top of the bars for positive values and below
        # for negative values
        for i, bar in enumerate(ax.patches):
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()

            # Get the value to annotate from the sorted DataFrame
            winnings_value = (
                total_winnings.iloc[i]['total_winnings']
            )

            # Determine text position and vertical alignment based on sign
            if winnings_value >= 0:
                vertical_alignment = 'bottom'
                y_pos = y + 5  # Small offset above the bar
            else:
                vertical_alignment = 'top'
                y_pos = y - 5  # Small offset below the bar

            ax.text(
                x,
                y_pos,
                f"${winnings_value}",
                ha='center',
                va=vertical_alignment,
                fontsize=10,
                fontweight='bold'
            )

        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'total_winnings_bar_chart.png')
        plt.close()

    def plot_manager_perf(self):
        """Plot manager point differential vs. win percentage.

        Create a scatter plot of each manager's cumulative point differntial
        vs. their win percentage.
        """

        df_standings = self.df_standings

        # Calculate cumulative stats for each manager
        cumulative_df = df_standings.groupby('manager').agg({
            'pf': 'sum',
            'pa': 'sum',
            'wins': 'sum',
            'losses': 'sum'
        }).reset_index()

        # Calculate total point differential (PF - PA)
        cumulative_df['total_point_diff'] = (
            cumulative_df['pf'] - cumulative_df['pa']
        )

        cumulative_df['win_percentage'] = (
            cumulative_df['wins'] / (
                cumulative_df['wins'] + cumulative_df['losses']
                )
        )

        # Create the scatter plot
        plt.figure(figsize=(12, 8))

        # Plot the linear regression trend line first to be behind the markers
        sns.regplot(
            x='total_point_diff',
            y='win_percentage',
            data=cumulative_df,
            scatter=False,
            color='gray',
            line_kws={'linestyle': '--', 'alpha': 0.7}
        )

        ax = sns.scatterplot(
            x='total_point_diff',
            y='win_percentage',
            hue='manager',
            style='manager',
            s=200,
            data=cumulative_df
        )

        ax.set_ylim((0.33, 0.66))
        ax.set_xlim((-1200, +1200))

        # Add annotations
        texts = []
        for i, row in cumulative_df.iterrows():
            texts.append(
                ax.text(
                    row["total_point_diff"],
                    row["win_percentage"],
                    row["manager"],
                    fontsize=9,
                    weight="bold")
                    )

        # Automatically adjust to avoid overlap
        adjust_text(
            texts,
            arrowprops=dict(
                arrowstyle="->",
                color="gray",
                lw=0.5,
                shrinkA=5,   # move arrow start away from text
                shrinkB=5    # move arrow end away from marker
            )
        )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Win Percentage vs. Total Point Differential (All Seasons)',
            fontsize=16
            )
        plt.xlabel('Total Points For - Total Points Against', fontsize=12)
        plt.ylabel('Win Percentage', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)

        handles, labels = ax.get_legend_handles_labels()

        line_handle = Line2D([0], [0], color='gray', linestyle='--', alpha=0.7)

        handles.append(line_handle)
        labels.append('Linear Trend Line')

        ax.legend(
            handles=handles,
            labels=labels,
            title='Manager',
            bbox_to_anchor=(1.05, 1),
            loc='upper left',

            )

        ax.get_legend().remove()

        plt.tight_layout(rect=[0, 0, 0.9, 1])
        plt.savefig(self.PLOTS_DIR / 'manager_win_vs_point_diff.png')
        plt.close()

    def plot_manager_finish(self):
        """Plot manager end of season placement.

        Include end of regular season (playoff seed) and final playoff ranking.
        Potential future improvement can include ignoring "consolation bracket"
        matchups.
        """

        df = self.df_standings

        # Calculate the average rank for each manager
        avg_seed = (
            df.groupby('manager')['seed'].mean()
            .reset_index().sort_values(by='seed')
        )
        avg_rank = (
            df.groupby('manager')['rank'].mean()
            .reset_index().sort_values(by='rank')
        )

        # --- Plot 1: Average Seed ---
        plt.figure(figsize=(10, 6))
        bars = sns.barplot(
            data=avg_seed,
            x='manager',
            y='seed',
            hue='manager',
            palette='Blues_r'
        )

        plt.grid(True, axis='y')
        bars.set_axisbelow(True)

        # Add annotations to the bars
        for bar in bars.patches:
            yval = bar.get_height()
            bars.text(
                bar.get_x() + bar.get_width()/2,
                yval,
                f'{yval:.2f}',
                ha='center',
                va='bottom'
                )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title('Average Playoff Seed per Manager', fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.ylabel('Average Seed', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'average_seed_barchart.png')
        plt.close()

        # --- Plot 2: Average Rank ---
        plt.figure(figsize=(10, 6))
        bars = sns.barplot(
            data=avg_rank,
            x='manager',
            y='rank',
            hue='manager',
            palette='Greens_r'
            )

        plt.grid(True, axis='y')
        bars.set_axisbelow(True)

        # Add annotations to the bars
        for bar in bars.patches:
            yval = bar.get_height()
            bars.text(
                bar.get_x() + bar.get_width()/2,
                yval,
                f'{yval:.2f}',
                ha='center',
                va='bottom'
                )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title('Average Overall Playoff Finish per Manager', fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.ylabel('Average Rank', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'average_rank_barchart.png')
        plt.close()

    def deprecated_plot_upsets(self):
        """DEPRECATED Plot matchup upsets in terms of projected points
        vs. actual outcome.

        Using a given threshold, determine if each matchup is an upset
        and generate output plots.

        TODO: This plot is better served as an interactive plot.
        """

        df = self.df

        threshold = 10

        # --- Projected outcome ---
        proj_conditions = [
            (df['proj_points'] - df['opp_proj_points'] > threshold),
            (df['opp_proj_points'] - df['proj_points'] > threshold)
        ]
        proj_choices = ['win', 'loss']

        df['proj_outcome'] = np.select(
            proj_conditions,
            proj_choices,
            default='close'
            )

        # --- Actual outcome ---
        actual_conditions = [
            (df['points'] - df['opp_points'] > threshold),
            (df['opp_points'] - df['points'] > threshold)
        ]
        actual_choices = ['win', 'loss']

        df['actual_outcome'] = np.select(
            actual_conditions,
            actual_choices,
            default='close'
            )

        # Define "upset" conditions
        df['upset_victory'] = (
            (df['proj_outcome'] == 'loss') &
            (df['actual_outcome'] == 'win')).astype(int)

        df['upset_loss'] = (
            (df['proj_outcome'] == 'win') &
            (df['actual_outcome'] == 'loss')).astype(int)

        # Calculate total upsets for each manager
        upset_summary = df.groupby('manager').agg(
            upset_victories=('upset_victory', 'sum'),
            upset_losses=('upset_loss', 'sum')
        ).reset_index()

        # Calculate net upset record
        upset_summary['net_upset_record'] = (
            upset_summary['upset_victories'] - upset_summary['upset_losses']
        )

        # Sort managers by net upset record for better visualization
        upset_summary = upset_summary.sort_values(
            by='net_upset_record', ascending=False
            )

        # Create the bar plot
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")

        # Create a color palette based on positive or negative net upset record
        colors = ['green' if x > 0
                  else 'red' for x in upset_summary['net_upset_record']]

        ax = sns.barplot(
            x='manager',
            y='net_upset_record',
            hue='manager',
            palette=colors,
            data=upset_summary,
            legend=False
        )

        # Add value labels on each bar
        for p in ax.patches:
            ax.annotate(
                text=f'{int(p.get_height())}',
                xy=(p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center',
                va='center',
                xytext=(0, 10 if p.get_height() > 0 else -15),
                textcoords='offset points', fontsize=12
                )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            'Net Upset Record (Upset Wins - Upset Losses)\n'
            'Win-Loss Record of Opposite Result from Projected Outcome',
            fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.ylabel('Net Upset Record', fontsize=12)

        # Add a line at y=0 for reference
        plt.axhline(0, color='black', linewidth=1.5)

        plt.grid(axis='x', linestyle='', alpha=0)
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'net_upset_record_bar_plot.png')
        plt.close()

    def plot_total_trades(self):
        """Plot count of trades made between managers.
        """

        df = self.df_trades

        # Count trades by each role
        trader_counts = df['trader'].value_counts()
        tradee_counts = df['tradee'].value_counts()

        # Combine into a single Series
        all_counts = trader_counts.add(tradee_counts, fill_value=0)

        # Reindex with all managers (missing get 0)
        all_counts = all_counts.reindex(
            self.df['manager'].unique(), fill_value=0
            )

        # Sort by most active
        all_counts = all_counts.sort_values(ascending=False)

        # Plot bar chart
        plt.figure(figsize=(10, 6))
        ax = all_counts.plot(kind='bar', color='skyblue', edgecolor='black')

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title("Trade Count by Manager")
        plt.xlabel("Manager")
        plt.ylabel("Number of Trades")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis='x', linestyle='', alpha=0, visible=True)
        ax.set_axisbelow(True)
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'total_trades.png')
        plt.close()

    def plot_trade_mapping(self):
        """Generate a bar plot of total trades made by each manager. Also
        create a network graph of the trades made between all managers.
        """

        df = self.df_trades

        # Build the graph
        G = nx.Graph()
        edges = list(zip(df['trader'], df['tradee']))

        # Add weighted edges (weight = number of trades between same pair)
        for trader, tradee in edges:
            if G.has_edge(trader, tradee):
                G[trader][tradee]['weight'] += 1
            else:
                G.add_edge(trader, tradee, weight=1)

        # Ensure all managers appear, even if isolated
        G.add_nodes_from(self.df['manager'].unique())

        # Draw the graph
        plt.figure(figsize=(10, 8))

        pos = nx.spring_layout(G, seed=42, k=0.5)  # consistent layout

        # Extract weights for line thickness
        weights = [G[u][v]['weight'] for u, v in G.edges()]

        nx.draw_networkx_nodes(
            G, pos, node_size=1500, node_color="skyblue", edgecolors="black"
            )
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
        nx.draw_networkx_edges(G, pos, width=[w for w in weights], alpha=0.6)

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title("Trade Network", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'trade_network.png')
        plt.close()

    def plot_draft_cost_points(self):

        df = pd.read_csv(self.DATA_DIR / 'draft_results.csv')

        plt.figure(figsize=(8, 6))
        sns.scatterplot(x='player_cost', y='points', data=df)

        plt.xlabel("Player Auction Draft Cost")
        plt.ylabel("Points Scored for Original Manager")
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title("Player Auction Draft Cost vs. Points Scored")
        plt.grid(True, linestyle="--", alpha=0.6)

        # Format x-axis with dollar signs
        plt.gca().xaxis.set_major_formatter(
            mtick.StrMethodFormatter('${x:,.0f}'))

        x_mean = df['player_cost'].mean()
        y_mean = df['points'].median()

        # Draw quadrant lines
        plt.axvline(x=x_mean, color='red', linestyle='--', alpha=0.7)
        plt.axhline(y=y_mean, color='red', linestyle='--', alpha=0.7)

        # Get current axis limits
        plt.xlim((0, 100))
        plt.ylim((-50, 500))
        x_min, x_max = plt.xlim()
        y_min, y_max = plt.ylim()

        x_pad = (x_max - x_min) * 0.02
        y_pad = (y_max - y_min) * 0.02

        # Place quadrant labels in corners
        plt.text(
            x_max - x_pad, y_max - y_pad,
            "As Advertised", fontsize=14, color="black", ha='right', va='top')
        plt.text(
            x_min + x_pad, y_max - y_pad,
            "Value\nPicks", fontsize=14, color="black", ha='left', va='top')
        plt.text(
            x_min + x_pad, y_min + y_pad,
            "JAGs", fontsize=14, color="black", ha='left', va='bottom')
        plt.text(
            x_max - x_pad, y_min + y_pad, "Busts",
            fontsize=14, color="black", ha='right', va='bottom')
        plt.tight_layout()
        plt.savefig(self.PLOTS_DIR / 'draft_scatter.png')
        plt.close()

        # Busts
        busts = df[
            (df['points'] < y_mean) &
            (df['player_cost'] > 40)
        ].reset_index()

        busts = busts.sort_values(
            by=['player_cost', 'points'],
            ascending=[False, True],
            )

        for k, row in busts.iterrows():
            print(
                f"{row['season']} - "
                f"{row['manager']} - "
                f"{row['player_name']} ({row['player_pos']}) - "
                f"${row['player_cost']} / {row['points']:0.2f}pts"
            )

        # Values
        values = df[
            (df['points'] > 275) &
            (df['player_cost'] < x_mean)
        ].reset_index()

        values = values.sort_values(
            by=['player_cost', 'points'],
            ascending=[True, True],
            )

        print()

        for k, row in values.iterrows():
            print(
                f"{row['season']} - "
                f"{row['manager']} - "
                f"{row['player_name']} ({row['player_pos']}) - "
                f"${row['player_cost']} / {row['points']:0.2f}pts"
            )

        for season in df['season'].unique():

            print(f"{season}")

            for k, rank in enumerate(["1st", "2nd", "3rd"]):
                df1 = self.df_standings[
                    (self.df_standings['season'] == season) &
                    (self.df_standings['rank'] == k+1)
                ].reset_index()

                winner = df1.loc[0, 'manager']

                qbs = df[
                    (df['manager'] == winner) &
                    (df['season'] == season) &
                    (df['player_pos'] == "QB")
                ]

                print(
                    f"\t{rank} - {winner} - {qbs['player_cost'].sum()} QB $s")
            print()

    def plot_pts_by_roster_spot(self):
        """
        """

        df = self.df

        all_managers = {}
        all_managers2 = {}

        js = []

        for manager in df["manager"].unique():

            pts_by_pos = defaultdict(int)
            pts_by_ros = defaultdict(int)

            s = df[df["manager"] == manager]

            for k, row in s.iterrows():
                roster = eval(row["roster"])
                # print(roster)

                for r in roster:
                    pts_by_ros[r[2]] += r[3]

                    if r[2] == "BN":
                        pts_by_pos["BN_" + r[4]] += r[3]
                    else:
                        pts_by_pos[r[4]] += r[3]

            all_managers[manager] = pts_by_ros
            all_managers2[manager] = pts_by_pos

        for manager in df["manager"].unique():
            s = df[df["manager"] == manager]

            for season in s["season"].unique():
                t = s[s["season"] == season]

                pts_by_ros = defaultdict(int)

                for k, row in t.iterrows():
                    roster = eval(row["roster"])

                    for r in roster:
                        pts_by_ros[r[2]] += r[3]

                for key, value in pts_by_ros.items():
                    entry = {
                        "manager": manager,
                        "season": int(season),
                        "position": key,
                        "points": value,
                    }
                    js.append(entry)
        print(js)

        with open("_data/rosters.json", "w") as f:
            json.dump(js, f, indent=3)

        custom_order = [
            'QB', 'RB', 'WR', 'TE', 'W/R/T', 'W/T', 'DEF', 'K', 'BN', 'IR'
        ]

        # Convert to DataFrame and transform to "long" format for plotting
        df = pd.DataFrame.from_dict(
            all_managers, orient='index').reset_index().rename(
                columns={'index': 'Manager'})
        df_long = df.melt(
            id_vars='Manager', var_name='Position', value_name='Value')

        managers = sorted(df['Manager'].unique().tolist())

        # Use a colormap suitable for up to 20 distinct categories
        cmap = plt.cm.get_cmap('tab20', 12)
        manager_to_color = {m: cmap(i) for i, m in enumerate(managers)}

        # Define 12 unique markers for better separation
        unique_markers = [
            'o', 's', '^', 'D', 'p', '*', 'h', 'v', '>', '<', 'X', 'P']
        manager_to_marker = {
            m: unique_markers[
                i % len(unique_markers)] for i, m in enumerate(managers)}

        position_to_x = {pos: i for i, pos in enumerate(custom_order)}

        plt.figure(figsize=(14, 8))
        ax = plt.gca()

        # Plotting with Jitter (Dodge) and Markers
        manager_offsets = np.linspace(-0.4, 0.4, 12)
        offset_map = dict(zip(managers, manager_offsets))

        # Calculate the base numerical x-position for each data point
        df_long['x_base'] = df_long['Position'].apply(
            lambda p: position_to_x[p])

        for manager in managers:
            subset = df_long[df_long['Manager'] == manager]

            x_pos = subset['x_base'] + offset_map[manager]
            y_pos = subset['Value']

            # Plot the points using Matplotlib's scatter
            ax.scatter(
                x_pos,
                y_pos,
                label=manager,
                color=manager_to_color[manager],
                marker=manager_to_marker[manager],
                s=80,
                edgecolors='black',
                linewidths=0.5
            )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        ax.set_title(
            'Roster Position Points Comparison Across All Managers',
            fontsize=16,
            )
        ax.set_xlabel('Roster Position', fontsize=12)
        ax.set_ylabel('Points', fontsize=12)

        # Set the X-ticks to the position names
        ax.set_xticks(np.arange(len(custom_order)))
        ax.set_xticklabels(custom_order, rotation=45, ha='right')

        # --- FIX: Set vertical grid lines at mid-points to box the data ---
        # Grid lines should be placed at 0.5, 1.5, 2.5, ..., 9.5, 10.5
        grid_ticks = np.arange(-0.5, len(custom_order) + 0.5, 1)

        # Add vertical grid lines
        ax.set_xticks(grid_ticks, minor=True)
        ax.grid(
            axis='x',
            which='minor',
            linestyle='-',
            alpha=0.9,
            color='lightgray',
            linewidth=1.5,
            )

        # Hide minor ticks if they appear
        ax.tick_params(axis='x', which='minor', size=0)

        # Remove the default grid lines that were aligned with the labels
        ax.grid(axis='x', which='major', visible=False)

        # Keep the horizontal (y-axis) grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        # Set X-limits to ensure the first and last boxes are fully drawn
        ax.set_xlim(grid_ticks.min(), grid_ticks.max())

        ax.legend(
            title='Manager',
            loc='upper left',
            bbox_to_anchor=(1.01, 1),
            ncol=1,
            fontsize=8,
            )

        # Adjust layout to make room for the 2-column legend
        plt.tight_layout(rect=[0, 0, 0.88, 1])

        plt.savefig(self.PLOTS_DIR / 'player_ros_pts_by_manager.png')
        plt.close()

        custom_order = [
            'QB', 'RB', 'WR', 'TE',
            'DEF', 'K',
            'BN_QB', 'BN_RB', 'BN_WR', 'BN_TE',
            'BN_DEF', 'BN_K',
            ]

        # Convert to DataFrame and transform to "long" format for plotting
        df = pd.DataFrame.from_dict(
            all_managers2, orient='index').reset_index().rename(
                columns={'index': 'Manager'})

        df_long = df.melt(
            id_vars='Manager',
            var_name='Position',
            value_name='Value',
            )

        # Use a colormap suitable for up to 20 distinct categories
        cmap = plt.cm.get_cmap('tab20', 12)
        manager_to_color = {m: cmap(i) for i, m in enumerate(managers)}

        # Define 12 unique markers for better separation
        unique_markers = [
            'o', 's', '^', 'D', 'p', '*', 'h', 'v', '>', '<', 'X', 'P']
        manager_to_marker = {
            m: unique_markers[
                i % len(unique_markers)] for i, m in enumerate(managers)}

        position_to_x = {pos: i for i, pos in enumerate(custom_order)}

        plt.figure(figsize=(14, 8))
        ax = plt.gca()

        # Manual Plotting with Jitter (Dodge) and Markers
        manager_offsets = np.linspace(-0.4, 0.4, 12)
        offset_map = dict(zip(managers, manager_offsets))

        # Calculate the base numerical x-position for each data point
        df_long['x_base'] = df_long['Position'].apply(
            lambda p: position_to_x[p])

        for manager in managers:
            subset = df_long[df_long['Manager'] == manager]

            x_pos = subset['x_base'] + offset_map[manager]
            y_pos = subset['Value']

            # Plot the points using Matplotlib's scatter
            ax.scatter(
                x_pos,
                y_pos,
                label=manager,
                color=manager_to_color[manager],
                marker=manager_to_marker[manager],
                s=80,
                edgecolors='black',
                linewidths=0.5
            )

        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        ax.set_title(
            'Player Position Points Comparison Across All Managers',
            fontsize=16,
            )
        ax.set_xlabel('Player Position', fontsize=12)
        ax.set_ylabel('Points', fontsize=12)

        # Set the X-ticks to the position names
        ax.set_xticks(np.arange(len(custom_order)))
        ax.set_xticklabels(custom_order, rotation=45, ha='right')

        # --- FIX: Set vertical grid lines at mid-points to box the data ---
        # Grid lines should be placed at 0.5, 1.5, 2.5, ..., 9.5, 10.5
        grid_ticks = np.arange(-0.5, len(custom_order) + 0.5, 1)

        # Add vertical grid lines
        ax.set_xticks(grid_ticks, minor=True)
        ax.grid(
            axis='x',
            which='minor',
            linestyle='-',
            alpha=0.9,
            color='lightgray',
            linewidth=1.5,
            )

        # Hide minor ticks if they appear
        ax.tick_params(axis='x', which='minor', size=0)

        # Remove the default grid lines that were aligned with the labels
        ax.grid(axis='x', which='major', visible=False)

        # Keep the horizontal (y-axis) grid lines
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        # Set X-limits to ensure the first and last boxes are fully drawn
        ax.set_xlim(grid_ticks.min(), grid_ticks.max())

        # Move the legend outside the plot, using 2 columns
        ax.legend(
            title='Manager',
            loc='upper left',
            bbox_to_anchor=(1.01, 1),
            ncol=1,
            fontsize=8,
            )

        # Adjust layout to make room for the 2-column legend
        plt.tight_layout(rect=[0, 0, 0.88, 1])

        plt.savefig(self.PLOTS_DIR / 'player_pos_pts_by_manager.png')
        plt.close()

    def plot_optimum_lineup(self):
        """
        """

        df = self.df

        mx = -1e9
        mx_str = ""

        sqr_pts_sum = 0.0
        total_w = 0

        m = defaultdict(lambda: {'opt_cnt': 0, 'sqr_pts': 0.0, 'flips': 0})

        for k, row in df.iterrows():

            roster = eval(row['roster'])
            s_roster = sorted(roster, key=lambda item: item[3], reverse=True)

            # print(roster)
            # print()
            # print(s_roster)
            # exit(0)

            manager = row['manager']
            week = row['week']
            season = row['season']

            starters = []
            bench = []
            optimum = []
            slots = []

            pts = 0
            opt_pts = 0

            for r in roster:
                if r[2] == 'BN' or r[2] == 'IR':
                    bench.append(r)
                else:
                    starters.append(r)
                    slots.append(r[2])
                    pts += r[3]

            for s in slots:
                kp = None
                for k, p in enumerate(s_roster):
                    if (
                        # Roster slot position matches player position
                        (s == p[4]) or
                        # Elseif is full FLEX
                        (s == "W/R/T" and (
                            p[4] == "WR" or p[4] == "RB" or p[4] == "TE")) or
                        # Elseif is WR or TE
                        (s == "W/T" and (p[4] == "WR" or p[4] == "TE"))
                    ):
                        kp = k
                        opt_pts += p[3]
                        break

                optimum.append(s_roster.pop(kp))

            # print(f"{manager}: Week {week} {season} | {pts} vs {opt_pts}")

            # DEBUG
            # Sanity check sum of player points vs. team scores
            # if round(pts, 2) != round(row['points'], 2):
            #     print("Points Mismatch")
            #     print(
            #         f"{manager}: Week {week} {season} - "
            #         f"{pts:0.2f} {row['points']:0.2f}\n"
            #         )

            if pts == opt_pts:
                # print(
                #     f"{manager}: Week {week} {season} - "
                #     f"Optimum Lineup {opt_pts:0.2f} pts"
                #     )
                m[manager]['opt_cnt'] += 1

            else:
                sqr_pts = opt_pts - pts
                m[manager]['sqr_pts'] += sqr_pts

                # Manual trivia extraction here
                if sqr_pts > mx and manager == "Chris":
                    mx = sqr_pts
                    mx_str = f"{manager}: Week {week} {season} | {opt_pts} pts"

                sqr_pts_sum += sqr_pts

                if opt_pts > row['opp_points'] and pts < row['opp_points']:
                    m[manager]['flips'] += 1

            total_w += 1

        print(f"{mx_str} {mx} pts")
        print(f"{sqr_pts_sum / total_w} {total_w}")

        # Create a list of (category, count) tuples
        data_pairs = [(key, data['opt_cnt']) for key, data in m.items()]

        sorted_data = sorted(
            data_pairs,
            key=lambda item: item[1],
            reverse=True,
            )

        # Unpack the sorted data for plotting
        categories = [item[0] for item in sorted_data]
        counts = [item[1] for item in sorted_data]

        plt.figure(figsize=(8, 6))
        plt.bar(categories, counts, color='skyblue')

        # Add labels and title
        plt.xlabel('Manager')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Num. of Optimum Lineup Weeks')
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title(
            "Weeks of Setting Optimum Lineup (No Squandered Bench Points)"
            )

        # Optional: Add the count value on top of each bar
        for i, count in enumerate(counts):
            plt.text(i, count + 0.1, str(count), ha='center', va='bottom')

        plt.tight_layout()

        # Display the chart (The output image is shown above)
        plt.savefig(self.PLOTS_DIR / 'opt_lineup_chart_counts.png')

        # Create a list of (category, count) tuples
        data_pairs = [(key, data['flips']) for key, data in m.items()]

        sorted_data = sorted(
            data_pairs,
            key=lambda item: item[1],
            reverse=True,
            )

        # Unpack the sorted data for plotting
        categories = [item[0] for item in sorted_data]
        counts = [item[1] for item in sorted_data]

        plt.figure(figsize=(8, 6))
        plt.bar(categories, counts, color='skyblue')

        # Add labels and title
        plt.xlabel('Manager')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of "Flipped" Games (Loss Becomes Win)')
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title("Num. Additional Wins With Optimal Lineup")

        # Optional: Add the count value on top of each bar
        for i, count in enumerate(counts):
            plt.text(
                i,
                count + 0.1,
                str(round(count)),
                ha='center',
                va='bottom',
                )

        plt.tight_layout()

        # Display the chart (The output image is shown above)
        plt.savefig(self.PLOTS_DIR / 'flips_chart_counts.png')

        # Create a list of (category, count) tuples
        data_pairs = [(key, data['sqr_pts']) for key, data in m.items()]

        sorted_data = sorted(
            data_pairs,
            key=lambda item: item[1],
            reverse=True,
            )

        # Unpack the sorted data for plotting
        categories = [item[0] for item in sorted_data]
        counts = [item[1] for item in sorted_data]

        plt.figure(figsize=(8, 6))
        plt.bar(categories, counts, color='skyblue')

        # Add labels and title
        plt.xlabel('Manager')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Total Squandered Bench Points')
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title("Squandered Bench Points")

        # Optional: Add the count value on top of each bar
        for i, count in enumerate(counts):
            plt.text(
                i,
                count + 0.1,
                str(round(count)),
                ha='center',
                va='bottom',
                )

        plt.tight_layout()

        # Display the chart (The output image is shown above)
        plt.savefig(self.PLOTS_DIR / 'squandered_pts_chart_counts.png')

    def plot_kicker_tackles(self):
        """
        """

        df_stats = pd.read_csv("nfl_player_stats.csv")

        df = self.df

        k_tkl_count = 0
        dlta_sum = 0
        k_tkl_thrs_count = 0

        qbs = []
        wrs = []
        rbs = []
        ks = []
        ks_tkl = []

        for k, df_row in df.iterrows():

            roster = eval(df_row["roster"])

            manager = df_row["manager"]
            opp_manager = df_row["opponent"]
            season = df_row["season"]
            week = df_row["week"]
            pts = df_row["points"]
            opp_pts = df_row["opp_points"]
            dlta = pts - opp_pts

            p_s = df_stats[
                (df_stats["season"] == season) &
                (df_stats["week"] == week)
            ]

            # Find kicker
            for r in roster:
                if r[4] == "QB":
                    qbs.append(r[3])
                if r[4] == "RB":
                    rbs.append(r[3])
                if r[4] == "WR":
                    wrs.append(r[3])


                if r[2] == "K":
                    ks.append(r[3])

                    first, last = r[0].split()

                    p_ss = p_s[
                        p_s["player_name"] == f"{first[0]}.{last}"
                    ].reset_index()

                    if p_ss.shape[0] != 1:
                        # print(f"|{first[0]}.{last}|")
                        # print(f"Week {week} {season} {r}")
                        # exit(0)
                        continue

                    k_tkl = p_ss.loc[0, "def_tackles_solo"]
                    ks_tkl.append(r[3] + k_tkl*8)

                    if k_tkl > 0:
                        # print(f"Week {week} {season} {r[0]} {k_tkl} | {pts} vs. {opp_pts}")

                        if opp_pts > pts:
                            dlta_sum += dlta
                            k_tkl_count += 1
                            # print(f"{manager} vs. {opp_manager} | Week {week} {season} {r[0]} - {k_tkl} tkl | {pts} vs. {opp_pts} ({dlta:0.2f} pts delta)")


                        if dlta < 0 and dlta > -10:
                            print(f"{manager} vs. {opp_manager} | Week {week} {season} {r[0]} - {k_tkl} tkl | {pts} vs. {opp_pts} ({dlta:0.2f} pts delta)")
                            k_tkl_thrs_count += 1

        print(f"Total Matchups with Kicker Tackles: {k_tkl_count}")
        print(f"Average Matchup Delta: {dlta_sum / k_tkl_count}")
        print(f"Total Matchups with 10-point (or less) Deltas: {k_tkl_thrs_count}")

        plt.figure(figsize=(10, 6))

        # Plot the Kernel Density Estimate (KDE) line
        sns.kdeplot(qbs, color='darkorange', linewidth=3, label="QBs")
        sns.kdeplot(rbs, color='darkgreen', linewidth=3, label="RBs")
        sns.kdeplot(wrs, color='lightgreen', linewidth=3, label="WRs")
        sns.kdeplot(ks, color='blue', linewidth=3, label="Ks (standard)")
        sns.kdeplot(ks_tkl, color='lightblue', linewidth=3, label="Ks (tackle pts)")

        # 3. Add title and labels
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
        plt.title('Distribution Shape of Position Scoring (Kernel Density Estimates)', fontsize=16)
        plt.xlabel('Weekly Points', fontsize=12)
        plt.ylabel('Density', fontsize=12)
        plt.grid(axis='y', alpha=0.5)
        plt.legend(loc="upper right", bbox_to_anchor=(1.05, 1))

        plt.tight_layout()
        # 4. Save the plot
        plt.savefig('kde_plot.png')
        plt.close()

    def plot_last_win(self):
        """
        """

        last_wins = {}

        longest = 0
        t_str = "None"

        df = self.df

        curr_season = df.iloc[-1, df.columns.get_loc('season')]
        curr_week = df.iloc[-1, df.columns.get_loc('week')]

        min_season = df.iloc[0, df.columns.get_loc('season')]

        weeks_now = (curr_season-min_season)*52 + curr_week

        for manager in df["manager"].unique():

            if manager != "Eric":
                continue

            s0 = df[df["manager"] == manager]

            opps = {}
            w_str = "Never"

            man_longest = 0
            man_str = "Never"

            for opponent in s0["opponent"].unique():
                s1 = s0[
                    s0["opponent"] == opponent
                    ].reset_index()

                wins = s1[
                    s1["points"] > s1["opp_points"]
                ].reset_index()

                if wins.shape[0] > 0:
                    k = wins.shape[0] - 1

                    wk = int(wins.loc[k, "week"])
                    sn = int(wins.loc[k, "season"])

                    w_str = f"Week {wk} {sn}"
                    opps[opponent] = w_str

                    t_weeks = weeks_now - (sn-min_season)*52 + wk

                    # print(f"{t_weeks}\t{longest}")

                    k = ((s1["season"] == sn) & (s1["week"] == wk)).idxmax()
                    s2 = s1.iloc[k+1:]

                    tot_losses = s2.shape[0]
                    consol_losses = s2["is_consolation"].sum()
                    playoff_losses = s2["is_playoffs"].sum() - consol_losses

                    if t_weeks > longest:
                        longest = t_weeks
                        t_str = f"{manager} vs {opponent} - {w_str} ({tot_losses}, {playoff_losses}, {consol_losses})"

                    if t_weeks > man_longest:
                        man_longest = t_weeks
                        man_str = f"{manager} vs {opponent} - {w_str} ({tot_losses}, {playoff_losses}, {consol_losses})"

            last_wins[manager] = opps
            print(man_str)

            print(manager)
            print(opps)
            print()

        # print(last_wins)
        print()
        print(t_str)

    def plot_monday_comebacks(self):
        """
        """

        df = self.df

        count = 0
        count2 = 0
        count3 = 0
        count4 = 0

        count2_sum = 0

        manager_counts = defaultdict(int)
        manager_opportunities = defaultdict(int)
        manager_needed = defaultdict(lambda: 1e9)
        manager_needed_s = dict()
        loser_counts = defaultdict(int)
        pos_counts = defaultdict(int)

        th_pts = 0

        max_win = -1e9
        min_win = 1e9

        managers = df['manager'].unique()

        total_matchups = df.shape[0] >> 1

        for k, row in df.iterrows():

            monday_players = []
            num_monday_players_opp = 0

            roster = eval(row["roster"])

            season = row["season"]
            week = row["week"]
            manager = row["manager"]
            opponent = row["opponent"]
            pts = row["points"]
            opp_pts = row["opp_points"]

            opp_row = df[
                (df["season"] == season) &
                (df["week"] == week) &
                (df["manager"] == opponent) &
                (df["opponent"] == manager)
            ].reset_index()

            opp_roster = eval(opp_row.loc[0, "roster"])

            for r in roster:
                day = r[5]

                active = True

                if r[2] == "BN" or r[2] == "IR":
                    active = False

                if day == "Monday" and active:
                    monday_players += [r]

            for r in opp_roster:
                day = r[5]

                active = True

                if r[2] == "BN" or r[2] == "IR":
                    active = False

                if day == "Monday" and active:
                    num_monday_players_opp += 1

            if len(monday_players) == 1 and num_monday_players_opp == 0:
                count += 1

                monday_pts = monday_players[0][3]
                r = monday_players[0]

                if (pts - monday_pts) + th_pts < opp_pts:
                    count2 += 1
                    count2_sum += opp_pts - (pts - monday_pts)

                    manager_opportunities[manager] += 1

                    needed = opp_pts - (pts - monday_pts)

                    s = (
                        f"Week {week:2d} {season} | "
                        f"{manager} ({pts}) vs. {opponent} ({opp_pts}) | "
                        f"{r[0]} ({r[1]} - {r[4]}): {r[3]:0.2f} pts "
                        f"(needed: {needed:0.2f})"
                    )

                    if pts > opp_pts:

                        count4 += 1
                        print(s)
                        print()

                        if pts - opp_pts < min_win:
                            min_s = s
                            min_win = pts - opp_pts

                        if needed > max_win:
                            max_s = s
                            max_win = needed

                        manager_counts[manager] += 1
                        loser_counts[opponent] += 1
                        pos_counts[monday_players[0][4]] += 1

                    else:

                        if needed < manager_needed[manager]:
                            manager_needed[manager] = needed
                            manager_needed_s[manager] = s

                else:
                    count3 += 1

        print(f"Matchups with 1 player remaining on Monday: {count} / {total_matchups} | ({100 * count / total_matchups:0.2f}%)")
        print(f"and where manager is behind by {th_pts} or more pts: {count2} ({count2_sum / count2:0.2f} pts avg.)")
        print(f"and where manager won: {count4} ({100*count4 / count:0.2f}%)")
        # print(count3)
        print(f"Num. MNF Comebacks by Manager: {dict(manager_counts)}")
        print(f"Num. MNF Comeback Chances by Manager: {dict(manager_opportunities)}")
        print(f"Num. MNF Comeback Victims by Manager: {dict(loser_counts)}")
        # print(loser_counts)
        print(pos_counts)
        print()
        print("Squeakiest Monday night comeback:")
        print(min_s)
        print(min_win)
        print()
        print("Biggest Monday night comeback:")
        print(max_s)
        print(max_win)
        print()

        for m in managers:
            print(m)
            print(manager_needed_s[m])
            print()

    def plot_cmc(self):
        """
        """

        df = self.df

        x = []
        y = []

        cmc_played = 0
        cmc_played_win = 0
        cmc_played_margin = 0

        cmc_benched = 0
        cmc_benched_win = 0
        cmc_benched_margin = 0

        man_wins = defaultdict(int)
        man_count = defaultdict(int)

        man_played = defaultdict(int)
        man_played_wins = defaultdict(int)

        for k, row in df.iterrows():

            # is_cmc = False

            # if row["is_playoffs"] == 0:
            #     continue

            # if row["is_consolation"] == 1:
            #     continue

            manager = row["manager"]
            season = row["season"]
            week = row["week"]

            cmc_pts = 0

            roster = eval(row["roster"])

            margin = row["points"] - row["opp_points"]

            for r in roster:
                if r[0] == "Christian McCaffrey":
                    cmc_pts = r[3]

                    print(f"Week {week} {season} | {manager} | {margin:0.2f} | {cmc_pts} [{r[2]}]")

                    man_count[manager] += 1
                    if margin > 0:
                        man_wins[manager] += 1

                    if r[2] == "IR" or r[2] == "BN":
                        cmc_benched += 1
                        cmc_benched_margin += margin

                        if margin > 0:
                            cmc_benched_win += 1

                    else:
                        cmc_played += 1
                        cmc_played_margin += margin
                        man_played[manager] += 1

                        if margin > 0:
                            cmc_played_win += 1
                            man_played_wins[manager] += 1


                    break

            x += [cmc_pts]
            y += [margin]

        print(f"{cmc_played} games rostered | {cmc_played_win / cmc_played:0.2f} | {cmc_played_margin / cmc_played:0.2f}")
        print(f"{cmc_benched} games benched | {cmc_benched_win / cmc_benched:0.2f} | {cmc_benched_margin / cmc_benched:0.2f}")

        for k in man_count:
            # print(k)
            print(f"{k} | {man_wins[k] / man_count[k]:0.2} | {man_wins[k]} / {man_count[k]}")
            if man_played[k] == 0:
                print(f"{k} | {man_played[k]} games played")

            else:
                print(f"{k} | {man_played_wins[k] / man_played[k]:0.2} | {man_played_wins[k]} / {man_played[k]}")
            # print(f"{k} | {man_played[k] / man_count[k]:0.2}")
            print()


        # plt.figure(figsize=(10, 7))

        # plt.scatter(
        #     x,
        #     y,
        #     s=200,
        #     marker='*',
        #     color='gold',
        #     edgecolor='black',
        #     zorder=10,
        #     label='League Winner'
        # )

        # plt.show()

    def plot_optimum_qbs(self):
        """
        """

        num_multi_qb = defaultdict(int)
        wrong_multi_qb = defaultdict(int)
        chc_wks = defaultdict(int)
        tot_qb_wks = defaultdict(int)

        df = self.df

        for k, row in df.iterrows():

            manager = row["manager"]
            weeks = row["week"]

            if manager != "Keara":
                continue

            roster = eval(row['roster'])

            qbs = []
            bn_pts = 0

            for r in roster:
                if r[4] == "QB":
                    tot_qb_wks[manager] += 1

                if r[4] == "QB" and r[5] != "BYE":
                    qbs += [r]

                    if r[2] == "QB":
                        qb_pts = r[3]
                    elif r[2] == "BN":
                        bn_pts = r[3]
                        if bn_pts > 0:
                            chc_wks[manager] += 1

            if len(qbs) > 1:
                num_multi_qb[manager] += 1

            if bn_pts > qb_pts:
                wrong_multi_qb[manager] += 1
                s = "WRONG"
            else:
                s = "Correct"

            print(f"Week {row["week"]} | {qbs} | {s}")

        for m in df["manager"].unique():

            print(m)
            print(f"\tMulti-QB weeks: {num_multi_qb[m]} / {weeks}")
            print(f"\tWrong QB start weeks: {wrong_multi_qb[m]} / {num_multi_qb[m]}")
            print(f"\tMulti-start QB weeks: {chc_wks[m]} / {num_multi_qb[m]}")
            print(f"\tTotal QB roster weeks: {tot_qb_wks[m]}")
            print()

    def plot_individual_perf(self):
        """
        """

        season = 2025

        df = self.df[self.df["season"] == season]

        mx = -1e9
        s = []

        for k, row in df.iterrows():

            manager = row["manager"]
            week = row["week"]

            roster = eval(row['roster'])

            for r in roster:

                if r[4] == "WR" or r[4] == "RB" or r[4] == "TE":

                    if r[3] > mx:
                        mx = r[3]
                        s = f"Week {week} | {manager} | {r}"

        print(s)

    def run(self):
        """Discovers and calls all plotting methods in the class.
        """
        # Use inspect.getmembers to find all methods of the class
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, method in members:
            if name.startswith('plot_'):
                print(f"Calling: {name}")
                method()


if __name__ == "__main__":

    p = Plotting()
    # p.plot_draft_cost_points()
    # p.plot_pts_by_roster_spot()
    # p.plot_optimum_lineup()
    # p.plot_kicker_tackles()
    # p.plot_proj_heatmap()
    # p.plot_last_win()
    # p.plot_monday_comebacks()
    # p.plot_cmc()
    # p.plot_optimum_qbs()
    p.plot_individual_perf()

