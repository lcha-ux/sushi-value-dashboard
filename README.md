# The AYCE Playbook — Dash dashboard

**Question:** *Where does your sushi dollar actually go — and what should you order first?*

A competition-ready Python Dash app built on ten years of real restaurant sales data. It ranks
every menu item by **ingredient share** (restaurant ingredient cost ÷ menu price) — an honest,
transparent proxy for "how much of your sushi dollar ends up in the food" — and turns that
finding into an interactive plate builder plus a "Fuel & Spend" macro tracker that recommends
your next order inside a dollar cap.

---

## 1. Run it locally

```bash
# Python 3.12 (see runtime.txt)
python -m pip install -r requirements.txt
python build_data.py     # only needed if you re-generate data/ from the raw CSVs
python app.py
```

Open <http://127.0.0.1:8050>. You should see the hero, four KPI cards, and four tabs.

> You do **not** need to run `build_data.py` to see the app — the aggregated CSVs are already in
> `data/`. It is included so the whole project is reproducible from the raw files.

### Make the art again (optional)

`assets/hero.png` and `assets/plate.png` are already included. To regenerate them:

```bash
python make_art.py
```

---

## 2. Deploy on Render (free tier)

1. Push this folder to a GitHub repository (all files at the repo root — `app.py`,
   `requirements.txt`, `data/`, `assets/`).
2. On Render → **New → Web Service** → connect that repo.
3. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server`
   - **Instance Type:** Free
4. Create the service. Render serves the app on the assigned `onrender.com` URL.
5. Paste that URL into `project_brief.md` / `project_brief.html` under **Render URL**.

`app.py` already contains the required `server = app.server` line. No other Render-specific
code is needed. The full dataset shipped to Render is ~200 KB, so the free tier is plenty.

> Free instances spin down when idle; the first click after a while may take ~30–60 seconds.
> Mention this in the showcase rather than treating it as a bug.

---

## 3. What is in each file

| File | Purpose |
|------|---------|
| `app.py` | The entire Dash app: layout, figures, callbacks, and the plate optimiser. |
| `assets/styles.css` | All custom styling (dark editorial theme, responsive grid). |
| `assets/hero.png`, `assets/plate.png` | Original sushi illustrations, generated locally by `make_art.py`. |
| `data/menu_items.csv` | One row per menu item: median price, median cost, ingredient share, pieces, popularity. |
| `data/item_facts.csv` | Item × year × channel sales, used by the value charts and click-to-inspect line chart. |
| `data/visit_facts.csv` | Year × month × weekday × channel order facts, used by the heatmap and KPI cards. |
| `data/party_facts.csv` | Year × channel × party size, used by the party-size bar chart. |
| `data/annual_channel.csv` | Year × channel spend and rating, used by the animated scatter. |
| `data/nutrition_estimates.csv` | Illustrative calories/protein/carbs/fat per standard portion for the Fuel & Spend tab. **Not from the sales dataset** — edit with sourced figures if required. |
| `build_data.py` | Aggregates the six raw CSVs (~50 MB) into the small files above. |
| `make_art.py` | Draws the two illustrations with matplotlib — no external image service. |
| `requirements.txt` | Pinned dependencies, including `gunicorn` for Render. |
| `runtime.txt` | Python version for Render. |
| `project_brief.md` / `project_brief.html` | The required one-page brief (open the HTML and "Save as PDF" if a PDF is wanted). |
| `analysis_findings.md` | Methodology, findings, and honest limitations — good showcase backup. |
| `showcase_script.md` | A timed 3-minute demo script plus likely Q&A answers. |

The raw `sushi_*.csv` files are **not** included in the submission: the course guide asks for a
small upload, and the raw item file alone is ~50 MB. Everything the app needs is pre-aggregated.

---

## 4. How the interactivity meets the rubric

- **Three chart types (plus):** horizontal bar, treemap, dual-axis line, heatmap, animated
  bubble/scatter, pie/donut, and a comparison table.
- **One advanced chart:** the animated year-by-year scatter (Play button + year slider), plus a
  treemap and a heatmap.
- **Shared controls update ≥2 charts:** the year range slider and channel dropdown jointly
  re-render all four KPI cards and all five charts on the first two tabs.
- **Click one chart → another changes:** clicking any bar in *Ingredient share by menu item* or
  any tile in *Menu map* drives the *price vs value over time* line chart and the explanation card.
- **4th tab — Fuel & Spend:** 20 quantity steppers, four target inputs, four live KPI cards,
  progress bars + a grouped bar chart, a greedy next-order recommender that closes macro gaps
  inside a spend cap, and a data-grounded "should I order a drink?" table. Macro numbers are
  clearly labelled illustrative estimates (the dataset has no nutrition fields).

---

## 5. Honest data notes

- There is **no "all-you-can-eat" field** in the data. The app studies value-per-dollar and what
  to prioritise at a fixed-price sushi deal — it does not model AYCE pricing.
- **Ingredient share is a cost ratio, not a quality score.** A high share means more of the price
  is food cost; it says nothing about taste, freshness, or nutrition.
- Weekend per-person spend ($40.33) is effectively identical to weekday ($40.39), so the app makes
  **no "best day to go" claim**.
- The sales dataset has **no nutrition/macro fields**. The calorie/protein/carb values in the
  Fuel & Spend tab are illustrative per-portion estimates in `data/nutrition_estimates.csv`,
  flagged in the app UI and in the brief; they are not measured data and not medical advice.
- All sales figures are derived from the group-supplied dataset; see `analysis_findings.md`.

---

## 6. Team hand-off checklist

- [x] Team name and members, dataset source link, and 4th-tab write-up are in the brief.
- [ ] Fill in the **Render URL** and **GitHub URL** fields (`project_brief.md` + `.html`).
- [ ] Confirm the **AI use note** matches your instructor's policy (a draft is provided).
- [ ] Rehearse `showcase_script.md` once; keep it to ~3 minutes.
- [ ] Zip the folder and submit before **Mon 30 Nov 2026, 11:59 PM**.
