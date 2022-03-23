import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re
from app import app
from models import School, Faculty, Course, Mark, db

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

home_layout = html.Div([

    html.Div([
        dcc.Dropdown([],
            id="schoolInput",
            placeholder="Select your school"),

        dcc.Dropdown([],
            id="homeFacultyInput",
            placeholder="Select school to see faculties"),

        dcc.Input(
            id="homeCourseInput",
            placeholder="Enter course code",
            value="",
            style={"padding": 10}
        ),

        dcc.Input(
            id="homeGradeInput",
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
    Output("schoolInput", "options"),
    Input("tabs", "active_tab"),
)
def updateSchoolDropdown(activeTab):
    schools = db.session.query(School.name).all()
    schools = sorted([school for sublist in schools for school in sublist])
    return schools

@app.callback(
    Output("homeFacultyInput", "options"),
    Input("homeSchoolInput", "value"),
)
def updateFacultyDropdown(schoolInput):
    faculties = db.session.query(Faculty.name).filter(School.id == Faculty.schoolID).filter(School.name == schoolInput).all()
    faculties = sorted([faculty for sublist in faculties for faculty in sublist])
    return faculties

@app.callback(
    Output("homeTable", "data"),
    Output("homeTable", "columns"),
    Output("addHomeMarkButton", "n_clicks"),
    Input("tabs", "active_tab"),
    Input("addHomeMarkButton", "n_clicks"),
    Input("schoolInput", "value"),
    Input("homeFacultyInput", "value"),
    Input("homeCourseInput", "value"),
    Input("homeGradeInput", "value"),
)
def updateHomeTable(activeTab, addClicks, schoolInput, facultyInput, courseInput, gradeInput):
    df = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).join(Faculty, School.id == Faculty.schoolID).join(Course, Course.facultyID == Faculty.id).join(Mark, Mark.courseID == Course.id).all(), columns=["School", "Faculty", "Course", "Mark"])
    columns = [{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns]

    if addClicks > 0:
        facultyID = db.session.query(Faculty.id).filter(School.id == Faculty.schoolID).filter(Faculty.name == facultyInput).filter(School.name == schoolInput).first()
        tempFacultyID = facultyID.id

        courseExists = db.session.query(Course.id).filter_by(courseCode=courseInput, facultyID=tempFacultyID).first()
        if courseExists is not None:
            tempCourseID = courseExists.id
        else:
            tempYearLevel = re.findall('\d+|$', courseInput)[0][0]
            course = Course(courseCode=courseInput, yearLevel=tempYearLevel, facultyID=tempFacultyID)
            tempCourseID = course.id
            db.session.add(course)
            db.session.commit()

        mark = Mark(mark=gradeInput, courseID=tempCourseID)
        db.session.add(mark)
        db.session.commit()
        df = df.append({"School": schoolInput, "Faculty": facultyInput, "Course": courseInput, "Mark": gradeInput}, ignore_index=True)

    return df.to_dict('records'), columns, 0

@app.callback(
    Output("homeGraph", "figure"),
    Input("homeTable", "data"),
    )
def display_graph(data):
    df = pd.DataFrame(data)
    fig = px.box(df, x="School", y="Mark", category_orders={"name": sorted(df['School'].unique())}, labels={"Mark": "Final Course Marks"})
    return fig
