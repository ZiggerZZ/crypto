import dash
from dash import html
import plotly.express as px
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import date, datetime
import glob
import os

# START_TIMESTAMP = 1609459200000  # 2021-01-01 00:00
# END_TIMESTAMP = 1640995200000  # 2021-01-01 00:00

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

path = r'data/'
all_files = glob.iglob(os.path.join(path, "*.csv"))


def pct_change(df):
    df = df[::-1]
    df['pct_change'] = df.open.pct_change()
    return df


df_from_each_file = (pct_change(pd.read_csv(f, skiprows=1)[['unix', 'date', 'symbol', 'open']]) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)
# df = df[df.unix >= START_TIMESTAMP]
# df = df[df.unix < END_TIMESTAMP]


fig1 = px.line(df, x="date", y="open", color="symbol")
fig2 = px.line(df, x="date", y="pct_change", color="symbol")

app.layout = html.Div(children=[
    html.H1(children='Crypto Zigfrid'),

    html.Div(children='''
        All prices are in USDT.
    '''),

    dcc.Graph(
        id='graph-with-data',
        figure=fig1
    ),

    dcc.Graph(
        id='graph-percent-change',
        figure=fig2
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

@app.callback(
    Output('graph-with-data', 'figure'),
    Output('graph-percent-change', 'figure'),
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

    fig2 = px.line(filtered_df, x="date", y="pct_change", color="symbol")

    fig2.update_layout(transition_duration=500)

    return fig, fig2


if __name__ == '__main__':
    app.run_server(debug=False)
