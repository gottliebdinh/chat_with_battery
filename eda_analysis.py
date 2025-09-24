"""
EDA script for chat_with_battery dataset.

This script loads data from data/data.json and generates:
- Correlation heatmap (numeric features)
- Distributions (histogram + KDE) per numeric column
- Optional time-series overview (if 'timestamp' exists)
- Seasonality heatmaps (Hour × Month) for selected metrics
- Energy flow stacked area (if flow columns present)
- Economics plots for savings and feed-in revenue (if present)
- Heavy load occurrence by hour-of-day (if present)

Outputs are saved under eda_output/.
"""

import os
import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def load_dataframe(json_path: Path) -> pd.DataFrame:
    with open(json_path, "r") as file_handle:
        data_records = json.load(file_handle)
    dataframe = pd.DataFrame(data_records)
    # Parse timestamp if present
    if "timestamp" in dataframe.columns:
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")
        dataframe = dataframe.sort_values("timestamp")
        dataframe = dataframe.set_index("timestamp")
    return dataframe


def save_fig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_correlation_heatmap(numeric_df: pd.DataFrame, output_dir: Path) -> None:
    if numeric_df.shape[1] == 0:
        return
    correlation = numeric_df.corr()
    num_features = correlation.shape[0]
    figsize = (min(1 + 0.5 * num_features, 16), min(1 + 0.5 * num_features, 16))
    plt.figure(figsize=figsize)
    sns.heatmap(correlation, cmap="coolwarm", center=0, vmin=-1, vmax=1, square=True)
    plt.title("Feature Correlations (Pearson)")
    save_fig(output_dir / "correlation_heatmap.png")


def plot_distributions(numeric_df: pd.DataFrame, output_dir: Path) -> None:
    for column_name in numeric_df.columns:
        plt.figure(figsize=(6, 4))
        sns.histplot(numeric_df[column_name].dropna(), kde=True, bins=40)
        plt.title(f"Distribution: {column_name}")
        plt.xlabel(column_name)
        plt.ylabel("Count")
        save_fig(output_dir / f"dist_{column_name}.png")


def select_top_numeric_columns(numeric_df: pd.DataFrame, max_columns: int = 6) -> List[str]:
    if numeric_df.empty:
        return []
    variances = numeric_df.var().sort_values(ascending=False)
    return list(variances.head(max_columns).index)


def plot_pairplot(numeric_df: pd.DataFrame, output_dir: Path, max_columns: int = 6) -> None:
    selected_columns = select_top_numeric_columns(numeric_df, max_columns=max_columns)
    if len(selected_columns) < 2:
        return
    sampled = numeric_df[selected_columns]
    if len(sampled) > 2000:
        sampled = sampled.sample(2000, random_state=0)
    sns.pairplot(sampled, corner=True, diag_kind="hist")
    plt.suptitle("Pairplot (Top-Variance Numeric Features)", y=1.02)
    save_fig(output_dir / "pairplot_top_features.png")


def plot_time_series_overview(df: pd.DataFrame, output_dir: Path) -> None:
    if not isinstance(df.index, pd.DatetimeIndex):
        return
    candidate_columns = [
        "net_load",
        "gross_load",
        "pv_profile",
        "f_opt",
        "SOC_opt",
    ]
    trend_columns = [col for col in candidate_columns if col in df.columns]
    if not trend_columns:
        return
    plt.figure(figsize=(14, 5))
    df[trend_columns].plot(ax=plt.gca(), alpha=0.8)
    plt.title("Time Series Overview (Hourly)")
    plt.xlabel("Time")
    plt.ylabel("Value")
    save_fig(output_dir / "timeseries_overview.png")

    daily_mean = df[trend_columns].resample("D").mean()
    plt.figure(figsize=(14, 4))
    daily_mean.plot(ax=plt.gca(), alpha=0.9)
    plt.title("Time Series (Daily Mean)")
    plt.xlabel("Date")
    plt.ylabel("Mean Value")
    save_fig(output_dir / "timeseries_daily_mean.png")


