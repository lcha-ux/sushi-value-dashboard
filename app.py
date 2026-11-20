"""The AYCE Playbook — a Dash dashboard about getting the most value from sushi.

Question: Where does your sushi dollar actually go, and what should you order first?

Run locally:  python app.py   ->  http://127.0.0.1:8050
Render start command:  gunicorn app:server
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, ctx, dcc, html

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

menu = pd.read_csv(DATA / "menu_items.csv")
item_facts = pd.read_csv(DATA / "item_facts.csv")
visit_facts = pd.read_csv(DATA / "visit_facts.csv")
party_facts = pd.read_csv(DATA / "party_facts.csv")
annual = pd.read_csv(DATA / "annual_channel.csv")
nutrition = pd.read_csv(DATA / "nutrition_estimates.csv")
NUTRI = nutrition.set_index("item")[["calories", "protein_g", "carbs_g", "fat_g"]].to_dict("index")

QTY_CATEGORIES = ["nigiri", "sashimi", "omakase", "roll", "side", "drink", "dessert"]
QTY_ORDER = [item for cat in QTY_CATEGORIES for item in menu[menu["category"] == cat]["item"]]

YEARS = sorted(visit_facts["year"].unique())
CHANNELS = ["All"] + sorted(visit_facts["channel"].unique().tolist())
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CAT_COLORS = {
    "nigiri": "#E4572E", "sashimi": "#E9B44C", "omakase": "#8A7CF0",
    "roll": "#4EA8A0", "side": "#8FBF6A", "drink": "#C982B2", "dessert": "#D98E73",
}
CHANNEL_COLORS = {"dine_in": "#E4572E", "takeaway": "#E9B44C", "delivery": "#4EA8A0"}
INK, CREAM, MUTED = "#0B1020", "#F5F1E8", "#9AA7B4"

app = Dash(__name__, assets_folder="assets", title="The AYCE Playbook")
server = app.server  # Render requires this exact name


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def money(x: float, digits: int = 0) -> str:
    return f"${x:,.{digits}f}"


def base_fig(fig: go.Figure, height: int = 330, showlegend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=42, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Atkinson Hyperlegible, Arial, sans-serif", color=CREAM, size=13),
        title=dict(font=dict(size=15, color=CREAM), x=0.02, xanchor="left"),
        hoverlabel=dict(bgcolor="#1B2433", font_color=CREAM, bordercolor="#3A4658"),
        showlegend=showlegend,
        legend=dict(orientation="h", y=1.16, x=0, font=dict(size=11, color=MUTED)),
    )
    fig.update_xaxes(gridcolor="#222B3A", zerolinecolor="#364153",
                     tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=11))
    fig.update_yaxes(gridcolor="#222B3A", zerolinecolor="#364153",
                     tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=11))
    return fig


def scoped_items(year_range, channel):
    d = item_facts[(item_facts["year"] >= year_range[0]) & (item_facts["year"] <= year_range[1])]
    if channel != "All":
        d = d[d["channel"] == channel]
    return d


def scoped_visits(year_range, channel):
    d = visit_facts[(visit_facts["year"] >= year_range[0]) & (visit_facts["year"] <= year_range[1])]
    if channel != "All":
        d = d[d["channel"] == channel]
    return d


def scoped_party(year_range, channel):
    d = party_facts[(party_facts["year"] >= year_range[0]) & (party_facts["year"] <= year_range[1])]
    if channel != "All":
        d = d[d["channel"] == channel]
    return d


def scoped_annual(year_range, channel):
    d = annual[(annual["year"] >= year_range[0]) & (annual["year"] <= year_range[1])]
    if channel != "All":
        d = d[d["channel"] == channel]
    return d


def ban(label, value, sub, accent="#E4572E"):
    return html.Div(className="ban", style={"--accent": accent}, children=[
        html.Div(className="ban-label", children=label),
        html.Div(className="ban-value", children=value),
        html.Div(className="ban-sub", children=sub),
    ])


# --------------------------------------------------------------------------- #
# Figures
# --------------------------------------------------------------------------- #
def value_bar_figure(d):
    g = (d.groupby(["item", "category"])
         .agg(value=("value_share", "mean"), units=("units", "sum"),
              revenue=("revenue", "sum"), cogs=("cogs", "sum"))
         .reset_index())
    g["value_pct"] = (g["value"] * 100).round(1)
    g = g.sort_values("value_pct", ascending=True)  # highest ends up at the top

    fig = go.Figure(go.Bar(
        x=g["value_pct"], y=g["item"], orientation="h",
        marker=dict(color=[CAT_COLORS[c] for c in g["category"]],
                    line=dict(color=INK, width=0.5)),
        customdata=np.stack([g["units"], g["revenue"], g["cogs"]], axis=-1),
        text=[f"{v:.0f}%" for v in g["value_pct"]],
        textposition="outside", cliponaxis=False,
        hovertemplate=("<b>%{y}</b><br>Ingredient share: %{x:.1f}%"
                       "<br>Units sold: %{customdata[0]:,}"
                       "<br>Revenue: $%{customdata[1]:,.0f}"
                       "<br>Ingredients: $%{customdata[2]:,.0f}<extra></extra>"),
    ))
    fig.update_xaxes(title="% of the menu price that is ingredients", range=[0, 52], ticksuffix="%")
    fig.update_yaxes(tickfont=dict(size=11, color=CREAM))
    return base_fig(fig.update_layout(title="Ingredient share by menu item  ·  click a bar"), 590)


def treemap_figure(d):
    t = (d.groupby(["category", "item"])
         .agg(units=("units", "sum"), revenue=("revenue", "sum"), cogs=("cogs", "sum"))
         .reset_index())
    t["value_pct"] = (t["cogs"] / t["revenue"] * 100).round(1)
    fig = px.treemap(
        t, path=["category", "item"], values="units", color="value_pct",
        color_continuous_scale=[[0, "#245450"], [0.5, "#E9B44C"], [1, "#E4572E"]],
        range_color=[5, 45],
        hover_data={"units": ":,", "value_pct": ":.1f", "revenue": ":,.0f"},
    )
    fig.update_traces(textinfo="label+value", textfont=dict(size=11),
                      marker=dict(line=dict(width=1, color=INK)),
                      hovertemplate=("<b>%{label}</b><br>Units: %{value:,}"
                                     "<br>Ingredient share: %{color:.1f}%<extra></extra>"))
    return base_fig(fig.update_layout(title="Menu map  ·  size = pieces sold, colour = value"), 590)


def heatmap_figure(v):
    g = (v.groupby(["day_of_week", "month"])
         .agg(revenue=("revenue", "sum"), party=("party_sum", "sum"))
         .reset_index())
    g["per_person"] = g["revenue"] / g["party"]
    piv = g.pivot(index="day_of_week", columns="month", values="per_person").reindex(DOW)
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[MONTHS[m - 1] for m in piv.columns], y=piv.index,
        colorscale=[[0, "#173B3B"], [0.5, "#E9B44C"], [1, "#E4572E"]],
        colorbar=dict(title="$ / head", thickness=9, len=0.85,
                      tickfont=dict(color=MUTED), titlefont=dict(color=MUTED)),
        hovertemplate="%{y} · %{x}<br>$%{z:.2f} per person<extra></extra>",
    ))
    fig.update_layout(title="Average bill per person  ·  day × month")
    return base_fig(fig, 330)


def party_figure(p):
    g = (p.groupby("party_size")
         .agg(revenue=("revenue", "sum"), people=("party_sum", "sum"), orders=("orders", "sum"))
         .reset_index())
    g["per_person"] = g["revenue"] / g["people"]
    fig = go.Figure(go.Bar(
        x=g["party_size"].astype(str), y=g["per_person"],
        marker=dict(color="#4EA8A0", line=dict(color=INK, width=0.5)),
        text=[f"${v:.0f}" for v in g["per_person"]], textposition="outside",
        customdata=g["orders"],
        hovertemplate="<b>%{x} people</b><br>$%{y:.2f} per person<br>%{customdata:,} orders<extra></extra>",
    ))
    fig.update_xaxes(title="Party size")
    fig.update_yaxes(title="$ per person", range=[0, 55])
    fig.update_layout(title="The bill scales almost perfectly with heads")
    return base_fig(fig, 330)


def animated_figure(a):
    years = sorted(a["year"].unique())
    frames = []
    for y in years:
        d = a[a["year"] == y]
        frames.append(dict(
            name=str(y),
            data=[go.Scatter(
                x=d["per_person"], y=d["avg_rating"], mode="markers+text",
                text=d["channel"].str.replace("_", " "), textposition="top center",
                textfont=dict(size=10, color=CREAM),
                marker=dict(size=np.sqrt(d["orders"]) / 3 + 9,
                            color=[CHANNEL_COLORS[c] for c in d["channel"]],
                            line=dict(color=INK, width=1), opacity=0.88),
                customdata=np.stack([d["orders"], d["rating_n"]], axis=-1),
                hovertemplate=("<b>%{text} · " + str(y) + "</b><br>$%{x:.2f} per person"
                               "<br>Rating: %{y:.2f}<br>%{customdata[0]:,} orders<extra></extra>"),
            )],
        ))
    fig = go.Figure(data=frames[0]["data"], frames=frames)
    buttons = [dict(label="▶  PLAY 10 YEARS", method="animate",
                    args=[None, dict(frame=dict(duration=650, redraw=True), fromcurrent=True)]),
               dict(label="❚❚", method="animate",
                    args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])]
    fig.update_layout(
        title="Ten years of sushi  ·  spend per person vs guest rating (press play)",
        xaxis_title="$ per person", yaxis_title="Average rating",
        yaxis=dict(range=[3.0, 4.1]),
        updatemenus=[dict(type="buttons", showactive=False, x=0.02, y=1.13,
                          buttons=buttons, bgcolor="#1B2433", bordercolor="#3A4658")],
        sliders=[dict(
            active=0, x=0.36, y=1.14, len=0.62,
            bgcolor="#1B2433", tickcolor=MUTED, font=dict(size=10, color=MUTED),
            currentvalue=dict(prefix="Year: ", font=dict(size=12, color=CREAM)),
            steps=[dict(label=str(y), method="animate",
                        args=[[str(y)], dict(frame=dict(duration=350, redraw=True), mode="immediate")])
                   for y in years],
        )],
    )
    return base_fig(fig, 370)


def item_trend_figure(d, selected):
    t = (d[d["item"] == selected].groupby("year")
         .agg(price=("avg_price", "mean"), value=("value_share", "mean"), units=("units", "sum"))
         .reset_index())
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t["year"], y=t["price"], mode="lines+markers", name="Average price",
        line=dict(color="#E9B44C", width=3), marker=dict(size=7),
        hovertemplate="%{x}: $%{y:.2f}<extra>Average price</extra>"))
    fig.add_trace(go.Scatter(
        x=t["year"], y=t["value"] * 100, mode="lines+markers", name="Ingredient share",
        yaxis="y2", line=dict(color="#E4572E", width=2, dash="dot"), marker=dict(size=6),
        hovertemplate="%{x}: %{y:.1f}%<extra>Ingredient share</extra>"))
    fig.update_layout(
        title=f"{selected}  ·  price vs value over time",
        xaxis=dict(dtick=1, title=""),
        yaxis=dict(title="Average price ($)", range=[0, max(t["price"].max() * 1.2, 10)]),
        yaxis2=dict(title="Ingredient share (%)", overlaying="y", side="right", range=[0, 60],
                    showgrid=False),
    )
    return base_fig(fig, 330, showlegend=True)


# --------------------------------------------------------------------------- #
# Plate builder (small dynamic-programming optimiser)
# --------------------------------------------------------------------------- #
def optimise_plate(budget: int, goal: str):
    limit = int(round(budget * 2))  # prices are stored in half-dollar units
    cand = menu if goal == "value" else menu[menu["pieces"].notna()]
    cand = cand.reset_index(drop=True)
    dp = {(0, 0): (0.0, ())}  # (half-dollars used, items) -> (score, chosen indices)
    for idx, row in cand.iterrows():
        price = int(round(row["price"] * 2))
        gain = float(row["median_cogs"] if goal == "value" else row["pieces"])
        fresh = {}
        for (used, count), (score, picked) in dp.items():
            new_used, new_count = used + price, count + 1
            if new_used <= limit and new_count <= 6:
                candidate = (score + gain, picked + (idx,))
                key = (new_used, new_count)
                if key not in fresh or candidate[0] > fresh[key][0]:
                    fresh[key] = candidate
        for key, candidate in fresh.items():
            if key not in dp or candidate[0] > dp[key][0]:
                dp[key] = candidate
    best_key = max(dp, key=lambda k: (dp[k][0], -k[0]))
    score, picked = dp[best_key]
    picks = cand.loc[list(picked)] if picked else cand.iloc[0:0]
    return picks, score, best_key[0] / 2


def classic_plate(budget: int):
    limit = int(round(budget * 2))
    top = menu.sort_values("units", ascending=False).head(4)
    chosen, spent = [], 0
    for _, row in top.iterrows():
        price = int(round(row["price"] * 2))
        for _ in range(2):  # a normal order rarely repeats an item more than twice
            if spent + price <= limit:
                chosen.append(row)
                spent += price
            else:
                break
    return pd.DataFrame(chosen)


# --------------------------------------------------------------------------- #
# Macro tracker helpers
# --------------------------------------------------------------------------- #
MACROS = [("calories", "Calories", "kcal"), ("protein_g", "Protein", "g"),
          ("carbs_g", "Carbs", "g")]
ZERO_MACROS = {k: 0.0 for k, _, _ in MACROS}


def plate_math(qty_map):
    """Turn {item: quantity} into a line-item table plus spend / cost / macro totals."""
    lines = []
    for item, qty in qty_map.items():
        try:
            q = int(qty or 0)
        except (TypeError, ValueError):
            q = 0
        if q <= 0:
            continue
        row = menu[menu["item"] == item]
        if row.empty:
            continue
        row = row.iloc[0]
        n = NUTRI.get(item, {})
        lines.append({
            "item": item, "qty": q, "category": row["category"],
            "price": float(row["price"]) * q,
            "cogs": float(row["median_cogs"]) * q,
            "share": float(row["value_share"]),
            **{k: float(n.get(k, 0)) * q for k in ZERO_MACROS},
        })
    df = pd.DataFrame(lines)
    totals = {"price": 0.0, "cogs": 0.0, **ZERO_MACROS}
    if not df.empty:
        totals.update(price=df["price"].sum(), cogs=df["cogs"].sum(),
                      **{k: df[k].sum() for k in ZERO_MACROS})
    return df, totals


def recommend_next(qty_map, targets, budget):
    """Greedy recommendation for the next portion that best closes remaining macro gaps."""
    _, cur = plate_math(qty_map)
    try:
        cap = float(budget or 0)
    except (TypeError, ValueError):
        cap = 0.0
    gaps = {k: max(float(targets.get(k) or 0) - cur[k], 0.0) for k in ZERO_MACROS}
    if not any(g > 0 for g in gaps.values()):
        return [], "Every macro target is already met — enjoy your plate. 🍣"
    if sum(gaps.values()) == 0:
        return [], "Set a calorie / protein / carb target on the left to get recommendations."
    if cap <= cur["price"]:
        return [], f"You are at your {money(cap)} cap — nothing else fits the budget."

    room = cap - cur["price"]
    scored = []
    for _, r in menu.iterrows():
        price = float(r["price"])
        if price <= 0 or price > room:
            continue
        n = NUTRI.get(r["item"], {})
        parts = [min(float(n.get(k, 0)), gaps[k]) / gaps[k]
                 for k in ZERO_MACROS if gaps[k] > 0]
        fit = sum(parts) / len(parts) if parts else 0.0
        if fit <= 0:
            continue
        score = fit / price * (1 + 0.25 * float(r["value_share"]))
        scored.append((score, r["item"], price, fit, n))
    scored.sort(key=lambda x: x[0], reverse=True)

    picks = []
    for _, item, price, fit, n in scored[:3]:
        bits = []
        for k in ZERO_MACROS:
            if gaps[k] > 0 and float(n.get(k, 0)) > 0:
                label = {"calories": "kcal", "protein_g": "g protein", "carbs_g": "g carbs"}[k]
                bits.append(f"{float(n.get(k, 0)):.0f} {label}")
        picks.append({"item": item, "price": price, "fit": fit,
                      "detail": ", ".join(bits) if bits else "little macro impact"})
    return picks, ""


def drink_advice(df, totals, budget):
    """Data-grounded answer to 'which drink should I order?'."""
    drinks = menu[menu["category"] == "drink"].sort_values("value_share", ascending=False)
    spent_drinks = df[df["category"] == "drink"]["price"].sum() if not df.empty else 0.0
    best = drinks.iloc[0]
    if spent_drinks > 0:
        headline = (f"{money(spent_drinks, 2)} of your plate went to drinks — "
                    f"that is {spent_drinks / max(totals['price'], 1) * 100:.0f}% of your spend, "
                    f"and drinks bring no protein.")
    elif totals["price"] > 0:
        headline = "No drinks in your plate — that keeps the whole budget on food."
    else:
        headline = "Add a few items to see how drinks affect your plate."
    kicker = (f"Among drinks, {best['item']} has the highest ingredient share "
              f"({float(best['value_share']) * 100:.0f}%), but it still adds calories and zero "
              f"protein. To eat the most food for your money, skip drinks and add nigiri.")
    rows = []
    for _, r in drinks.iterrows():
        n = NUTRI.get(r["item"], {})
        rows.append(html.Tr(children=[
            html.Td(r["item"]),
            html.Td(money(float(r["price"]), 2)),
            html.Td(f"{float(r['value_share']) * 100:.0f}%"),
            html.Td(f"{float(n.get('calories', 0)):.0f}"),
            html.Td("most food-value" if r["item"] == best["item"] else "adds spend, no protein"),
        ]))
    table = html.Table(children=[
        html.Thead(html.Tr([html.Th("Drink"), html.Th("Price"), html.Th("Ingredient share"),
                            html.Th("kcal*"), html.Th("Take")])),
        html.Tbody(rows),
    ])
    return headline, kicker, table


def progress_bar(label, value, target, unit, colour):
    pct = min(value / max(target, 1) * 100, 100) if target else 0
    state = "met" if target and value >= target else ""
    return html.Div(className="prog", children=[
        html.Div(className="prog-top", children=[
            html.Span(label),
            html.Span(f"{value:,.0f} / {target:,.0f} {unit}", className=state),
        ]),
        html.Div(className="prog-track", children=[
            html.Div(className="prog-fill", style={"width": f"{pct}%", "--bar": colour}),
        ]),
    ])


def qty_row(r):
    return html.Div(className="qty-row", children=[
        html.Span(r["item"], className="qty-name", title=r["item"]),
        html.Span(f"{money(float(r['price']), 2)}", className="qty-price"),
        dcc.Input(id={"type": "qty", "index": r["item"]}, type="number", min=0, max=30,
                  step=1, value=0, className="qty-input", debounce=False,
                  placeholder="0"),
    ])


# --------------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------------- #
app.layout = html.Div([
    html.Div(className="hero", style={"backgroundImage": f"url({app.get_asset_url('hero.png')})"},
             children=[
        html.Div(className="hero-inner", children=[
            html.Div(className="eyebrow", children="A DATA-DRIVEN GUIDE TO SUSHI VALUE"),
            html.H1("THE AYCE PLAYBOOK"),
            html.P("Ten years of real sushi receipts, one simple question: "
                   "what should you order first?"),
            html.Div(className="hero-chips", children=[
                html.Span("🍣  83,890 orders"), html.Span("🧾  ~1M menu items"),
                html.Span("📅  2015–2024"),
            ]),
        ]),
    ]),

    html.Div(className="question-bar", children=[
        html.Span(className="q-tag", children="THE QUESTION"),
        html.Span(children="Where does your sushi dollar actually go — and what should you order first?"),
    ]),

    html.Div(className="controls", children=[
        html.Div(className="control control-years", children=[
            html.Label("YEARS"),
            dcc.RangeSlider(
                id="year-slider", min=YEARS[0], max=YEARS[-1], value=[YEARS[0], YEARS[-1]],
                marks={str(y): str(y) for y in YEARS}, step=1, allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ]),
        html.Div(className="control", children=[
            html.Label("ORDER CHANNEL"),
            dcc.Dropdown(
                id="channel", clearable=False,
                options=[{"label": c.replace("_", " ").title(), "value": c} for c in CHANNELS],
                value="All",
            ),
        ]),
        html.Div(className="control-hint",
                 children="↗  These two controls update every card and chart below."),
    ]),

    html.Div(id="bans", className="ban-grid"),
    html.Div(className="method-note", children=[
        html.B("How to read “ingredient share”:"),
        " restaurant cost of ingredients ÷ menu price. A higher share means more of your "
        "dollar ends up in the food — the items to prioritise at any fixed-price sushi deal. "
        "It is a transparent proxy, not a claim about taste or nutrition.",
    ]),

    dcc.Tabs(id="tabs", value="value", className="tabs", children=[
        dcc.Tab(label="🍣  Value Playbook", value="value", className="tab",
                selected_className="tab-on", children=html.Div(className="tab-body", children=[
            html.Div(className="section-head", children=[
                html.H2("What your money is actually buying"),
                html.P("Ranked by how much of each price is ingredients. Click any bar or tile "
                       "to inspect that item's history →"),
            ]),
            html.Div(className="grid-2", children=[
                html.Div(className="panel", children=[dcc.Graph(id="value-bar",
                         config={"displayModeBar": False})]),
                html.Div(className="panel", children=[dcc.Graph(id="value-treemap",
                         config={"displayModeBar": False})]),
            ]),
            html.Div(className="grid-2", children=[
                html.Div(className="panel", children=[dcc.Graph(id="item-trend",
                         config={"displayModeBar": False})]),
                html.Div(className="panel explain", children=[
                    html.H3(id="item-title", children="Sashimi Platter (10pc)"),
                    html.P(id="item-copy", children=""),
                    html.Div(className="explain-art", children=[
                        html.Img(src=app.get_asset_url("plate.png"), alt="Sushi illustration"),
                    ]),
                ]),
            ]),
        ])),

        dcc.Tab(label="📈  The Bill", value="bill", className="tab",
                selected_className="tab-on", children=html.Div(className="tab-body", children=[
            html.Div(className="section-head", children=[
                html.H2("The bill, the timing and the trend"),
                html.P("Same filters, different lens: when sushi costs more, and how guests "
                       "rated the experience over ten years."),
            ]),
            html.Div(className="grid-2", children=[
                html.Div(className="panel", children=[dcc.Graph(id="heatmap",
                         config={"displayModeBar": False})]),
                html.Div(className="panel", children=[dcc.Graph(id="party-bar",
                         config={"displayModeBar": False})]),
            ]),
            html.Div(className="panel", children=[dcc.Graph(id="animated",
                     config={"displayModeBar": False})]),
        ])),

        dcc.Tab(label="🍱  Build Your Plate", value="plate", className="tab",
                selected_className="tab-on", children=html.Div(className="tab-body", children=[
            html.Div(className="section-head", children=[
                html.H2("Put the finding to work"),
                html.P("Set a per-person budget. The optimiser builds the highest-value "
                       "combination of up to six different items and compares it with a "
                       "typical four-item order."),
            ]),
            html.Div(className="builder", children=[
                html.Div(className="builder-art", children=[
                    html.Img(src=app.get_asset_url("plate.png"), alt="Sushi illustration"),
                ]),
                html.Div(className="builder-main", children=[
                    html.Div(className="builder-field", children=[
                        html.Label("BUDGET PER PERSON"),
                        dcc.Slider(id="budget", min=15, max=150, step=5, value=50,
                                   marks={15: "$15", 50: "$50", 100: "$100", 150: "$150"},
                                   tooltip={"placement": "bottom", "always_visible": False}),
                    ]),
                    html.Div(className="builder-field", children=[
                        html.Label("OPTIMISE FOR"),
                        dcc.Dropdown(
                            id="goal", clearable=False,
                            options=[{"label": "Ingredient value (most food for the money)",
                                      "value": "value"},
                                     {"label": "Pieces on the plate (portion-count items only)",
                                      "value": "pieces"}],
                            value="value",
                        ),
                    ]),
                    html.Div(id="builder-kpis", className="mini-bans"),
                    html.Div(id="builder-table", className="pick-list"),
                ]),
                html.Div(className="panel builder-donut", children=[
                    dcc.Graph(id="builder-donut", config={"displayModeBar": False}),
                ]),
            ]),
        ])),

        dcc.Tab(label="🎯  Fuel & Spend", value="fuel", className="tab",
                selected_className="tab-on", children=html.Div(className="tab-body", children=[
            html.Div(className="section-head", children=[
                html.H2("Track what you ate — and what it cost the restaurant"),
                html.P("Add the quantities on your plate, set your macro and dollar targets, "
                       "and get a data-backed recommendation for your next order."),
            ]),
            html.Div(className="nutrition-note", children=[
                html.B("* Nutrition values are illustrative estimates for a standard portion, "),
                "not measured in the sales dataset. Edit data/nutrition_estimates.csv to use "
                "sourced figures. Not medical advice.",
            ]),
            html.Div(className="fuel-grid", children=[
                html.Div(className="fuel-left", children=[
                    html.Div(className="panel targets", children=[
                        html.H3("Your targets"),
                        html.Div(className="target-grid", children=[
                            html.Div(className="target-field", children=[
                                html.Label("CALORIES (kcal)"),
                                dcc.Input(id="target-kcal", type="number", min=0, max=10000,
                                          step=100, value=2000, className="target-input"),
                            ]),
                            html.Div(className="target-field", children=[
                                html.Label("PROTEIN (g)"),
                                dcc.Input(id="target-protein", type="number", min=0, max=1000,
                                          step=10, value=120, className="target-input"),
                            ]),
                            html.Div(className="target-field", children=[
                                html.Label("CARBS (g)"),
                                dcc.Input(id="target-carbs", type="number", min=0, max=1000,
                                          step=10, value=250, className="target-input"),
                            ]),
                            html.Div(className="target-field", children=[
                                html.Label("SPEND CAP ($)"),
                                dcc.Input(id="target-budget", type="number", min=0, max=1000,
                                          step=5, value=50, className="target-input"),
                            ]),
                        ]),
                    ]),
                    html.Div(className="panel menu-picker", children=[
                        html.H3("What did you eat?"),
                        html.Div(className="qty-list", children=[
                            html.Div(className="qty-group", children=[
                                html.H4(cat.upper()),
                                *[qty_row(r) for _, r in menu[menu["category"] == cat].iterrows()],
                            ])
                            for cat in QTY_CATEGORIES
                        ]),
                    ]),
                ]),
                html.Div(className="fuel-right", children=[
                    html.Div(id="fuel-kpis", className="ban-grid fuel-bans"),
                    html.Div(className="panel progress-panel", children=[
                        html.H3("Progress toward your targets"),
                        html.Div(id="macro-bars"),
                    ]),
                    html.Div(className="panel", children=[
                        dcc.Graph(id="macro-compare", config={"displayModeBar": False}),
                    ]),
                    html.Div(id="next-order", className="panel recommend"),
                    html.Div(id="drink-panel", className="panel drink-panel"),
                ]),
            ]),
        ])),
    ]),

    html.Footer(children=[
        html.Span("Built with Dash + Plotly  ·  Source: group-supplied restaurant sales data, 2015–2024"),
        html.Span("🍣  Move the filters. Click a bar. Press play. Then vote."),
    ]),
], className="app")


# --------------------------------------------------------------------------- #
# Callbacks
# --------------------------------------------------------------------------- #
@app.callback(
    Output("bans", "children"),
    Output("value-bar", "figure"),
    Output("value-treemap", "figure"),
    Output("heatmap", "figure"),
    Output("party-bar", "figure"),
    Output("animated", "figure"),
    Input("year-slider", "value"), Input("channel", "value"),
)
def update_dashboard(year_range, channel):
    di, dv, dp, da = (scoped_items(year_range, channel), scoped_visits(year_range, channel),
                      scoped_party(year_range, channel), scoped_annual(year_range, channel))

    per_person = dv["revenue"].sum() / dv["party_sum"].sum()
    rated = dv[dv["rating_n"] > 0]
    avg_rating = rated["rating_sum"].sum() / max(rated["rating_n"].sum(), 1)
    top = (di.groupby("item").agg(c=("cogs", "sum"), r=("revenue", "sum"))
           .assign(s=lambda x: x["c"] / x["r"]).sort_values("s", ascending=False))
    best_item, best_share = top.index[0], top["s"].iloc[0] * 100
    low_share = top["s"].iloc[-1] * 100
    span = f"{year_range[0]}–{year_range[1]}"
    channel_label = "all channels" if channel == "All" else channel.replace("_", " ")

    bans = [
        ban("AVERAGE BILL / PERSON", money(per_person, 2), f"{span} · {channel_label}", "#E4572E"),
        ban("BEST VALUE ITEM", best_item.replace(" (", "\n("), f"{best_share:.0f}% of price is ingredients", "#E9B44C"),
        ban("VALUE SPREAD", f"{best_share / max(low_share, 1):.0f}×",
            f"{best_share:.0f}% top item vs {low_share:.0f}% green tea", "#4EA8A0"),
        ban("AVERAGE GUEST RATING", f"{avg_rating:.2f} / 5",
            f"{int(rated['rating_n'].sum()):,} rated orders", "#8A7CF0"),
    ]
    return (bans, value_bar_figure(di), treemap_figure(di), heatmap_figure(dv),
            party_figure(dp), animated_figure(da))


@app.callback(
    Output("item-trend", "figure"),
    Output("item-title", "children"),
    Output("item-copy", "children"),
    Input("value-bar", "clickData"), Input("value-treemap", "clickData"),
    Input("year-slider", "value"), Input("channel", "value"),
)
def inspect_item(bar_click, tree_click, year_range, channel):
    trigger = ctx.triggered_id
    selected = None
    if trigger == "value-bar" and bar_click:
        selected = bar_click["points"][0]["y"]
    elif trigger == "value-treemap" and tree_click:
        label = tree_click["points"][0].get("label")
        names = set(menu["item"])
        if label in names:
            selected = label
        elif label in set(menu["category"]):
            selected = (menu[menu["category"] == label]
                        .sort_values("units", ascending=False)["item"].iloc[0])
    if selected is None:
        selected = menu.iloc[0]["item"]

    d = scoped_items(year_range, channel)
    row = menu[menu["item"] == selected].iloc[0]
    sub = d[d["item"] == selected]
    share = sub["cogs"].sum() / max(sub["revenue"].sum(), 1) * 100
    pieces = "" if pd.isna(row["pieces"]) else f" Each portion is {int(row['pieces'])} pieces."
    copy = (f"Across the selected years, {share:.0f}% of every dollar spent on this item "
            f"went into ingredients — {row['category']} category, "
            f"{int(sub['units'].sum()):,} portions sold.{pieces} "
            f"Median menu price: {money(row['median_price'], 2)}.")
    return item_trend_figure(d, selected), selected, copy


@app.callback(
    Output("builder-kpis", "children"),
    Output("builder-table", "children"),
    Output("builder-donut", "figure"),
    Input("budget", "value"), Input("goal", "value"),
)
def build_plate(budget, goal):
    picks, score, spent = optimise_plate(budget, goal)
    classic = classic_plate(budget)
    new_share = picks["median_cogs"].sum() / max(spent, 1) * 100
    old_share = classic["median_cogs"].sum() / max(classic["price"].sum(), 1) * 100
    if goal == "value":
        headline, sub = f"{new_share:.0f}%", f"of your ${budget} is ingredients"
        third = ban("THE SWAP", f"{new_share - old_share:+.0f} pts",
                    "ingredient share vs typical order", "#E4572E")
    else:
        classic_pcs = classic["pieces"].fillna(0).sum()
        headline, sub = f"{score:.0f} pcs", f"for ${spent:.1f} spent"
        third = ban("THE SWAP", f"+{score - classic_pcs:.0f} pcs",
                    "more pieces vs typical order", "#E4572E")

    kpis = [
        ban("YOUR PLATE", headline, sub, "#E9B44C"),
        ban("TYPICAL ORDER", f"{old_share:.0f}%", "ingredient share, top 4 items", "#8A7CF0"),
        third,
    ]

    rows = []
    for _, r in picks.iterrows():
        rows.append(html.Tr(children=[
            html.Td(r["item"]),
            html.Td(money(r["price"], 2)),
            html.Td(money(r["median_cogs"], 2)),
            html.Td("—" if pd.isna(r["pieces"]) else f"{int(r['pieces'])} pc"),
        ]))
    table = html.Table(children=[
        html.Thead(html.Tr([html.Th("Item"), html.Th("Price"), html.Th("In it"), html.Th("Portion")])),
        html.Tbody(rows if rows else [html.Tr(html.Td("No items fit this budget."))]),
    ])
    table_wrap = html.Div(children=[
        html.H4("Your optimised plate", className="pick-title"), table,
        html.P(f"Total: {money(spent, 2)}  ·  {len(picks)} different items  ·  "
               f"comparison order: {', '.join(classic['item'].tolist())}",
               className="pick-foot"),
    ])

    fig = go.Figure(go.Pie(
        labels=picks["item"], values=picks["median_cogs"], hole=0.64,
        marker=dict(colors=[CAT_COLORS[c] for c in picks["category"]],
                    line=dict(color=INK, width=2)),
        textinfo="label+percent", textfont=dict(size=10, color=CREAM),
        hovertemplate="<b>%{label}</b><br>$%{value:.2f} of ingredients<extra></extra>",
    ))
    fig.update_layout(title="Where the food value comes from")
    fig = base_fig(fig, 340, showlegend=False)
    fig.update_traces(textposition="inside")
    return kpis, table_wrap, fig


@app.callback(
    Output("fuel-kpis", "children"),
    Output("macro-bars", "children"),
    Output("macro-compare", "figure"),
    Output("next-order", "children"),
    Output("drink-panel", "children"),
    Input({"type": "qty", "index": ALL}, "value"),
    Input("target-kcal", "value"),
    Input("target-protein", "value"),
    Input("target-carbs", "value"),
    Input("target-budget", "value"),
)
def update_fuel(qtys, target_kcal, target_protein, target_carbs, target_budget):
    qty_map = dict(zip(QTY_ORDER, qtys))
    df, t = plate_math(qty_map)
    targets = {"calories": target_kcal, "protein_g": target_protein, "carbs_g": target_carbs}
    share = t["cogs"] / max(t["price"], 1) * 100
    portions = int(df["qty"].sum()) if not df.empty else 0

    kpis = [
        ban("PRICE YOU PAID", money(t["price"], 2), f"{portions} portions on your plate", "#E4572E"),
        ban("COST OF THE FOOD", money(t["cogs"], 2), "what the kitchen spent on ingredients", "#E9B44C"),
        ban("INGREDIENT SHARE", f"{share:.0f}%", "of your spend ended up in the food", "#4EA8A0"),
        ban("CALORIES (EST.)", f"{t['calories']:,.0f}",
            f"{t['protein_g']:.0f}g protein · {t['carbs_g']:.0f}g carbs", "#8A7CF0"),
    ]

    colours = ["#E4572E", "#E9B44C", "#4EA8A0"]
    bars = [progress_bar(label, t[k], float(targets[k] or 0), unit, colours[i])
            for i, (k, label, unit) in enumerate(MACROS)]
    cap = float(target_budget or 0)
    if cap > 0:
        bars.append(progress_bar("Spend", t["price"], cap, "$ spent", "#8A7CF0"))

    cats = [label for _, label, _ in MACROS]
    pct = [min(t[k] / max(float(targets[k] or 0), 1) * 100, 150) for k, _, _ in MACROS]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your plate", x=cats, y=pct, marker=dict(color=colours),
                         text=[f"{v:.0f}%" for v in pct], textposition="outside",
                         hovertemplate="%{x}: %{y:.0f}% of target<extra>Your plate</extra>"))
    fig.add_trace(go.Bar(name="Target", x=cats, y=[100, 100, 100],
                         marker=dict(color="#39465B"),
                         hovertemplate="%{x}: 100%<extra>Target</extra>"))
    fig.update_layout(barmode="group", title="Progress toward your targets  ·  % of target")
    fig.update_yaxes(title="% of target", range=[0, 165], ticksuffix="%")
    fig = base_fig(fig, 300, showlegend=True)

    picks, msg = recommend_next(qty_map, targets, target_budget)
    if msg:
        rec = html.Div([html.H3("🎯  Your next order"), html.P(msg, className="rec-lead")])
    else:
        room = cap - t["price"]
        cards = []
        for p in picks:
            cards.append(html.Div(className="rec-card", children=[
                html.Div(className="rec-item", children=p["item"]),
                html.Div(className="rec-meta", children=[
                    money(p["price"], 2), "  ·  closes ",
                    f"{p['fit'] * 100:.0f}%", " of the remaining gap",
                ]),
                html.Div(className="rec-detail", children=p["detail"]),
            ]))
        rec = html.Div([
            html.H3("🎯  Your next order"),
            html.P(f"With {money(room, 2)} left under your cap, these portions close the "
                   f"biggest share of your remaining macro gaps:", className="rec-lead"),
            html.Div(className="rec-cards", children=cards),
        ])

    headline, kicker, table = drink_advice(df, t, target_budget)
    drink = html.Div([
        html.H3("🍹  The drink question"),
        html.P(headline, className="drink-headline"),
        html.P(kicker),
        table,
        html.P("Cost and share figures come from the sales data; calories are illustrative estimates.",
               className="pick-foot"),
    ])
    return kpis, bars, fig, rec, drink


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
