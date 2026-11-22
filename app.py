from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ALL, dcc, html, ctx, no_update

ROOT = Path(__file__).resolve().parent
menu = pd.read_csv(ROOT / 'data/menu_items.csv').fillna({'pieces': 0})
nutrition = pd.read_csv(ROOT / 'data/nutrition_estimates.csv').set_index('item')
FEE = 45.0
CATS = ['appetizer', 'nigiri', 'sashimi', 'rolls', 'chef sets', 'drinks', 'dessert']
GROUP = {'side':'appetizer','nigiri':'nigiri','sashimi':'sashimi','roll':'rolls','omakase':'chef sets','drink':'drinks','dessert':'dessert'}
COLORS = ['#d92727','#f28c28','#111111','#e8b84b','#8c2020','#6f8a56','#d45d35']
app = Dash(__name__, assets_folder='assets', title='Sushi House AYCE')
server = app.server

def money(v): return f'${v:,.2f}'
def item_rows(cat):
    return [html.Div(className='menu-row', children=[html.Div([html.Span(r.item,className='dish'), html.Small(f"{int(r.pieces) if r.pieces else '1'} pc portion · menu value ${r.price:.2f}",className='dish-note')]), dcc.Input(id={'type':'order-qty','item':r.item},type='number',min=0,max=30,step=1,value=0,className='order-input',debounce=True)]) for r in menu[menu.category.map(GROUP)==cat].itertuples()]