def plot_seasonality_heatmaps(df: pd.DataFrame, output_dir: Path) -> None:
    if not isinstance(df.index, pd.DatetimeIndex):
        return
    metrics = [m for m in ["net_load", "gross_load", "pv_profile"] if m in df.columns]
    if not metrics:
        return
    df = df.copy()
    df["_hour"] = df.index.hour
    df["_month"] = df.index.month
    for metric in metrics:
        pivot = df.pivot_table(index="_hour", columns="_month", values=metric, aggfunc="mean")
        plt.figure(figsize=(10, 5))
        sns.heatmap(pivot, cmap="mako", cbar=True)
        plt.title(f"{metric}: Mean by Hour × Month")
        plt.xlabel("Month")
        plt.ylabel("Hour")
        save_fig(output_dir / f"seasonality_{metric}.png")


def plot_energy_flow(df: pd.DataFrame, output_dir: Path) -> None:
    flow_columns = [c for c in ["s_l_pv_opt", "s_l_grid_opt", "s_e_opt"] if c in df.columns]
    if not flow_columns:
        return
    subset = df[flow_columns].copy()
    if not subset.empty and isinstance(subset.index, pd.DatetimeIndex):
        subset = subset.iloc[: 24 * 7]  # first week for readability
    plt.figure(figsize=(14, 5))
    subset.plot.area(ax=plt.gca(), alpha=0.85)
    plt.title("Energy Supply to Load (First Week)")
    plt.ylabel("Power / Energy (units)")
    save_fig(output_dir / "energy_flow_stacked_area.png")


def plot_economics(df: pd.DataFrame, output_dir: Path) -> None:
    econ_columns = [c for c in ["electricity_savings_step", "feed_in_revenue_delta_step"] if c in df.columns]
    if not econ_columns:
        return
    cumulative = df[econ_columns].cumsum()
    plt.figure(figsize=(12, 4))
    cumulative.plot(ax=plt.gca())
    plt.title("Cumulative Savings and Feed-in Revenue")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Value")
    save_fig(output_dir / "economics_cumulative.png")

    melted = df[econ_columns].melt(var_name="metric", value_name="value")
    g = sns.displot(melted, x="value", col="metric", col_wrap=2, kde=True, height=3, facet_kws={"sharex": False})
    g.set_titles("{col_name} per-step")
    # seaborn's FacetGrid uses its own savefig
    g.fig.tight_layout()
    g.savefig(output_dir / "economics_distributions.png", dpi=150)
    plt.close("all")


def plot_heavy_load_rate(df: pd.DataFrame, output_dir: Path) -> None:
    if "heavy_load" not in df.columns or not isinstance(df.index, pd.DatetimeIndex):
        return
    hourly_rate_percent = df.groupby(df.index.hour)["heavy_load"].mean() * 100.0
    plt.figure(figsize=(10, 4))
    hourly_rate_percent.plot(kind="bar")
    plt.title("Heavy Load Rate by Hour (%)")
    plt.xlabel("Hour of Day")
    plt.ylabel("Percentage (%)")
    save_fig(output_dir / "heavy_load_rate_by_hour.png")


def run_eda(json_path: Path, output_dir: Path) -> None:
    sns.set_context("talk")
    sns.set_style("whitegrid")

    ensure_output_dir(output_dir)
    df = load_dataframe(json_path)
    numeric_df = df.select_dtypes(include=[np.number])

    # Core EDA
    plot_correlation_heatmap(numeric_df, output_dir)
    plot_distributions(numeric_df, output_dir)
    plot_pairplot(numeric_df, output_dir, max_columns=6)

    # Optional time-based and domain plots
    plot_time_series_overview(df, output_dir)
    plot_seasonality_heatmaps(df, output_dir)
    plot_energy_flow(df, output_dir)
    plot_economics(df, output_dir)
    plot_heavy_load_rate(df, output_dir)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    default_json = project_root / "data" / "data.json"
    default_output = project_root / "eda_output"
    run_eda(default_json, default_output)


