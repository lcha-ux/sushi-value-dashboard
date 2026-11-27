from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ALL, dcc, html, ctx

ROOT = Path(__file__).resolve().parent
menu = pd.read_csv(ROOT / 'data/menu_items.csv').fillna({'pieces': 0})
nutrition = pd.read_csv(ROOT / 'data/nutrition_estimates.csv').set_index('item')
CATS = ['appetizer', 'nigiri', 'sashimi', 'rolls', 'chef sets', 'drinks', 'dessert']
GROUP = {'side':'appetizer','nigiri':'nigiri','sashimi':'sashimi','roll':'rolls','omakase':'chef sets','drink':'drinks','dessert':'dessert'}
COLORS = ['#d92727','#f28c28','#111111','#e8b84b','#8c2020','#6f8a56','#d45d35']
app = Dash(__name__, assets_folder='assets', title="Group 3's AYCE Sushi")
server = app.server

def money(v): return f'${v:,.2f}'
FOOD_IMAGES = {
    'gyoza': 'https://imgfp.hotp.jp/IMGH/02/96/P044000296/P044000296_480.jpg',
    'edamame': 'https://images.unsplash.com/photo-1515543904379-3d7577cd1ec5?auto=format&fit=crop&w=800&q=80',
    'miso': 'https://ichibansushi.co.id/wp-content/uploads/2023/06/MISO-SOUP-2-600x600.jpg',
    'sashimi': 'https://images.rawpixel.com/image_social_landscape/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDI0LTA3L3Jhd3BpeGVsX29mZmljZV8zNF9waG90b19vZl9zYXNoaW1pX29mX3NsaWNlZF9taXhlZF9maXNoX3NlcnZlZF9fMzQ0NTA5MTAtODU5MS00M2RiLWFmYzQtZDU2N2NjMmExYTE4XzEuanBn.jpg',
    'nigiri': 'https://cdn.yosushi.com/r/w-1260/YoSushi/files/e3/e3d220d8-f6a4-4c67-bd42-0a85ad0206a7.639110271220000000.png',
    'roll': 'https://images.deliveryhero.io/image/global-menu-service/TB_AE/vendor/44424/PRODUCT/8850e126-4dd8-4b42-a487-5f4e3a9aa769.jpg',
}
ROLL_INGREDIENTS = {
    'Truffle Salmon Roll': 'Salmon · avocado · cucumber · truffle · rice · nori',
    'Rainbow Roll': 'Crab · avocado · cucumber · assorted fish · rice · nori',
    'Dragon Roll': 'Eel · avocado · cucumber · eel sauce · rice · nori',
    'Spicy Tuna Roll': 'Tuna · spicy mayo · cucumber · rice · nori',
    'California Roll': 'Crab · avocado · cucumber · rice · nori',
}
def image_for(row):
    if row.category == 'side':
        return FOOD_IMAGES['gyoza'] if row.item.startswith('Gyoza') else FOOD_IMAGES['edamame'] if row.item == 'Edamame' else FOOD_IMAGES['miso']
    if row.category == 'sashimi': return FOOD_IMAGES['sashimi']
    if row.category == 'roll':
        if row.item == 'Dragon Roll': return 'https://schoolofsushi.com/wp-content/uploads/2023/02/dragon-roll-sushi.jpg'
        if row.item == 'Spicy Tuna Roll': return 'https://t0.gstatic.com/images?q=tbn%3AANd9GcR0_qI-pKlNaxrXorgs5SARRhuS3eOv3gogy5aWKI8ADFH9jFm1'
        return FOOD_IMAGES['roll']
    if row.category == 'nigiri':
        if row.item == 'Tuna Nigiri (2pc)': return 'https://rimage.gnst.jp/rest/img/cza83yrm0000/s_0n7e.jpg?t=1779440824'
        return FOOD_IMAGES['nigiri']
    return None