app.layout = html.Main(className='app', children=[
    html.Header(className='masthead',children=[html.Div('🍣  SUSHI HOUSE',className='brand'),html.Div('ALL YOU CAN EAT · ONE PRICE',className='mast-note'),html.Div([html.Small('DINNER · PER PERSON'),html.Strong('$45',className='fee')],className='fee-stamp')]),
    html.Section(className='intro',children=[html.Div('ORDER SHEET  /  01',className='eyebrow'),html.H1('The all-you-can-eat\n sushi challenge.'),html.P('Build your order, send it to the kitchen, then see how your choices stack up.')]),
    dcc.Store(id='submitted-order',data={}),
    dcc.Tabs(id='tabs',value='build',className='tabs',children=[
        dcc.Tab(label='Build Your Plate',value='build',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE MENU · WRITE YOUR QUANTITIES',className='eyebrow'),html.H2('What can we make for you?'),html.P('Enter the number of portions beside each dish. The listed à la carte values are for the buffet comparison.')]),html.Div(className='paper-menu',children=[html.Div(className='menu-top',children=[html.Strong('SUSHI HOUSE'),html.Span('AYCE DINNER MENU  ·  $45 / PERSON')]),*[html.Section(className='menu-section',children=[html.H3(cat.upper()),*item_rows(cat)]) for cat in CATS],html.Div(className='menu-submit',children=[html.Div(id='order-summary',children='0 portions selected'),html.Button('Send to Kitchen  →',id='send-order',n_clicks=0,className='send-button')]),html.Div(id='send-message',className='send-message')])])),
        dcc.Tab(label='Did You Beat the Buffet?',value='beat',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE CHECK',className='eyebrow'),html.H2('Did your order beat the buffet?'),html.P('À la carte value estimates and restaurant ingredient cost are calculated per portion from the supplied data.')]),html.Div(id='beat-content') ])),
        dcc.Tab(label='Track Your Macros',value='macros',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE FUEL',className='eyebrow'),html.H2('Where did your plate go?'),html.P('Estimated nutrition for your submitted order. Nutrition values are illustrative estimates from the dataset.')]),html.Div(id='macro-content') ])),
        dcc.Tab(label='Build Your Next Strategy',value='strategy',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE GAME PLAN',className='eyebrow'),html.H2('Choose your buffet persona.'),html.P('Get a suggested order based on what you want to optimize.')]),dcc.RadioItems(id='persona',options=[{'label':x,'value':x} for x in ['Gym Bro','Rice Dodger','DIY Omakase','Rookie']],value='Gym Bro',inline=True,className='personas'),html.Div(id='strategy-content')]))
    ]),html.Footer('Menu values, restaurant COGS and nutrition are estimates based on the supplied sushi dataset. Flat buffet fee: $45 per person.')
])

@app.callback(Output('order-summary','children'),Input({'type':'order-qty','item':ALL},'value'))
def summary(qtys): return f'{sum(int(q or 0) for q in qtys)} portions selected'

@app.callback(Output('submitted-order','data'),Output('send-message','children'),Input('send-order','n_clicks'),State({'type':'order-qty','item':ALL},'id'),State({'type':'order-qty','item':ALL},'value'),prevent_initial_call=True)
def submit(n,ids,qtys):
    order={i['item']:int(q or 0) for i,q in zip(ids,qtys) if int(q or 0)>0}
    return order, f'✓  Kitchen ticket sent · {sum(order.values())} portions'

def ordered_rows(order):
    rows=[]
    for name,q in (order or {}).items():
        r=menu[menu.item==name].iloc[0]
        rows.append((name,q,r))
    return rows

@app.callback(Output('beat-content','children'),Input('submitted-order','data'))
def beat(order):
    rows=ordered_rows(order); totalval=sum(float(r.price)*q for _,q,r in rows); cogs=sum(float(r.median_cogs)*q for _,q,r in rows)
    table=html.Table([html.Thead(html.Tr([html.Th(x) for x in ['Item','Qty','À la carte value','Restaurant COGS','Item margin']])),html.Tbody([html.Tr([html.Td(name),html.Td(q),html.Td(money(r.price*q)),html.Td(money(r.median_cogs*q)),html.Td(money((r.price-r.median_cogs)*q),className='positive' if r.price>=r.median_cogs else 'negative')]) for name,q,r in rows] or [html.Tr(html.Td('Send an order from Build Your Plate to see your results.',colSpan=5))])])
    diff=totalval-FEE; restaurant=FEE-cogs
    return html.Div([html.Div(className='table-wrap',children=table),html.Div(className='score-grid',children=[html.Div([html.Small('À LA CARTE VALUE'),html.Strong(money(totalval))]),html.Div([html.Small('BUFFET FEE'),html.Strong(money(FEE))]),html.Div([html.Small('YOUR BUFFET RESULT'),html.Strong(('You gained ' if diff>=0 else 'You left ')+money(abs(diff)),className='positive' if diff>=0 else 'negative')]),html.Div([html.Small('RESTAURANT PROFIT / (LOSS)'),html.Strong(money(restaurant),className='positive' if restaurant>=0 else 'negative')])]),html.P('Buffet result = à la carte value minus $45. Restaurant profit estimate = $45 fee minus ingredient COGS.',className='fine-print')])

@app.callback(Output('macro-content','children'),Input('submitted-order','data'))
def macros(order):
    rows=ordered_rows(order); totals={k:0 for k in ['calories','protein_g','carbs_g','fat_g']}; names=[]; vals=[]
    for name,q,r in rows:
        n=nutrition.loc[name]
        for k in totals: totals[k]+=float(n[k])*q
        names.append(name); vals.append(float(n.calories)*q)
    colors=COLORS[:len(names)] or ['#eee']
    pie=go.Figure(go.Pie(labels=names,values=vals,hole=.56,marker={'colors':colors},textinfo='label+percent',hovertemplate='%{label}<br>%{value:.0f} kcal<extra></extra>'))
    pie.update_layout(title='Estimated calories by dish',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#171717'},margin={'t':55,'b':10,'l':10,'r':10},height=420)
    stats=html.Div(className='macro-stats',children=[html.Div([html.Small(k.replace('_g','').upper()),html.Strong(f"{v:,.0f}{' g' if k!='calories' else ' kcal'}")]) for k,v in totals.items()])
    return html.Div([stats,html.Div(className='macro-layout',children=[dcc.Graph(figure=pie,config={'displayModeBar':False}),html.Div(className='source-list',children=[html.H3('Macro sources by dish'),html.Table([html.Thead(html.Tr([html.Th('Dish'),html.Th('Qty'),html.Th('Protein'),html.Th('Carbs'),html.Th('Fat')])),html.Tbody([html.Tr([html.Td(name),html.Td(q),*[html.Td(f'{float(nutrition.loc[name][k])*q:.0f} g') for k in ['protein_g','carbs_g','fat_g']]]) for name,q,r in rows] or [html.Tr(html.Td('No submitted order yet.',colSpan=5))])])])])])

@app.callback(Output('strategy-content','children'),Input('persona','value'))
def strategy(persona):
    candidates=menu.copy()
    if persona=='Gym Bro':
        candidates=candidates.merge(nutrition.reset_index(),on='item').sort_values('protein_g',ascending=False).head(5); detail='Protein-forward picks with a mix of rolls, nigiri and sashimi.'
    elif persona=='Rice Dodger':
        candidates=candidates[~candidates.item.str.contains('Roll|Nigiri|Omakase',case=False)].sort_values('median_cogs',ascending=False).head(5); detail='Rice-free picks ranked by estimated ingredient cost per portion.'
    elif persona=='DIY Omakase':
        candidates=pd.concat([menu[menu.category=='sashimi'].head(1),menu[menu.category=='nigiri'].head(2),menu[menu.category=='roll'].head(1),menu[menu.category=='side'].head(1)]); detail='A chef-style progression: sashimi, nigiri, a roll and a small side.'
    else:
        candidates=menu.merge(nutrition.reset_index(),on='item')
        candidates['fill_per_cost']=candidates['calories']/candidates['median_cogs'].clip(lower=.01)
        candidates=candidates.sort_values(['fill_per_cost','median_cogs'],ascending=[False,True]).head(5)
        detail='Filling calorie estimates per dollar of ingredient cost, with lower-cost picks favored.'
    return html.Div(className='strategy-card',children=[html.H3(persona),html.P(detail),html.Ul([html.Li(f'{r.item}  ·  ${r.median_cogs:.2f} estimated COGS · ${r.price:.2f} menu value') for r in candidates.itertuples()])])

if __name__=='__main__': app.run(debug=False,host='0.0.0.0')
