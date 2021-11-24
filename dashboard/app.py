from dotenv import dotenv_values
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('dashboard/assets/cgm48members.csv')


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([
                html.Th(col) for col in dataframe.columns
            ])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto'})


app.layout = html.Div(children=[
    html.H1(children='CGM48 Real-Time Social Listening',
            style={'textAlign': 'center'}),

    html.H5(children='Immediate analytics for all influencers',
            style={'textAlign': 'center'}),

    html.Hr(),

    generate_table(df)
])


if __name__ == '__main__':
    app.run_server(debug=True)
