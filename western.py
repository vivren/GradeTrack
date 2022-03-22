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
from sqlalchemy.sql import text

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
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

        html.Button("Clear Filters", id="clearFilterButton", n_clicks=0)
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

        html.Button("Add Mark", id="addWesternMarkButton", n_clicks=0),

        html.Button("Clear Input", id="Clear input button", n_clicks=0)],
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='gradesTable', children=[
        dash_table.DataTable(
            id="westernTable",
            columns=[],
            data=[],
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={'textAlign': 'left', "minWidth": "100px", "width": "800px", "maxWidth": "800px"}
        ),
    ]),

    html.Div("", id="noDataError", style={"padding": 50, "color": "red"}),

    dcc.Graph(id="westernGraph"),


], style={'backgroundColor': colors['background']})

@app.callback(
    Output("courseNameFilter", "options"),
    Input("tabs", "active_tab"),
    Input("westernTable", "data")
)
def updateCourseNameFilter(activeTab, data):
    df = pd.DataFrame(db.session.query(Course.courseCode).filter(Course.schoolID == School.id).filter(School.name == "University of Western Ontario"))["courseCode"].unique().tolist()
    df = sorted(df)
    return df

@app.callback(
    Output("westernTable", "data"),
    Output("westernTable", "columns"),
    Output("addWesternMarkButton", "n_clicks"),
    Input("tabs", "active_tab"),
    Input("clearFilterButton", "n_clicks"),
    Input("addWesternMarkButton", "n_clicks"),
    Input("courseYearFilter", "value"),
    Input("courseNameFilter", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
    Input("westernTable", "data"),
)
def updateHomeTable(activeTab, clearFilterClicks, addClicks, courseYearFilter, courseNameFilter, courseInput, gradeInput, data):
    if (courseYearFilter != [] or courseNameFilter != "") and clearFilterClicks == 0:
        if not courseYearFilter:
            courseYearFilter = db.session.query(Course.yearLevel).filter(School.name == "University of Western Ontario").all()
            courseYearFilter = [year for sublist in courseYearFilter for year in sublist]
        else:
            for i in range(len(courseYearFilter)):
                courseYearFilter[i] = int(courseYearFilter[i][0])
        if courseNameFilter == "":
            courseNameFilter = db.session.query(Course.courseCode).filter(Course.schoolID == School.id).filter(School.name == "University of Western Ontario").all()
            courseNameFilter = [course for sublist in courseNameFilter for course in sublist]
        returnData = pd.DataFrame(db.session.query(School.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(Course.schoolID == School.id).filter(School.name == "University of Western Ontario").filter(Course.courseCode.in_(courseNameFilter)).filter(Course.yearLevel.in_(list(set(courseYearFilter)))).all())
        if returnData.empty:
            return [], [], 0
    else:
        returnData = pd.DataFrame(db.session.query(School.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(School.id == Course.schoolID).filter(School.name == "University of Western Ontario").all())
        if addClicks > 0:
            schoolID = db.session.query(School.id).filter_by(name="University of Western Ontario").first()
            tempSchoolID = schoolID.id

            courseExists = db.session.query(Course.id).filter_by(courseCode=courseInput, schoolID=tempSchoolID).first()
            if courseExists is not None:
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

            returnData = returnData.append({"name": "University of Western Ontario", "courseCode": courseInput, "mark": gradeInput}, ignore_index=True)
            print(returnData)
    columns = [{'name': str(x), 'id': str(x), 'deletable': False} for x in returnData.columns[1:]]
    return returnData.to_dict('records'), columns, 0

@app.callback(
    Output("clearFilterButton", "n_clicks"),
    Output("courseYearFilter", "value"),
    Output("courseNameFilter", "value"),
    Input("clearFilterButton", "n_clicks"),
)
def clearFilters(clearClicks):
    if clearClicks > 0:
        return 0, [], ""
    return 0, [], ""

@app.callback(
    Output("westernGraph", "figure"),
    Output("noDataError", "children"),
    Output("gradesTable", "children"),
    Input("westernTable", "data"),
)
def display_graph(data):
    df = pd.DataFrame(data)
    if df.empty:
        return {}, "Filters Returned No Results", None
    else:
        return px.box(df, x="courseCode", y="mark",  category_orders={"courseCode": sorted(df['courseCode'].unique())}, labels={"courseCode": "Course Name", "mark": "Final Course Marks"}), "", dash.no_update