def item_rows(cat):
    cards=[]
    for r in menu[menu.category.map(GROUP)==cat].itertuples():
        img=image_for(r)
        pieces=int(r.pieces) if r.pieces else 1
        detail = f'{pieces} pc portion'
        if r.category == 'roll': detail = '8 pc roll'
        ingredients = ROLL_INGREDIENTS.get(r.item, {'Gyoza (6pc)':'Pork · cabbage · ginger · dumpling wrapper','Edamame':'Steamed soybeans · sea salt','Miso Soup':'Miso · tofu · wakame · scallion','Sashimi Platter (10pc)':'Chef-selected sliced fish','Tuna Nigiri (2pc)':'Tuna · seasoned sushi rice','Salmon Nigiri (2pc)':'Salmon · seasoned sushi rice','Yellowtail Nigiri (2pc)':'Yellowtail · seasoned sushi rice'}.get(r.item, ''))
        cards.append(html.Article(className='menu-card',children=[html.Div(className='dish-photo-wrap',children=[html.Img(src=img,alt=r.item,className='dish-photo')]) if img else html.Div(className='dish-photo-wrap photo-placeholder',children='🍣'),html.Div(className='card-info',children=[html.Div(className='card-name',children=[html.Strong(r.item),html.Small(detail)]),html.Small(ingredients,className='ingredients')]),html.Button('+',id={'type':'add-item','item':r.item},n_clicks=0,className='add-button',title=f'Add {r.item}',**{'aria-label':f'Add {r.item}'})]))
    return cards

def cart_contents(order):
    if not order: return html.P('Tap + beside a dish to start your order.',className='cart-empty')
    children=[]
    for name,qty in order.items():
        row=menu[menu.item==name].iloc[0]
        img=image_for(row)
        children.append(html.Div(className='cart-row',children=[html.Img(src=img,alt='') if img else html.Div(className='cart-thumb-placeholder',children='🍣'),html.Div(className='cart-item-copy',children=[html.Strong(name),html.Small(f'Qty {qty}')]),html.Span(f'× {qty}',className='cart-qty')]))
    return children

