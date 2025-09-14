#!/usr/bin/env python3

import inspect
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx
import numpy as np

from adjustText import adjust_text
from pathlib import Path
from matplotlib.lines import Line2D
from statsmodels.formula.api import ols


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

        # Perform common pre-processing on the dataframes

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

                    avg_delta = matchup_df['point_diff'].mean()

                    # Annotations info
                    matchup_data.append([manager, opponent, avg_delta])
                    annot_data.append(
                        [manager, opponent, f"{record}\n{avg_delta:.2f}"]
                        )
                else:
                    matchup_data.append([manager, opponent, float('nan')])
                    annot_data.append([manager, opponent, ""])

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
        plt.savefig(self.PLOTS_DIR / 'fmls.png')
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
    p.run()
