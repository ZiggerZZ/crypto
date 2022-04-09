import dash
from dash import html
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import date, datetime
import glob
import os

START_TIMESTAMP = 1609459200000  # 2021-01-01 00:00
END_TIMESTAMP = 1640995200000  # 2021-01-01 00:00

app = dash.Dash()

path = r'data/'
all_files = glob.iglob(os.path.join(path, "*.csv"))

df_from_each_file = (pd.read_csv(f, skiprows=1)[['unix', 'date', 'symbol', 'open']] for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)
# df = df[df.unix >= START_TIMESTAMP]
# df = df[df.unix < END_TIMESTAMP]



# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

fig = px.line(df, x="date", y="open", color="symbol")

app.layout = html.Div(children=[
    html.H1(children='Crypto Zigfrid'),

    html.Div(children='''
        All prices are in USDT.
    '''),

    dcc.Graph(
        id='graph-with-data',
        figure=fig
    ),

    dcc.Dropdown(
        ['BTC', 'ETH', 'LTC', 'DOGE', 'NEO', 'BNB', 'XRP', 'LINK', 'EOS', 'TRX', 'ETC', 'XLM', 'ZEC', 'ADA', 'QTUM', 'DASH', 'XMR', 'BTT'],
        ['BTC'],
        multi=True,
        id='selected-currencies'
    ),

    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=date(2017, 8, 17),
        max_date_allowed=date(2022, 4, 9),
        start_date=date(2021, 1, 1),
        end_date=date(2022, 1, 1)
    ),
])


# @app.callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

@app.callback(
    Output('graph-with-data', 'figure'),
    Input('selected-currencies', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_figure(selected_currencies, start_date, end_date):
    print(start_date, end_date)
    filtered_df = df[df.symbol.isin([s + "/USDT" for s in selected_currencies])]
    if start_date:
        filtered_df = filtered_df[df.date >= start_date]
    if end_date:
        filtered_df = filtered_df[df.date < end_date]

    fig = px.line(filtered_df, x="date", y="open", color="symbol")

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)