app.layout = html.Main(className='app', children=[
    html.Header(className='masthead',children=[html.Div("🍣  Group 3's AYCE Sushi",className='brand'),html.Div('ALL YOU CAN EAT · ONE PRICE',className='mast-note'),html.Div([html.Small('PER PERSON'),html.Strong('$45',id='fee-display',className='fee')],className='fee-stamp')]),
    html.Section(className='intro',children=[html.Div('01 / Order Sheet',className='eyebrow'),html.H1('All You Can Eat Sushi'),html.P('How can a diner “beat” AYCE sushi?')]),
    dcc.Store(id='draft-order',data={}),dcc.Store(id='submitted-order',data={}),
    dcc.Tabs(id='tabs',value='build',className='tabs',children=[
        dcc.Tab(label='Build Your Plate',value='build',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE MENU · BUILD YOUR ORDER',className='eyebrow'),html.H2('What can we make for you?'),html.P('Build a plate from the menu, one dish at a time.')]),html.Div(className='price-control',children=[html.Label('BUFFET PRICE TO BEAT · PER PERSON'),dcc.Input(id='buffet-price',type='number',min=0,step=0.5,value=45,className='price-input')]),html.Div(className='paper-menu',children=[html.Div(className='menu-top',children=[html.Strong("GROUP 3'S AYCE SUSHI"),html.Span('AYCE MENU  ·  $45 / PERSON',id='menu-fee')]),html.Div(className='menu-order-layout',children=[html.Div(className='menu-sections',children=[html.Section(className='menu-section',children=[html.H3(cat.upper()),html.Div(className='dish-grid',children=item_rows(cat))]) for cat in CATS]),html.Aside(className='order-cart',children=[html.Div(className='cart-header',children=[html.H3('Your Order'),html.Div(id='order-summary',children='0 portions')]),html.Div(id='cart-items',children=cart_contents({})),html.Button('Clear Order',id='clear-order',n_clicks=0,className='clear-button'),html.Button('Send Order to Kitchen  →',id='send-order',n_clicks=0,className='send-button'),html.Div(id='send-message',className='send-message')])])])])),
        dcc.Tab(label='Did You Beat the Buffet?',value='beat',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE CHECK',className='eyebrow'),html.H2('Did your order beat the buffet?'),html.P('À la carte value estimates and restaurant ingredient cost are calculated per portion from the supplied data.')]),html.Div(id='beat-content') ])),
        dcc.Tab(label='Track Your Macros',value='macros',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE FUEL',className='eyebrow'),html.H2('Where did your plate go?'),html.P('Estimated nutrition for your submitted order. Nutrition values are illustrative estimates from the dataset.')]),html.Div(id='macro-content') ])),
        dcc.Tab(label='Build Your Next Strategy',value='strategy',className='tab',selected_className='tab-on',children=html.Div(className='page',children=[html.Div(className='page-title',children=[html.Div('THE GAME PLAN',className='eyebrow'),html.H2('Choose your buffet persona.'),html.P('Get a suggested order based on what you want to optimize.')]),dcc.RadioItems(id='persona',options=[{'label':x,'value':x} for x in ['Gym Bro','Rice Dodger','DIY Omakase','Rookie']],value='Gym Bro',inline=True,className='personas'),html.Div(id='strategy-content')]))
    ]),html.Footer('Restaurant COGS and nutrition are estimates based on the supplied sushi dataset. The buffet price is set by you.')
])

@app.callback(Output('fee-display','children'),Output('menu-fee','children'),Input('buffet-price','value'))
def show_price(price):
    fee=max(0,float(price or 0))
    return money(fee),f'AYCE MENU  ·  {money(fee)} / PERSON'

@app.callback(Output('draft-order','data'),Input({'type':'add-item','item':ALL},'n_clicks'),Input('clear-order','n_clicks'),State('draft-order','data'),prevent_initial_call=True)
def update_order(add_clicks,clear_clicks,order):
    order=dict(order or {})
    triggered=ctx.triggered_id
    if triggered == 'clear-order': return {}
    if not isinstance(triggered,dict): return order
    item=triggered['item']
    order[item]=order.get(item,0)+1
    return order

@app.callback(Output('order-summary','children'),Output('cart-items','children'),Input('draft-order','data'))
def render_cart(order):
    count=sum((order or {}).values())
    return f'{count} portions',cart_contents(order)

@app.callback(Output('submitted-order','data'),Output('send-message','children'),Input('send-order','n_clicks'),State('draft-order','data'),prevent_initial_call=True)
def submit(n,order):
    count=sum((order or {}).values())
    if not count: return {},'Add a dish to your order before sending it to the kitchen.'
    return dict(order),f'✓  Kitchen ticket sent · {count} portions'

def ordered_rows(order):
    rows=[]
    for name,q in (order or {}).items():
        r=menu[menu.item==name].iloc[0]
        rows.append((name,q,r))
    return rows

@app.callback(Output('beat-content','children'),Input('submitted-order','data'),Input('buffet-price','value'))
def beat(order,price):
    fee=max(0,float(price or 0))
    rows=ordered_rows(order); totalval=sum(float(r.price)*q for _,q,r in rows); cogs=sum(float(r.median_cogs)*q for _,q,r in rows)
    table=html.Table([html.Thead(html.Tr([html.Th(x) for x in ['Item','Qty','À la carte value','Restaurant COGS','Item margin']])),html.Tbody([html.Tr([html.Td(name),html.Td(q),html.Td(money(r.price*q)),html.Td(money(r.median_cogs*q)),html.Td(money((r.price-r.median_cogs)*q),className='positive' if r.price>=r.median_cogs else 'negative')]) for name,q,r in rows] or [html.Tr(html.Td('Send an order from Build Your Plate to see your results.',colSpan=5))])])
    diff=totalval-fee; restaurant=fee-cogs
    return html.Div([html.Div(className='table-wrap',children=table),html.Div(className='score-grid',children=[html.Div([html.Small('À LA CARTE VALUE'),html.Strong(money(totalval))]),html.Div([html.Small('BUFFET FEE'),html.Strong(money(fee))]),html.Div([html.Small('YOUR BUFFET RESULT'),html.Strong(('You gained ' if diff>=0 else 'You left ')+money(abs(diff)),className='positive' if diff>=0 else 'negative')]),html.Div([html.Small('RESTAURANT PROFIT / (LOSS)'),html.Strong(money(restaurant),className='positive' if restaurant>=0 else 'negative')])]),html.P(f'Buffet result = à la carte value minus {money(fee)}. Restaurant profit estimate = buffet fee minus ingredient COGS.',className='fine-print')])

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
