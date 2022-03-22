import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re
from app import app
from models import School, Course, Mark, db

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

home_layout = html.Div([

    html.Div([
        dcc.Dropdown(["University of Western Ontario", "University of Toronto", "York University",
                      "University of British Columbia", "University of Waterloo", "McGill University",
                      "Wilfred Laurier University", "Queens University", "University of Guelph"],
                     placeholder="Select your school", id="schoolInput"),

        dcc.Input(
            id="courseInput",
            placeholder="Enter course code",
            value="",
            style={"padding": 10}
        ),

        dcc.Input(
            id="gradeInput",
            placeholder="Enter course grade",
            value='',
            style={"padding": 10}
        ),

        html.Button("Add Mark", id="addHomeMarkButton", n_clicks=0),

        html.Button("Clear Input", id="Clear input button", n_clicks=0)],
        style={'backgroundColor': colors['background']}
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='gradesTable', children=[
        dash_table.DataTable(
            id="homeTable",
            columns=[],
            data=[],
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
        ),
    ]),
    dcc.Graph(id="homeGraph")
])
@app.callback(
    Output("homeTable", "data"),
    Output("homeTable", "columns"),
    Output("addHomeMarkButton", "n_clicks"),
    Input("tabs", "active_tab"),
    Input("addHomeMarkButton", "n_clicks"),
    Input("homeTable", "data"),
    Input("schoolInput", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
)
def updateHomeTable(activeTab, addClicks, df, schoolInput, courseInput, gradeInput):
    df = pd.DataFrame(db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).all())
    columns = [{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns]

    if addClicks > 0:
        schoolID = db.session.query(School.id).filter_by(name=schoolInput).first()
        tempSchoolID = schoolID.id

        courseExists = db.session.query(Course.id).filter_by(courseCode=courseInput, schoolID=tempSchoolID).first()
        if courseExists != None:
            tempCourseID = courseExists.id
        else:
            tempYearLevel = re.findall('\d+|$', courseInput)[0][0]
            course = Course(courseCode=courseInput, yearLevel=tempYearLevel, schoolID=tempSchoolID)
            tempCourseID = course.id
            db.session.add(course)
            db.session.commit()

        mark = Mark(mark=gradeInput, courseID=tempCourseID)
        db.session.add(mark)
        db.session.commit()
        df = df.append({"name": schoolInput, "courseCode": courseInput, "mark": gradeInput}, ignore_index=True)

    return df.to_dict('records'), columns, 0

@app.callback(
    Output("homeGraph", "figure"),
    Input("homeTable", "data"),
    )
def display_graph(data):
    df = pd.DataFrame(data)
    fig = px.box(df, x="name", y="mark", category_orders={"name": sorted(df['name'].unique())}, labels={"name": "School Name", "mark": "Final Course Marks"})
    return fig
