import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re
from app import app
from models import School, Faculty, Course, Mark, db
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

        dcc.Dropdown([], id="facultyFilter", multi=True),
        dcc.Dropdown([], id="courseNameFilter", multi=True),

        html.Button("Clear Filters", id="clearFilterButton", n_clicks=0)
    ]),

    html.Div([
        html.H3(
            children="Add Mark"
        ),

        dcc.Dropdown([], id="westernFacultyInput", multi=True),

        dcc.Input(
            id="westernCourseInput",
            placeholder="Enter course code",
            value="",
            style={"padding": 10}
        ),

        dcc.Input(
            id="westernGradeInput",
            placeholder="Enter course code",
            value='',
            style={"padding": 10}
        ),

        html.Button("Add Mark", id="addWesternMarkButton", n_clicks=0),

        html.Button("Clear Input", id="Clear input button", n_clicks=0)],
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='westernTable', children=[
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

    dcc.Graph(id="westernGraph", clickData=None),

    dcc.Graph(id="westernFacultyGraph" ,clickData=None),

    dcc.Graph(id="westernCourseGraph")


], style={'backgroundColor': colors['background']})

@app.callback(
    Output("westernFacultyInput", "options"),
    Output("facultyFilter", "options"),
    Input("tabs", "active_tab"),
)
def updateFacultyFilter(schoolInput):
    faculties = db.session.query(Faculty.name).filter(School.id == Faculty.schoolID).filter(School.name == "University of Western Ontario").all()
    faculties = sorted([faculty for sublist in faculties for faculty in sublist])
    return faculties, faculties

@app.callback(
    Output("courseNameFilter", "options"),
    Input("tabs", "active_tab"),
    #Input("westernTable", "data")
)
def updateCourseNameFilter(activeTab):
    df = pd.DataFrame(db.session.query(Course.courseCode).filter(Course.facultyID == Faculty.id).filter(Faculty.schoolID == School.id).filter(School.name == "University of Western Ontario"))["courseCode"].unique().tolist()
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
    Input("facultyFilter", "value"),
    Input("facultyFilter", "options"),
    Input("courseNameFilter", "value"),
    Input("courseNameFilter", "options"),
    Input("westernFacultyInput", "value"),
    Input("westernCourseInput", "value"),
    Input("westernGradeInput", "value"),
)
def updateHomeTable(activeTab, clearFilterClicks, addClicks, courseYearFilter, facultyFilter, faculties, courseNameFilter, courses, facultyInput, courseInput, gradeInput):
    if (courseYearFilter != [] or courseNameFilter != "" or facultyFilter != "") and clearFilterClicks == 0:
        if not courseYearFilter:
            courseYearFilter = [1,2,3,4]
        else:
            for i in range(len(courseYearFilter)):
                courseYearFilter[i] = int(courseYearFilter[i][0])
        if courseNameFilter == "":
            courseNameFilter = courses
        if facultyFilter == [] or facultyFilter == "":
            facultyFilter = faculties
        returnData = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(Course.facultyID == Faculty.id).filter(Faculty.schoolID == School.id).filter(School.name == "University of Western Ontario").filter(Faculty.name.in_(facultyFilter)).filter(Course.courseCode.in_(courseNameFilter)).filter(Course.yearLevel.in_(courseYearFilter)).all(), columns=["School", "Faculty", "Course", "Mark"])
        if returnData.empty:
            return [], [], 0
    else:
        returnData = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(Course.facultyID == Faculty.id).filter(School.id == Faculty.schoolID).filter(School.name == "University of Western Ontario").all(), columns=["School", "Faculty", "Course", "Mark"])
        if addClicks > 0:
            tempFacultyID = db.session.query(Faculty.id).filter(School.id == Faculty.schoolID).filter(Faculty.name == facultyInput[0]).filter(School.name == "University of Western Ontario").first()[0]

            courseExists = db.session.query(Course.id).filter(Course.courseCode == courseInput).filter(Course.facultyID == tempFacultyID).first()
            if courseExists is not None:
                tempCourseID = courseExists[0]
            else:
                tempYearLevel = re.findall('\d+|$', courseInput)[0][0]
                course = Course(courseCode=courseInput, yearLevel=tempYearLevel, facultyID=tempFacultyID)
                db.session.add(course)
                db.session.commit()
                tempCourseID = db.session.query(Course.id).filter_by(courseCode=courseInput, facultyID=tempFacultyID).first()[0]

            mark = Mark(mark=gradeInput, courseID=tempCourseID)
            db.session.add(mark)
            db.session.commit()
            returnData = returnData.append({"School": "University of Western Ontario", "Faculty": facultyInput[0], "Course": courseInput, "Mark": gradeInput}, ignore_index=True)

    columns = [{'name': str(x), 'id': str(x), 'deletable': False} for x in returnData.columns[1:]]
    return returnData.to_dict('records'), columns, 0

