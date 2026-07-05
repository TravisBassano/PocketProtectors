# Statistical League History

## Overview

This README provides an overview of the statistical league history, focusing on data ingestion, analytics and math, and data visualization.

## Data Ingestion

The system expects raw inputs from various sources. The data is structured in a way that allows for efficient analysis and reporting.

### Raw Inputs
- **Seasons Data**: Contains detailed statistics for each season.
- **Playoff Data**: Tracks performance during the playoffs.
- **Overall Data**: Aggregates wins, losses, points scored (PF), and points against (PA) across seasons.

## Analytics & Math

The system aggregates historical trends and tracks scoring metrics across seasons. Key calculations include:

- **Win Percentage**: Total wins divided by total games played.
- **Points Scored (PF)**: Sum of all points scored in each season.
- **Points Against (PA)**: Sum of all points against in each season.

### Mathematical Formulas

1. **Win Percentage**:
   \[
   Win\ Percentage = \frac{Total\ Wins}{Total\ Games\ Played}
   \]

2. **Points Scored (PF)**:
   \[
   PF = \sum_{i=1}^{n} PF_i
   \]
   Where \( n \) is the number of seasons.

3. **Points Against (PA)**:
   \[
   PA = \sum_{i=1}^{n} PA_i
   \]

## Data Visualization

The system generates visual representations of the data to help understand trends and performance. Key charts include:

### Bar Charts

1. **Trade Count by Manager**: Displays the number of trades made by each manager across all seasons.
2. **Trade Network**: Shows a network graph representing trades between managers.

### Line Graphs

1. **Fantasy Manager Playoff Stats**: Plots playoff statistics for each manager over the years, including playoff appearances, playoffs byes, championship appearances, and championships.

These visualizations are designed to provide insights into the league's performance and help track individual managers' success.