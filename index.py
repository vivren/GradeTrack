import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re

from home import home_layout
from western import western_layout
from app import app
from models import School, Course, Mark, db

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
}

selectedTabStyle = {
    "background": '#7FDBFF',
    'color': 'white',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding':'6px'
}

app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Home", tab_id="homeTab", active_tab_style = selectedTabStyle, labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Western", tab_id="UniversityofWesternOntarioTab", active_tab_style = selectedTabStyle, labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
            ],
            id="tabs",
            active_tab="homeTab",
        ),
    ], className="mt-3"
)

app.layout = html.Div([
    html.Div(children=[
        html.H1(
            children='GradeTrack',
        )
    ]),

    html.Div(children="View Your School Course Averages", style={
    }),

    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),

    html.Div(id='content', children=[]),
    ], style={'backgroundColor': colors['background'], "color": colors['text'], "textAlign": "center", "font-family": 'Trebuchet MS'})


@app.callback(
    Output("content", "children"),
    Input("tabs", "active_tab"),
)
def switch_tab(tab_chosen):
    if tab_chosen == "homeTab":
        return home_layout
    elif tab_chosen == "UniversityofWesternOntarioTab":
        return western_layout


if __name__ == '__main__':
    app.run_server(debug=True)
