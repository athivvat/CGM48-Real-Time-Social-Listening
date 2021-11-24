from dotenv import dotenv_values
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('dashboard/assets/cgm48members.csv')


def generate_table(dataframe, max_rows=48):
    headers = []
     # Add image column
    headers.append(html.Th(""))

     # Add column headers
    for col in dataframe.columns:
        if col not in ['Facebook Link', 'Instagram Link']:
            headers.append(html.Th(col))

    return html.Table([
        html.Thead(
            html.Tr(headers)
        ),
        html.Tbody([
            html.Tr([
                html.Td(html.Img(src='assets/images/' + dataframe.iloc[i]['Nickname'].lower() +'.jpg', width=70, height=70, style={'borderRadius': '50%'})),
                html.Td(dataframe.iloc[i]['Name']),
                html.Td(dataframe.iloc[i]['Nickname']),
                html.Td(dataframe.iloc[i]['Age']),
                html.Td(html.A(children=dataframe.iloc[i]['Facebook'], href=dataframe.iloc[i]['Facebook Link'], target="_blank")),
                html.Td(html.A(children=dataframe.iloc[i]['Instagram'], href=dataframe.iloc[i]['Instagram Link'], target="_blank")),
                html.Td(dataframe.iloc[i]['Twitter Volume']),
                html.Td(dataframe.iloc[i]['Favorites']),
                html.Td(dataframe.iloc[i]['Retweets']),
                html.Td(dataframe.iloc[i]['Engagement Rate']),
                html.Td(dataframe.iloc[i]['Sentiment']),
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto'})


app.layout = html.Div(children=[
    html.H1(children='CGM48 Real-Time Social Listening',
            style={'textAlign': 'center', 'marginTop': '50px'}),

    html.H5(children='Immediate analytics for all influencers',
            style={'textAlign': 'center'}),

    html.Hr(),

    generate_table(df),

    html.P(children='Made with \u2764\ufe0f by 401 Cha-Thai', style={'textAlign': 'center', 'margin': '50px'}),
])


if __name__ == '__main__':
    app.run_server(debug=True)
