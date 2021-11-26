from dotenv import dotenv_values
from pymongo import MongoClient
from pathlib import Path
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import pandas as pd
from pymongo.message import query

"""LOAD ENVIRONMENT VALUES"""
path = Path().absolute()
config = dotenv_values(path.joinpath('.env'))

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
                html.Td(html.Img(src='assets/images/' + dataframe.iloc[i]['Nickname'].lower(
                ) + '.jpg', width=70, height=70, style={'borderRadius': '50%'})),
                html.Td(dataframe.iloc[i]['Name']),
                html.Td(dataframe.iloc[i]['Nickname']),
                html.Td(dataframe.iloc[i]['Age']),
                html.Td(html.A(
                    children=dataframe.iloc[i]['Facebook'], href=dataframe.iloc[i]['Facebook Link'], target="_blank")),
                html.Td(html.A(children=dataframe.iloc[i]['Instagram'],
                        href=dataframe.iloc[i]['Instagram Link'], target="_blank")),
                html.Td('#' + dataframe.iloc[i]['Hashtag']),
                html.Td(dataframe.iloc[i]['Twitter Volume'], style={
                        'textAlign': 'center'}),
                html.Td(dataframe.iloc[i]['Favorites'],
                        style={'textAlign': 'center'}),
                html.Td(dataframe.iloc[i]['Retweets'],
                        style={'textAlign': 'center'}),
                html.Td(f"{dataframe.iloc[i]['Engagement Score']}%", style={
                        'textAlign': 'center'}),
                html.Td(dataframe.iloc[i]['Sentiment']),
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto'})


def generate_summary(df, n):
    twitter_volume = df['Twitter Volume'].sum() if n > 1 else 0
    favorites = df['Favorites'].sum() if n > 1 else 0
    retweets = df['Retweets'].sum() if n > 1 else 0

    return html.Table([
        html.Thead(
            html.Tr([
                html.Th("Twitter Volume"), 
                html.Th("Favorites"), 
                html.Th("Retweets")
            ])
        ),
         html.Tbody([
            html.Tr([
                html.Td(twitter_volume, style={'textAlign': 'center', 'fontSize': '2em', 'fontWeight': 'bold'}),
                html.Td(favorites, style={'textAlign': 'center', 'fontSize': '2em', 'fontWeight': 'bold'}),
                html.Td(retweets, style={'textAlign': 'center', 'fontSize': '2em', 'fontWeight': 'bold'})
            ])
         ])
    ], style={'marginLeft': 'auto', 'marginRight': 'auto', 'marginBottom': '50px'})

app.layout = html.Div(children=[
    html.H1(children='CGM48 Real-Time Social Monitoring',
            style={'textAlign': 'center', 'marginTop': '50px'}),

    html.H5(children='Immediate analytics for all influencers',
            style={'textAlign': 'center'}),

    html.P(children='Made with \u2764\ufe0f by 401 Cha-Thai',
           style={'textAlign': 'center', 'margin': '50px'}),

    html.Hr(),

    html.H3(children='Summary', style={'textAlign': 'center'}),

    html.Div(id='live-summary-update'),

    html.Div(id='live-update'),

    dcc.Interval(
        id='interval-component-slow',
        interval=5*1000,  # in milliseconds: 5000 ms = 5 sec.
        n_intervals=0
    )
], style={'padding': '20px'})


def favorite_count(collection, hashtag):
    query_results = collection.aggregate([
        {'$match': {'hashtags': hashtag}},
        {'$group': {'_id': None, 'favorite_count': {'$sum': "favorites"}}}
    ])
    resuults = list(query_results)
    if len(resuults) > 0:
        return resuults[0]['favorite_count']
    else:
        return 0

def retweet_count(collection, hashtag):
    query_results = collection.aggregate([
        {'$match': {'hashtags': hashtag}},
        {'$group': {'_id': None, 'retweet_count': {'$sum': "retweets"}}}
    ])
    resuults = list(query_results)
    if len(resuults) > 0:
        return resuults[0]['retweet_count']
    else:
        return 0

@app.callback(
    [Output('live-summary-update', 'children')],
    [Input('interval-component-slow', 'n_intervals')]
)

def update_summary(n):
    children = [generate_summary(df, n)]
    return children


@ app.callback(
    [Output('live-update', 'children')],
    [Input('interval-component-slow', 'n_intervals')]
)
def update_table(n):
    # Loading data from MongoDB
    client = MongoClient(config['MONGODB_URI'])
    db = client.twitters
    collection = db.tweets

    for i in range(len(df)):
        twitter_volume = collection.count_documents(
            {'hashtags': df.iloc[i]['Hashtag']})
        df.at[i, 'Twitter Volume'] = twitter_volume

        df.at[i, 'Favorites'] = favorite_count(
            collection, df.iloc[i]['Hashtag'])

        df.at[i, 'Retweets'] = retweet_count(
            collection, df.iloc[i]['Hashtag'])

        if df.iloc[i]['Twitter Volume'] > 0:
            df.at[i, 'Engagement Score'] = (df.iloc[i]['Favorites'] + df.iloc[i]['Retweets']) / df.iloc[i]['Twitter Volume'] * 100
        else:
            df.at[i, 'Engagement Score'] = 0.0

    children = [generate_table(df)]
    return children


if __name__ == '__main__':
    app.run_server(debug=True)
