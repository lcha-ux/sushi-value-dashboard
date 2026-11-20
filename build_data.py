"""Build compact, submission-safe data extracts from the raw sushi sales CSVs.

The raw order_items.csv is ~50 MB, which is too large for the GitHub/Render
workflow (the course guide asks for <20 MB). Everything the dashboard needs is
pre-aggregated here into a few small CSVs, so the app stays fast on Render's
free tier and the submitted zip stays tiny.

Run:  python build_data.py
Input: ../sushi restaurant sales/*.csv   (the six files supplied by the group)
Output: data/*.csv
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT.parent / "sushi restaurant sales"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

PIECES = {
    "Sashimi Platter (10pc)": 10,
    "Omakase Set (15pc)": 15,
    "Tuna Nigiri (2pc)": 2,
    "Yellowtail Nigiri (2pc)": 2,
    "Salmon Nigiri (2pc)": 2,
    "Gyoza (6pc)": 6,
    "Mochi (3pc)": 3,
}
DOW_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main() -> None:
    orders = pd.read_csv(
        RAW / "sushi_orders.csv",
        usecols=[
            "order_id", "date", "year", "month", "quarter", "day_of_week",
            "is_weekend", "is_holiday", "customer_segment", "channel",
            "party_size", "revenue", "cogs", "gross_profit", "rating",
            "tip", "delivery_fee", "total_collected",
        ],
    )
    items = pd.read_csv(
        RAW / "sushi_order_items.csv",
        usecols=["order_id", "date", "item", "category", "unit_price", "cogs"],
    )
    items["year"] = pd.to_datetime(items["date"]).dt.year

    # Join the item lines to their order so item charts can respond to the
    # channel / time filters (the raw item file has no channel column).
    item_join = items.merge(
        orders[["order_id", "channel", "day_of_week", "customer_segment", "is_weekend"]],
        on="order_id", how="left", validate="many_to_one",
    )
    assert item_join["channel"].notna().all(), "orphan item rows: no matching order"

    # --- menu_items.csv -----------------------------------------------------
    menu = (
        items.groupby(["item", "category"])
        .agg(
            units=("item", "size"),
            median_price=("unit_price", "median"),
            median_cogs=("cogs", "median"),
            min_price=("unit_price", "min"),
            max_price=("unit_price", "max"),
        )
        .reset_index()
    )
    menu["price"] = (menu["median_price"] * 2).round() / 2  # clean menu price
    menu["value_share"] = (menu["median_cogs"] / menu["median_price"]).round(4)
    menu["pieces"] = menu["item"].map(PIECES)
    menu["popularity_rank"] = menu["units"].rank(ascending=False, method="min").astype(int)
    menu = menu.sort_values("value_share", ascending=False)
    menu.to_csv(OUT / "menu_items.csv", index=False)

    # --- item_facts.csv -----------------------------------------------------
    item_facts = (
        item_join.groupby(["item", "category", "year", "channel"])
        .agg(
            units=("item", "size"),
            revenue=("unit_price", "sum"),
            cogs=("cogs", "sum"),
            avg_price=("unit_price", "mean"),
        )
        .reset_index()
    )
    item_facts["value_share"] = (item_facts["cogs"] / item_facts["revenue"]).round(4)
    item_facts.to_csv(OUT / "item_facts.csv", index=False)

    # --- visit_facts.csv ----------------------------------------------------
    visit = (
        orders.groupby(["year", "month", "day_of_week", "channel"])
        .agg(
            orders=("order_id", "size"),
            revenue=("revenue", "sum"),
            party_sum=("party_size", "sum"),
            rating_sum=("rating", "sum"),
            rating_n=("rating", "count"),
            tip_sum=("tip", "sum"),
            total_collected=("total_collected", "sum"),
        )
        .reset_index()
    )
    visit["is_weekend"] = visit["day_of_week"].isin(["Sat", "Sun"])
    visit.to_csv(OUT / "visit_facts.csv", index=False)

    # --- party_facts.csv ----------------------------------------------------
    party = (
        orders.groupby(["year", "channel", "party_size"])
        .agg(orders=("order_id", "size"), revenue=("revenue", "sum"),
             party_sum=("party_size", "sum"))
        .reset_index()
    )
    party.to_csv(OUT / "party_facts.csv", index=False)

    # --- annual_channel.csv -------------------------------------------------
    annual = (
        orders.groupby(["year", "channel"])
        .agg(
            orders=("order_id", "size"),
            revenue=("revenue", "sum"),
            party_sum=("party_size", "sum"),
            rating_sum=("rating", "sum"),
            rating_n=("rating", "count"),
        )
        .reset_index()
    )
    annual["per_person"] = (annual["revenue"] / annual["party_sum"]).round(2)
    annual["avg_rating"] = (annual["rating_sum"] / annual["rating_n"]).round(3)
    annual.to_csv(OUT / "annual_channel.csv", index=False)

    print(
        "Wrote:",
        ", ".join(f"{p.name} ({p.stat().st_size / 1024:.0f} KB)" for p in sorted(OUT.glob("*.csv"))),
    )
    print(f"Raw orders: {len(orders):,} | raw item lines: {len(items):,} | years: {orders.year.min()}-{orders.year.max()}")


if __name__ == "__main__":
    main()
