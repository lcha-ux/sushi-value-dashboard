# Analysis notes — The AYCE Playbook

These are the working notes behind the dashboard. They are useful if a judge asks *"how did you
get that number?"* during the showcase. Every figure below was computed directly from the
group-supplied CSVs by `build_data.py`.

## Data used

| Source | Rows | What we took from it |
|--------|------|----------------------|
| `sushi_orders.csv` | 83,890 | order date/year/channel/party size/revenue/cogs/rating/tip |
| `sushi_order_items.csv` | 998,920 | item name, category, unit price, ingredient cost per item line |
| `sushi_customers.csv` | 1,800 | not needed for the dashboard's question |
| `sushi_reviews.csv` | 15,146 | used indirectly: rating is present on the order file |
| `sushi_daily_pnl.csv` | 3,653 | cross-check of totals |
| `sushi_staff.csv` | 11 | not needed for the dashboard's question |

Coverage: **2015-01-01 → 2024-12-31** (3,653 days), **83,890 orders**, **20 menu items**, three
channels (dine in, takeaway, delivery). Total revenue **$9,249,665.50**.

## The metric, and why it is defensible

**Ingredient share = ingredient cost ÷ menu price.** On the item file this is `cogs / unit_price`.
It answers a real question — *what fraction of the price is the actual food?* — using a field the
dataset really contains, so no numbers are invented.

A few deliberate choices make it honest rather than sensational:

- We use the **median** cost and price per item, so a handful of promotional prices cannot swing a
  ranking.
- We say "ingredient share", never "quality" or "value for money" in absolute terms. A 43% share
  means more of the price is food cost; it does not mean the dish tastes better.
- We never claim the app analyses **all-you-can-eat pricing** — the dataset has no AYCE field.
  The takeaway is framed as "what to prioritise at a fixed-price sushi deal".

## Findings, with the numbers

1. **Six-fold value spread.** Sashimi Platter 43%, Omakase Set 42%, Tuna Nigiri 41%, Yellowtail
   Nigiri 39%, Salmon Nigiri 38% at the top. Green Tea 7%, Miso Soup 11%, Edamame 14% at the
   bottom. The ratio between the top and bottom item is about **6×**.

2. **Popularity and value pull in different directions.** By portions sold the leaders are
   California Roll (136,367; 28% share), Spicy Tuna Roll (108,172; 32%), Salmon Nigiri (104,982;
   38%), Tuna Nigiri (86,620; 41%). Three of the four best-sellers are mid-to-high value — but the
   5th, 6th and 7th best-sellers (Edamame 14%, Miso Soup 11%, Green Tea 7%) are the cheapest
   fillers. That contrast is the story the first tab tells.

3. **Real price growth.** Revenue per person by year: 2015 $30.12, 2016 $31.58, 2017 $33.72, 2018
   $34.92, 2019 $39.19, 2020 $43.75, 2021 $46.27, 2022 $43.83, 2023 $45.26, 2024 $46.48 — a
   **54% rise**. Average party size is **2.73** and barely moves year to year, so the increase is
   not an artefact of bigger groups. All-years average: **$40.37 per person**.

4. **Guest ratings.** Overall average **3.65** across 15,146 rated orders. Yearly average rises
   from **3.31 (2015)** to **3.92 (2024)** with a clear **2020 dip to 3.35**. By channel:
   takeaway **3.72**, dine in **3.66**, delivery **3.51**. This is what the animated scatter plots
   against spend per person.

5. **No timing effect worth claiming.** Weekend spend per person **$40.33** vs weekday **$40.39**;
   the heatmap shows mild seasonal variation but no robust "best day/month to go". The dashboard
   presents the heatmap as descriptive only and makes no recommendation from it.

6. **The optimiser.** A small dynamic program picks up to six different items under a per-person
   budget, maximising ingredient dollars (or piece count for the "portions" goal). At **$50** it
   selects Sashimi Platter + Yellowtail Nigiri + Rainbow Roll for **~40%** ingredient share, against
   **~31%** for a typical most-ordered four-item basket — **~9 points** more of the budget in food.
   At **$33**, ~42% vs ~29%. The up-to-six-different-items constraint deliberately stops it
   recommending an unrealistic plate made of one item repeated.

## The Fuel & Spend tab (macro tracker)

This tab is an **interactive tool**, not a new finding from the sales data. It reuses the
`menu_items.csv` price and ingredient-cost figures to compare *what you paid* with *what the
kitchen spent on ingredients* for a plate you build yourself, then recommends the next portion
that closes the largest share of your remaining calorie/protein/carb gaps within a spend cap. It
also surfaces the "should I order a drink?" question: drinks have among the lowest ingredient
shares (Sapporo 30%, Sake 27%, Whisky 22%) and add calories but no protein, so the recommendation
is to put the budget on nigiri if the goal is maximum food per dollar.

**Important provenance:** the sales dataset has **no nutrition columns**. The calories/protein/
carbs/fat per portion in `data/nutrition_estimates.csv` are illustrative estimates for a standard
portion, added by us for the interactive feature, editable in that file, and labelled as estimates
in the app and the brief. They are not measured, not sourced from the dataset, and not medical
advice. Only the price, ingredient-cost and ingredient-share numbers on this tab are data-derived.

## Limitations to volunteer if asked

- Cost ratio is not a measure of quality, freshness, portion size or nutrition.
- Nutrition estimates in the Fuel & Spend tab are illustrative, not measured or medically
  advised; only its cost figures come from the dataset.
- This is one restaurant group's data, not the whole market; results describe this menu.
- The 2020 dip coincides with the pandemic — the data shows the dip, it does not explain it.
- Ratings exist for a subset of orders (15,146 of 83,890), so rating cuts use fewer rows.
- The "typical order" in the plate builder is defined as the four most-ordered items, doubled
  where budget allows; it is a simple comparison baseline, not a claim about any real basket.

## Reproducing

```bash
python build_data.py      # rebuild data/*.csv from ../sushi restaurant sales/*.csv
python app.py             # open http://127.0.0.1:8050
```
