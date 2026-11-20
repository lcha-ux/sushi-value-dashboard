# Showcase script (~3 minutes)

The judges see a live Dash app. Do **not** try to cover everything — walk the one story:
**popular ≠ valuable, and here is a tool that uses that.**

---

### 0:00–0:25 — Hook and question

> "Quick show of hands: when you go to an all-you-can-eat sushi place, how do you decide what to
> order? Most of us go for the familiar things. We had ten years of real sushi receipts — 83,890
> orders — and one question: **where does your sushi dollar actually go, and what should you order
> first?** This is the AYCE Playbook."

Point at the hero and the **question bar**. Pause one beat.

### 0:25–0:55 — The metric (say this clearly, it is the crux)

> "The dataset records what each dish costs the restaurant to make. So we defined **ingredient
> share** — ingredient cost divided by menu price. It's a simple, honest way to ask how much of
> the price ends up in the food. It is *not* a taste score. And the moment you rank the menu by it,
> the spread is enormous: **43%** for sashimi, **7%** for green tea — about a six-times difference."

Point to the four KPI cards: bill per person, best-value item, 6× value spread, guest rating.

### 0:55–1:40 — Value Playbook tab + the click interaction

> "Here's every item ranked by ingredient share. Sashimi, omakase and nigiri at the top; tea, soup
> and edamame at the bottom. Now — this is the bit I want you to watch — **click a bar**."
>
> *[Click the Green Tea bar, then a Sashimi bar.]*
>
> "The chart on the right follows: it redraws that item's price and value history and explains the
> number. Clicking the treemap does the same thing. So it's not a static picture — you can explore
> the whole menu."

### 1:40–2:15 — The Bill tab + advanced chart

> "Second tab: the bill. A day-by-month heatmap of spend per person, and a party-size chart that
> shows the bill scales almost exactly with heads. And here's our advanced chart — an animated,
> ten-year scatter of spend per person against guest rating. Press play."
>
> *[Press **▶ PLAY 10 YEARS** and let it run.]*
>
> "Spend per person climbs from about **$30 to $46**, but the group size didn't change — and ratings
> climbed too, apart from a dip in 2020. Notice we *don't* claim a best day to go: weekend and
> weekday spending are basically identical, and we're happy to say so."

### 2:15–2:40 — Build Your Plate tab + shared filters

> "Third tab — the payoff. Set a per-person budget… say **fifty dollars**… and the optimiser builds
> the highest-value combination of up to six different items. It gets about **40%** of your money
> into ingredients versus about **31%** for a typical order — same budget, about nine points more
> food. And these two filters up here, years and channel, update *every* card and *every* chart. Try
> switching to takeaway."

*[Change the channel dropdown once so the shared filtering is visible.]*

### 2:40–3:05 — Fuel & Spend tab (the personalised payoff — great for votes)

> "One more tab, and this is the one people actually play with. Tell it what you ate — I'll add two
> sashimi, two tuna nigiri and a beer — set your calorie, protein, carb and dollar targets, and it
> tracks your spend against the cost of the food and shows your progress. Then it recommends your
> **next order** to close the biggest remaining macro gaps inside your budget, and answers the drink
> question with our cost data: drinks have low ingredient share and no protein, so skip them if the
> goal is maximum food."

*[Set a couple of quantities on the Fuel & Spend tab so the KPI cards and recommendation update.]*

> "Be honest about one thing: the sales data has no nutrition fields, so those macro numbers are
> clearly labelled illustrative estimates — the cost figures are the real data."

### 3:05–3:15 — Close

> "So: the practical takeaway is prioritise sashimi, nigiri and omakase, and treat tea, soup and
> edamame as fillers. One question, backed by ten years of data, with a tool you can actually use.
> The AYCE Playbook — please vote for us."

> *Running long? Cut the live Fuel & Spend demo to the single sentence about recommendations — the
> tab stays in the app for judges to explore afterwards.*

---

## Likely questions and short answers

- **"Is ingredient share the same as quality?"** No. It's a cost ratio. It tells you how much of
  the price is food cost, not whether the fish is better. We chose it because the data actually
  contains it, and we say that plainly in the app.
- **"Did you analyse all-you-can-eat pricing?"** No — there's no AYCE field. We studied value per
  dollar and what to prioritise at a fixed-price deal. That's exactly what the brief says.
- **"Where did the numbers come from?"** Six group-supplied CSVs of restaurant sales, 2015–2024.
  `build_data.py` aggregates them into the small files the app reads; `analysis_findings.md` lists
  every figure.
- **"Why no raw data in the zip?"** The item file alone is ~50 MB; the course asks for a small
  upload. The app ships pre-aggregated CSVs (~200 KB total) and the script that rebuilds them.
- **"Does it work on a phone?"** Yes — the layout is responsive and collapses to one column.
- **"Why might the live site be slow the first time?"** Render's free tier sleeps when idle; the
  first request after inactivity takes ~30–60 seconds to wake.
- **"Where do the calorie/macro numbers come from?"** The sales dataset has no nutrition fields.
  They're illustrative per-portion estimates we added for the interactive tracker, clearly labelled
  in the app and editable in `data/nutrition_estimates.csv`. The price and cost figures are real.
- **"Is the drink recommendation medical/nutritional advice?"** No — it's a value argument from the
  cost data (drinks have low ingredient share and no protein), not dietary advice.
- **"What did the AI do?"** It helped analyse the data, write the code and draft the text. The team
  checked every figure, chose the framing and made all final decisions. Nothing was submitted
  automatically.
