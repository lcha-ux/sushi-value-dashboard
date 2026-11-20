# ONE-PAGE PROJECT BRIEF — The AYCE Playbook

> Only the **Render URL** and **GitHub URL** still need filling in, plus a quick check of the
> **AI use note**. Everything else is ready.

**Title:** The AYCE Playbook — What your sushi dollar actually buys

**Team:** Luke Cha, Emily Chue, Fiona Zhu, Albina Martynenko

**Audience:** Fellow students and anyone who eats sushi, especially people choosing what to order
at a fixed-price / all-you-can-eat sushi deal who want to feel they got their money's worth.

**Main question:** *Where does your sushi dollar actually go — and what should you order first?*

**Dataset links / source:** [Sushi Restaurant Sales Simulation — 10 Years (Kaggle)](https://www.kaggle.com/datasets/troykueh/sushi-restaurant-sales-simulation-10-years).
Six CSV files (`sushi_orders.csv`, `sushi_order_items.csv`, `sushi_daily_pnl.csv`,
`sushi_customers.csv`, `sushi_reviews.csv`, `sushi_staff.csv`) — 83,890 orders and ~998,920
item lines covering **2015-01-01 to 2024-12-31**.

**Render URL:** [https://__________.onrender.com]

**GitHub URL:** [https://github.com/__________/__________]

**AI use note:** *[Draft — confirm with your instructor.]* An AI coding assistant was used to
explore the dataset, build the Dash application and its visual design, and draft this written
material. The team reviewed every figure against the source data, chose the framing and the
"ingredient share" proxy, corrected the claims, and made the final decisions about what to
include. No application was submitted and no data was collected by the AI outside the files
supplied for the project.

---

## Key findings

1. **Value varies six-fold across the menu.** ingredients account for **43%** of the price of a
   Sashimi Platter but only **7%** of Green Tea. Omakase (42%), Tuna Nigiri (41%) and Yellowtail
   Nigiri (39%) lead; Miso Soup (11%) and Edamame (14%) sit at the bottom.

2. **The most popular items are not the best value.** The top four orders are California Roll
   (136,367 portions, 28% ingredient share), Spicy Tuna Roll (108,172, 32%), Salmon Nigiri
   (104,982, 38%) and Tuna Nigiri (86,620, 41%) — but Miso Soup (#6, 11%) and Green Tea (#7, 7%)
   are also among the most-ordered items. Popularity and value are different things.

3. **The bill is rising, and it is not because groups got bigger.** Spend per person climbed from
   **$30.12 in 2015 to $46.48 in 2024 (+54%)**, while average party size stayed almost flat at
   **2.73 people**.

4. **Guests rated the experience more highly over time.** Average rating improved from **3.31**
   in 2015 to **3.92** in 2024, with a visible dip to **3.35 in 2020**. Takeaway rated highest
   (3.72), delivery lowest (3.51).

5. **There is no "cheap day to go" in this data.** Weekend spend per person ($40.33) is the same
   as weekday ($40.39). The app deliberately does not claim otherwise.

6. **The finding is actionable.** At a **$50 per-person** budget, the plate optimiser reaches
   **~40% ingredient share** versus **~31%** for a typical four-item order — about **9 percentage
   points more food for the same money** (e.g. Sashimi Platter + Yellowtail Nigiri + Rainbow Roll).

---

## What the dashboard lets you do

Three tabs, all driven by one shared **year range** and **order channel** filter:

- **Value Playbook** — rank all 20 menu items by ingredient share, explore the menu as a treemap,
  and click any bar or tile to see that item's price and value history.
- **The Bill** — a day × month heatmap of spend per person, a party-size chart, and an animated
  10-year scatter of spend per person against guest rating.
- **Build Your Plate** — set a per-person budget and let a small optimiser build the highest-value
  combination of up to six different items, compared with a typical order.
- **Fuel & Spend** — add the quantities you ate, set calorie / protein / carb / dollar targets, and
  the app tracks progress, recommends the portions that best close the remaining gaps within your
  budget, and answers the "should I order a drink?" question using the item cost data.

**Method in one line:** *ingredient share = median ingredient cost ÷ median menu price*, computed
from the item-level sales file; it is a transparent cost proxy, not a claim about taste or quality.
**Nutrition note:** the sales dataset contains no nutrition fields. The macro values in the
Fuel & Spend tab are clearly labelled illustrative estimates for a standard portion (editable in
`data/nutrition_estimates.csv`), not measured data and not medical advice.
