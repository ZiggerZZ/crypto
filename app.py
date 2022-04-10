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

TIME_PERIOD = 30  # let's monitor TIME_PERIOD days


def standard_score(series):
    return (series - series.mean()) / series.std()


def add_features(df):
    df = df[::-1]
    df['pct_change'] = df.open.pct_change()
    df['rolling_pct_change'] = df['pct_change'].rolling(TIME_PERIOD).sum() / TIME_PERIOD
    # Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements.
    df['std_deviation'] = df['open'].rolling(TIME_PERIOD).std(ddof=0)
    df['sharpe_score'] = df['rolling_pct_change'] / df['std_deviation']
    df['standard_score'] = standard_score(df.open)
    return df


ROWS_TO_KEEP = ['unix', 'date', 'symbol', 'open']
# dict {name: df}
currencies = {f[:-10].split('_')[1]: pd.read_csv(f, skiprows=1)[ROWS_TO_KEEP] for f in all_files}

df_from_each_file = (add_features(df_currency) for df_currency in currencies.values())
df = pd.concat(df_from_each_file, ignore_index=True)


df_open = [df_currency.open.rename(currency) for currency, df_currency in currencies.items()]
df_open.append(currencies['BTC'].date)
df_correlation = pd.concat(df_open, axis=1)

corr_matrix = df_correlation.drop(['date'], axis=1).corr().round(2)

fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto")
fig1 = px.line(df, x="date", y="open", color="symbol")
fig2 = px.line(df, x="date", y="pct_change", color="symbol")
fig3 = px.line(df, x="date", y="standard_score", color="symbol")
fig4 = px.line(df, x="date", y="rolling_pct_change", color="symbol")
fig5 = px.line(df, x="date", y="sharpe_score", color="symbol")

app.layout = html.Div(children=[
    html.H1(children='Crypto Zigfrid'),

    html.Div([html.Img(src="https://alternative.me/crypto/fear-and-greed-index.png")],
             style={'textAlign': 'center'}),
    dcc.Dropdown(
        ['BTC', 'ETH', 'LTC', 'DOGE', 'NEO', 'BNB', 'XRP', 'LINK', 'EOS', 'TRX', 'ETC', 'XLM', 'ZEC', 'ADA', 'QTUM',
         'DASH', 'XMR', 'BTT'],
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

    dcc.Graph(
        id="graph-corr",
        figure=fig_corr
    ),

    html.Div(children='''
        All prices are in USDT.
    '''),
    html.H2(children='Opening price by date'),
    dcc.Graph(
        id='graph-with-data',
        figure=fig1
    ),
    html.H2(children='Daily return'),
    dcc.Graph(
        id='graph-percent-change',
        figure=fig2
    ),
    html.H2(children='Standard score (Y_t - mean)/std'),
    dcc.Graph(
        id='graph-standard-score',
        figure=fig3
    ),
    html.H2(children=f'Mean rolling return over {TIME_PERIOD} days'),
    dcc.Graph(
        id='graph-rolling-percent-change',
        figure=fig4
    ),
    html.H2(children=f'Sharpe score (mean rolling return / rolling std)'),
    dcc.Graph(
        id='graph-sharpe-score',
        figure=fig5
    ),
])


def calc_standard_score(df, start_date, end_date):
    df = df[::-1]
    if start_date:
        df = df[df.date >= start_date]
    if end_date:
        df = df[df.date < end_date]
    df['standard_score'] = standard_score(df.open)
    return df


def prepare_df(selected_currencies, start_date, end_date):
    df_from_each_file = (calc_standard_score(currencies[currency], start_date, end_date) for currency in selected_currencies)
    df = pd.concat(df_from_each_file, ignore_index=True)
    return df


@app.callback(
    Output('graph-with-data', 'figure'),
    Output('graph-percent-change', 'figure'),
    Output('graph-standard-score', 'figure'),
    Output('graph-rolling-percent-change', 'figure'),
    Output('graph-sharpe-score', 'figure'),
    Input('selected-currencies', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_figure(selected_currencies, start_date, end_date):

    filtered_df = df[df.symbol.isin([s + "/USDT" for s in selected_currencies])]
    if start_date:
        filtered_df = filtered_df[df.date >= start_date]
    if end_date:
        filtered_df = filtered_df[df.date < end_date]

    fig1 = px.line(filtered_df, x="date", y="open", color="symbol")
    fig1.update_layout(transition_duration=500)

    fig2 = px.line(filtered_df, x="date", y="pct_change", color="symbol")
    fig2.update_layout(transition_duration=500)

    fig3 = px.line(prepare_df(selected_currencies, start_date, end_date), x="date", y="standard_score", color="symbol")
    fig3.update_layout(transition_duration=500)

    fig4 = px.line(filtered_df, x="date", y="rolling_pct_change", color="symbol")
    fig4.update_layout(transition_duration=500)

    fig5 = px.line(filtered_df, x="date", y="sharpe_score", color="symbol")
    fig5.update_layout(transition_duration=500)

    return fig1, fig2, fig3, fig4, fig5


if __name__ == '__main__':
    app.run_server(debug=False)
