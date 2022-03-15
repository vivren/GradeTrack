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

server = Flask(__name__)

app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://master:password@gradetrack.cmoor2gacvn8.us-east-1.rds.amazonaws.com/gradetrack"

db = SQLAlchemy(app.server)

class School(db.Model):
    __tablename__ = "school"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    courses = db.relationship("Course", backref='school')


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    courseCode = db.Column(db.String(40), nullable=False)
    yearLevel = db.Column(db.Integer, nullable=False)
    schoolID = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    marks = db.relationship("Mark", backref='course')


class Mark(db.Model):
    __tablename__ = "mark"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)
    courseID = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

data = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).all()
df = pd.DataFrame(data)

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
}

selectedTabStyle = {
    "background": '#7FDBFF',
    'color': 'white',
    #'font-size': '11px',
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
                dbc.Tab(label="Western", tab_id="westernTab", active_tab_style = selectedTabStyle, labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                #dbc.Tab(label="Waterloo", tab_id="tab-waterloo", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                #dbc.Tab(label="Queens", tab_id="tab-queens", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
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
    #dbc.Row(dbc.Row(app_tabs), className="mb-3"),

    html.Div(id='content', children=[]),
    ], style={'backgroundColor': colors['background'], "color": colors['text'], "textAlign": "center", "font-family": 'Trebuchet MS'})

@app.callback(
    Output("table", "data"),
    Output("filterButton", "n_clicks"),
    Input("filterButton", "n_clicks"),
    Input("courseYearFilter", "value")
)
def filterData(n_clicks, courseYear):
    if n_clicks > 0:
        filteredData = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).filter_by(yearLevel=courseYear[0]).all()
        return data, 0

@app.callback(
    Output("table", 'data'),
    Output("Add mark button", "n_clicks"),
    Input("Add mark button", "n_clicks"),
    Input("table", "data"),
    Input("schoolInput", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
    Input("tabs", "active_tab")
)
def addRows(n_clicks, data, schoolInput, courseInput, gradeInput, activeTab):
    if n_clicks > 0:
        if activeTab != "homeTab":
            schoolInput = data[0]["name"]

        schoolID = db.session.query(School.id).filter_by(name=schoolInput).first()
        tempSchoolID = schoolID.id

        courseExists = db.session.query(Course.id).filter_by(courseCode=courseInput, schoolID=tempSchoolID).first()
        if courseExists != None:
            tempCourseID = courseExists.id
        else:
            yearLevel = re.findall('\d+|$', courseInput)[0][0]
            course = Course(courseCode=courseInput, yearLevel=1, schoolID=tempSchoolID)
            tempCourseID = course.id
            db.session.add(course)
            db.session.commit()

        mark = Mark(mark=gradeInput, courseID=tempCourseID)
        db.session.add(mark)
        db.session.commit()

        data.append({"name": schoolInput, "courseCode": courseInput, "mark": gradeInput})
        return data, 0

@app.callback(
    Output("graph", "figure"),
    Input("table", "data"),
    Input("tabs", "active_tab")
)
def display_graph(data, tab_chosen):
    df = pd.DataFrame(data)
    if tab_chosen == "homeTab":
        fig = px.box(df, x="name", y="mark", labels={"name": "School Name", "mark": "Final Course Marks"})
    else:
        fig = px.box(df, x="courseCode", y="mark", labels={"courseCode": "Course Code", "mark": "Final Course Marks"})
    return fig


@app.callback(
    Output("content", "children"),
    Input("tabs", "active_tab")
)
def switch_tab(tab_chosen):
    if tab_chosen == "homeTab":
        return home_layout
    elif tab_chosen == "westernTab":
        return western_layout
    # elif tab_chosen == "tab-waterloo":
    #     return waterloo_layout
    # elif tab_chosen == "tab-queens":
    #     return queens_layout

if __name__ == '__main__':
    app.run_server(debug=True)
