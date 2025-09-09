#!/usr/bin/env python3

import inspect
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from adjustText import adjust_text
from pathlib import Path
from matplotlib.lines import Line2D


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

        min_season = min(self.df["season"].unique())
        max_season = max(self.df["season"].unique())
        self.PLT_HEADER = f"MVKC\nSeaons {min_season}-{max_season}\n"

    def plot_proj(self):

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

        # Add a horizontal line at 0
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.tight_layout()

        plt.savefig(self.PLOTS_DIR / "projected_pts_diff_bar.png")

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
                if manager == opponent:
                    # Skip self-matchups
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
                    # Else no matches, use NaN for plotting
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

        # Manually add annotations with bolded record
        for i, row in enumerate(annot_data_pivoted.index):
            for j, col in enumerate(annot_data_pivoted.columns):
                annotation = annot_data_pivoted.loc[row, col]
                if annotation:
                    record, delta = annotation.split('\n')
                    # Add the bold record on top
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
                    # Add the regular delta on the bottom
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

    def plot_weekly_scatter(self):

        df = self.df

        # Calculate the point differential for each matchup
        df['point_differential'] = df['points'] - df['opp_points']

        # Identify all unique managers
        managers = df['manager'].unique()

        # Determine the symmetrical y-axis limits based on the maximum
        # absolute point differential
        max_diff = df['point_differential'].abs().max()
        y_limit = max_diff * 1.1

        # Create a separate scatter plot for each manager
        for manager in managers:
            # Filter the DataFrame for the current manager
            manager_df = df[df['manager'] == manager]

            # Create the scatter plot
            plt.figure(figsize=(10, 7))
            sns.scatterplot(
                x='points',
                y='point_differential',
                data=manager_df,
                s=150,  # Size of the markers
                edgecolor='black',
                hue='opponent',  # Color points based on the opponent
                style='opponent',  # Set marker style based on the opponent
            )

            # Add a horizontal line at y=0 for visual reference
            plt.axhline(0, color='gray', linestyle='--')
            plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)
            plt.title(f'Weekly Matchup Performance for {manager}', fontsize=16)
            plt.xlabel('Manager Points Scored', fontsize=12)
            plt.ylabel(
                'Point Differential (Manager Points - Opponent Points)',
                fontsize=12
                )

            # Set the y-axis to be symmetrical
            plt.ylim(-y_limit, y_limit)

            # Add a legend
            plt.legend(
                title='Opponent',
                bbox_to_anchor=(1.05, 1),
                loc='upper left'
                )

            plt.grid(True, which='both', linestyle='--', linewidth=0.5)
            plt.tight_layout()

            # Save the figure with a descriptive filename
            manager_str = f'{manager.lower().replace(" ", "_")}'
            plt.savefig(self.PLOTS_DIR / f'{manager_str}_matchup_scatter.png')
            plt.close()

    def plot_points_against(self):

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

    def plot_winnings(self):

        # with open('league_dues.json', 'r') as f:
        #     league_dues = json.load(f)

        df = self.df_standings

        num_teams = len(df['manager'].unique())

        # Define the prize money for each place
        # (in terms of dues proportion)
        # { "rank" : "prize"}
        # Non placers lose money
        PRIZES = dict.fromkeys(list(range(1, num_teams+1)), -1)
        PRIZES[1] = 9
        PRIZES[2] = 1
        PRIZES[3] = 0

        # total_winnings = dict.fromkeys(
        #     manager_nicknames,
        #     -sum(league_dues.values())
        #     )

        # for season in df["season"].unique():
        #     for manager in manager_nicknames:
        #         total_winnings[manager] -= league_dues[f"{season}"]

        # Create a 'winnings' column by mapping the 'rank' column
        # Use the .map() method, which is ideal for this kind of lookup.
        # Any rank not in the `prizes` dictionary will result in a NaN value.
        df['winnings'] = df['rank'].map(PRIZES)

        # # Fill any NaN values with 0, in case some ranks don't get a prize
        # df['winnings'] = df['winnings'].fillna(0)

        # df['winnings'] = df['winnings'] - 1

        total_winnings_per_manager = (
            df.groupby('manager')['winnings']
            .sum().
            reset_index()
        )

        # Rename columns for clarity
        total_winnings_per_manager.columns = ['manager', 'total_winnings']

        # Sort the DataFrame by total winnings in descending order
        total_winnings_per_manager = total_winnings_per_manager.sort_values(
            by='total_winnings',
            ascending=False
            )

        # Create the bar chart
        plt.figure(figsize=(10, 7))
        ax = sns.barplot(
            x='manager',
            y='total_winnings',
            data=total_winnings_per_manager,
            palette='viridis',
            hue='manager',
            legend=False,
            order=total_winnings_per_manager['manager']
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
                total_winnings_per_manager.iloc[i]['total_winnings']
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

    def plot_manager_perf(self):

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
            # expand_points=(1.2, 1.4),
            # expand_text=(5.05, 5.2),
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

        # Get the handles and labels for the scatter plot legend
        handles, labels = ax.get_legend_handles_labels()

        # Create a new handle for the regression line
        line_handle = Line2D([0], [0], color='gray', linestyle='--', alpha=0.7)

        # Add the new handle and its label to the lists
        handles.append(line_handle)
        labels.append('Linear Trend Line')

        # Create the final legend with all entries
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

    def plot_luck_factor(self):

        df = self.df

        # Calculate the 'delta' column (actual points - projected points)
        df['delta'] = df['points'] - df['proj_points']

        # Calculate overall statistics for the entire dataset
        overall_avg_delta = df['delta'].mean()
        overall_std_dev = df['delta'].std()

        print("Overall Statistics (All Managers & Seasons):")
        print(f"  Average Projection: {df['proj_points'].mean():.2f}")
        print(f"  Average Score: {df['points'].mean():.2f}")
        print(f"  Average Delta: {overall_avg_delta:.2f}")
        print(f"  Standard Deviation: {overall_std_dev:.2f}")
        print("\n" + "-"*50 + "\n")

        # Calculate statistics per manager
        manager_stats = (
            df.groupby('manager')['delta']
            .agg(['mean', 'std'])
            .rename(
                columns={'mean': 'Average Delta',
                         'std': 'Standard Deviation',
                         }
                    )
        )

        print("Statistics per Manager:")
        print(manager_stats.to_string(float_format="%.2f"))
        print("\n" + "="*50 + "\n")

        # --------------------
        # Lucky Wins Analysis
        # --------------------

        # Calculate point differentials
        df['actual_point_diff'] = df['points'] - df['opp_points']
        df['proj_point_diff'] = df['proj_points'] - df['opp_proj_points']

        # Calculate the standard deviation of the actual point differential
        # across all matchups
        std_dev_point_diff = df['actual_point_diff'].std()

        # Define the criteria for a "lucky win"
        # 1. Projected point differential is a significant loss (more than one
        # std dev below zero)
        # 2. Actual point differential is a significant win (more than one std
        # dev above zero)
        # df['lucky_win'] = np.where(
        #     (df['proj_point_diff'] < -std_dev_point_diff) &
        #     (df['actual_point_diff'] > std_dev_point_diff),
        #     1, 0
        # )

        df['lucky_win'] = np.where(
            (
                (df['actual_point_diff'] - df['proj_point_diff'] >
                 std_dev_point_diff) &
                (df['proj_point_diff'] < 0)
            ),
            1, 0
        )

        df['lucky_loss'] = np.where(
            (
                (df['proj_point_diff'] - df['actual_point_diff'] >
                 std_dev_point_diff) &
                (df['proj_point_diff'] > 0)
            ),
            1, 0
        )

        # Count the total lucky wins for each manager
        lucky_wins_count = (
            df.groupby('manager')['lucky_win'].sum().reset_index()
        )

        # Count the total lucky wins for each manager
        lucky_losses_count = (
            df.groupby('manager')['lucky_loss'].sum().reset_index()
        )

        # Create the bar plot for lucky wins
        plt.figure(figsize=(10, 7))
        ax = sns.barplot(
            x='manager',
            y='lucky_win',
            hue='manager',
            data=lucky_wins_count,
            palette='viridis',
            legend=False,
        )

        # Set the y-axis limit dynamically
        max_lucky_wins = lucky_wins_count['lucky_win'].max()
        plt.ylim(0, max_lucky_wins + 3)

        # Add annotations to the bars
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom',
                            xytext=(0, 5),
                            textcoords='offset points',
                            fontsize=12)

        plt.grid(True, axis='y')
        ax.set_axisbelow(True)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)

        plt.title('Total Lucky Wins per Manager', fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of Lucky Wins', fontsize=12)
        plt.tight_layout()

        plt.savefig(self.PLOTS_DIR / 'lucky_wins_bar_plot.png')

        # Create the bar plot for lucky losses
        plt.figure(figsize=(10, 7))
        ax = sns.barplot(
            x='manager',
            y='lucky_loss',
            hue='manager',
            data=lucky_losses_count,
            palette='viridis',
            legend=False,
        )

        # Set the y-axis limit dynamically
        max_lucky_losses = lucky_losses_count['lucky_loss'].max()
        plt.ylim(0, max_lucky_losses + 3)

        # Add annotations to the bars
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom',
                            xytext=(0, 5),
                            textcoords='offset points',
                            fontsize=12)

        plt.grid(True, axis='y')
        ax.set_axisbelow(True)
        plt.suptitle(self.PLT_HEADER, fontsize=16, weight="heavy", y=0.95)

        plt.title('Total Unlucky Losses per Manager', fontsize=16)
        plt.xlabel('Manager', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of Unlucky Losses', fontsize=12)
        plt.tight_layout()

        plt.savefig(self.PLOTS_DIR / 'unlucky_losses_bar_plot.png')

    def plot_upsets(self):

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

    def plot_all(self):
        """Discovers and calls all plotting methods in the class.
        """
        print("--- Calling all plots ---")
        # Use inspect.getmembers to find all methods of the class
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, method in members:
            # Check if the method name starts with 'plot_'
            # and is not the plot_all method itself
            if name.startswith('plot_') and name != "plot_all":
                print(f"Calling: {name}")
                method()
        print("--- All plots generated ---")


if __name__ == "__main__":

    p = Plotting()
    p.plot_all()
