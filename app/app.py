from flask import Flask, render_template
import pandas as pd
import os
import glob

app = Flask(__name__)


def get_latest_csv():
    list_of_files = glob.glob("data/*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def load_data():
    csv_file = get_latest_csv()
    df = pd.read_csv(csv_file, thousands=".", decimal=",")

    if df["Anzahl"].dtype == "object":
        df["Anzahl"] = pd.to_numeric(
            df["Anzahl"].str.replace(",", "."), errors="coerce"
        )

    df["Kaufpreis"] = pd.to_numeric(df["Kaufpreis"], errors="coerce")
    df["Aktueller Wert"] = pd.to_numeric(df["Aktueller Wert"], errors="coerce")

    return df


def calculate_portfolio_summary(df):
    total_value = df["Aktueller Wert"].sum()
    total_purchase_value = (df["Kaufpreis"] * df["Anzahl"]).sum()
    performance = (
        ((total_value - total_purchase_value) / total_purchase_value) * 100
        if total_purchase_value != 0
        else 0
    )
    return total_value, total_purchase_value, performance


def get_top_holdings(df):
    df_sorted = df.sort_values("Aktueller Wert", ascending=False).head(5)
    df_sorted["Percentage"] = (
        df_sorted["Aktueller Wert"] / df["Aktueller Wert"].sum() * 100
    )
    return df_sorted[["Name", "Wertpapiertyp", "Aktueller Wert", "Percentage"]].to_dict(
        "records"
    )


def get_asset_allocation(df):
    asset_allocation = df.groupby("Wertpapiertyp")["Aktueller Wert"].sum()
    total = asset_allocation.sum()
    return {k: v / total * 100 for k, v in asset_allocation.items()}


def get_geographical_distribution(df):
    geo_dist = df.groupby("Region")["Aktueller Wert"].sum()
    total = geo_dist.sum()
    return {k: v / total * 100 for k, v in geo_dist.items()}


def get_sector_distribution(df):
    sector_dist = df.groupby("Sektor")["Aktueller Wert"].sum()
    total = sector_dist.sum()
    return {k: v / total * 100 for k, v in sector_dist.items()}


@app.route("/")
def index():
    df = load_data()
    total_value, total_purchase_value, performance = calculate_portfolio_summary(df)
    top_holdings = get_top_holdings(df)
    asset_allocation = get_asset_allocation(df)
    geographical_distribution = get_geographical_distribution(df)
    sector_distribution = get_sector_distribution(df)

    return render_template(
        "index.html",
        total_value=total_value,
        total_purchase_value=total_purchase_value,
        performance=performance,
        top_holdings=top_holdings,
        asset_allocation=asset_allocation,
        geographical_distribution=geographical_distribution,
        sector_distribution=sector_distribution,
    )


if __name__ == "__main__":
    app.run(debug=True)