@app.callback(
    Output("clearFilterButton", "n_clicks"),
    Output("facultyFilter", "value"),
    Output("courseYearFilter", "value"),
    Output("courseNameFilter", "value"),
    Input("clearFilterButton", "n_clicks"),
)
def clearFilters(clearClicks):
    if clearClicks > 0:
        return 0, "", [], ""
    return 0, "", [], ""

@app.callback(
    Output("westernGraph", "figure"),
    Output("noDataError", "children"),
    Output("westernTable", "children"),
    Input("westernTable", "data"),
)
def displayMainGraph(data):
    df = pd.DataFrame(data)
    if df.empty:
        return {}, "Filters Returned No Results", None
    else:
        return px.box(df, x="Faculty", y="Mark", title="Grade Distribution By Faculty - Western University", category_orders={"Faculty": sorted(df['Faculty'].unique())}, labels={"mark": "Final Course Marks"}), "", dash.no_update

@app.callback(
    Output("westernFacultyGraph", "figure"),
    Input("westernGraph", "clickData"),
    Input("westernTable", "data"),
    Input("facultyFilter", "value")
)
def displayFacultyGraph(clickData, data, facultyFilter):
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    if facultyFilter != "":
        return px.box(df, x="Course", y="Mark",  category_orders={"Course": sorted(df['Course'].unique())}, labels={"mark": "Final Course Marks", "count": "Frequency"})
    if clickData is not None:
        faculty = clickData["points"][0]["x"]
        return px.box(df.loc[df["Faculty"] == faculty], x="Course", y="Mark", title=f"Grade Distribution By Course - {faculty}, Western University", category_orders={"Course": sorted(df['Course'].unique())}, labels={"mark": "Final Course Marks", "count": "Frequency"})
    return {}

@app.callback(
    Output("westernCourseGraph", "figure"),
    Input("westernFacultyGraph", "clickData"),
    Input("westernTable", "data"),
    Input("courseNameFilter", "value")
)
def displayFacultyGraph(clickData, data, courseFilter):
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    if courseFilter != "":
        return ff.create_distplot([df["Mark"]], [df["Course"].iloc[0]], bin_size=2.5).update_layout(title_text=f"{df['Course'].iloc[0]} Grade Distribution - {df['Faculty'].iloc[0]}, Western University")
        #return px.histogram(df, x="Mark", range_x=[0,100], nbins = 20, labels={"Mark": "Final Course Marks", "count": "Frequency"})
    if clickData is not None:
        course = clickData["points"][0]["x"]
        return ff.create_distplot([df.loc[df["Course"] == course]["Mark"].tolist()], [df.loc[df["Course"] == course]["Course"].iloc[0]], bin_size=2.5).update_layout(title_text=f"{course} Grade Distribution - {df.loc[df['Course'] == course]['Faculty'].iloc[0]}, Western University")
       #return px.histogram(df.loc[df["Course"] == course], x="Mark", title=f"{course} Grade Distribution - {df.loc[df['Course'] == course]['Faculty'].unique()[0]}, Western University", range_x=[0,100], nbins = 20, labels={"Mark": "Final Course Marks", "count": "Frequency"})
    return {}


#
# @app.callback(
#     Output("westernFacultyGraph", "figure"),
#     #Output("westernFacultyGraph", "clickData"),
#     Input("westernGraph", "clickData"),
#     Input("westernFacultyGraph", "clickData"),
#     Input("westernTable", "data"),
#     Input("facultyFilter","value")
# )
# def displayFacultyGraph(clickData, facultyClickData, data, facultyFilter):
#     df = pd.DataFrame(data)
#     if df.empty:
#         return {}
#     if facultyFilter != "":
#         return px.box(df, x="Course", y="Mark",  category_orders={"Course": sorted(df['Course'].unique())}, labels={"mark": "Final Course Marks", "count": "Frequency"})
#     if clickData is not None:
#         #if facultyClickData is not None:
#          #   return px.box(df.loc[df["Faculty"] == clickData["points"][0]["x"]], x="Course", y="Mark", category_orders={"Course": sorted(df['Course'].unique())}, labels={"mark": "Final Course Marks", "count": "Frequency"}), facultyClickData["points"].append(clickData["points"])
#         return px.box(df.loc[df["Faculty"] == clickData["points"][0]["x"]], x="Course", y="Mark",  category_orders={"Course": sorted(df['Course'].unique())}, labels={"mark": "Final Course Marks", "count": "Frequency"}), clickData
#     return {}

