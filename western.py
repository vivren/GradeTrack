import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re
from app import app, df
from models import School, Course, Mark, db

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
print(df)

western_layout = html.Div([
    html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Western',
            style={
                'textAlign': 'center',
                'color': colors['text']
            })
    ]),

    html.Div([
        html.H3(
            children="Filter Data",
        ),

        dcc.Checklist(["1st Year", "2nd Year", "3rd Year", "4th Year"], id="courseYearFilter"),

        dcc.Dropdown(["course 1", "course2"], id="courseNameFilter", multi=True),

        html.Button("Filter Courses", id="filterButton", n_clicks=0)
    ]),


    html.Div([
        html.H3(
            children="Add Mark"
        ),

        html.Div(id="schoolInput"),

        dcc.Input(
            id="courseInput",
            placeholder="Enter course code",
            value="",
            style={"padding": 10}
        ),

        dcc.Input(
            id="gradeInput",
            placeholder="Enter course code",
            value='',
            style={"padding": 10}
        ),

        html.Button("Add Mark", id="addMarkButton", n_clicks=0),

        html.Button("Clear Input", id="Clear input button", n_clicks=0)],
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='gradesTable', children=[
        dash_table.DataTable(
            id="westernTable",
            columns=[{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns[1:]],
            data=df.loc[df["name"] == "University of Western Ontario"].to_dict('records'),
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
        ),
    ]),
    dcc.Graph(id="westernGraph"),

    html.Div()

])

@app.callback(
    Output("westernTable", "data"),
    Output("filterButton", "n_clicks"),
    Input("filterButton", "n_clicks"),
    Input("westernTable", "data"),
    Input("courseYearFilter", "value"),
)
def filterData(filterClicks, data, courseFilter):
    if filterClicks > 0:
        #filteredData = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).filter_by(yearLevel=courseYear[0]).all()
        filteredData = db.session.query(Course.courseCode, Course.yearLevel).filter_by(yearLevel=1).all()
        print(filteredData)
        df = pd.DataFrame(filteredData)
        return df, 0
    return data, 0

@app.callback(
    Output("westernGraph", "figure"),
    Input("westernTable", "data"),
    )
def display_graph(data):
    df = pd.DataFrame(data)
        # df.columns = ['name', 'courseCode', 'mark']
    fig = px.box(df, x="courseCode", y="mark", labels={"courseCode": "Course Name", "mark": "Final Course Marks"})
    return fig
