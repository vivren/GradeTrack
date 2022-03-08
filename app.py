import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re

from western import western_layout

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# db.create_all()
# western = School(name="University of Western Ontario")
# uoft = School(name="University of Toronto")
# york = School(name="York University")
# ubc = School(name="University of British Columbia")
# waterloo = School(name="University of Waterloo")
# mcgill = School(name="McGill University")
# laurier = School(name="Wilfred Laurier University")
# queens = School(name="Queens University")
# guelph = School(name="University of Guelph")
#
# course = Course(courseCode="CS1026", yearLevel=1, schoolID=1)
# course2 = Course(courseCode="CS1027", yearLevel=1, schoolID=2)
# course3 = Course(courseCode="CS1026", yearLevel=1, schoolID=3)
# course4 = Course(courseCode="CS1026", yearLevel=1, schoolID=4)
# course5 = Course(courseCode="CS1026", yearLevel=1, schoolID=5)
# course6 = Course(courseCode="CS1026", yearLevel=1, schoolID=6)
# course7 = Course(courseCode="CS1026", yearLevel=1, schoolID=7)
# course8 = Course(courseCode="CS1026", yearLevel=1, schoolID=8)
# course9 = Course(courseCode="CS1026", yearLevel=1, schoolID=9)
#
# mark = Mark(mark=91, courseID=1)
# mark2 = Mark(mark=85, courseID=2)
# mark3 = Mark(mark=62, courseID=3)
# mark4 = Mark(mark=50, courseID=4)
# mark5 = Mark(mark=99, courseID=5)
# mark6 = Mark(mark=78, courseID=6)
# mark7 = Mark(mark=42, courseID=7)
# mark8 = Mark(mark=72, courseID=8)
# mark9 = Mark(mark=89, courseID=9)
#
# db.session.add(western)
# db.session.add(uoft)
# db.session.add(york)
# db.session.add(ubc)
# db.session.add(waterloo)
# db.session.add(mcgill)
# db.session.add(laurier)
# db.session.add(queens)
# db.session.add(guelph)
#
# db.session.add(course)
# db.session.add(course2)
# db.session.add(course3)
# db.session.add(course4)
# db.session.add(course5)
# db.session.add(course6)
# db.session.add(course7)
# db.session.add(course8)
# db.session.add(course9)
#
# db.session.add(mark)
# db.session.add(mark2)
# db.session.add(mark3)
# db.session.add(mark4)
# db.session.add(mark5)
# db.session.add(mark6)
# db.session.add(mark7)
# db.session.add(mark8)
# db.session.add(mark9)

#db.session.commit()
data = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).all()
df = pd.DataFrame(data)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Western", tab_id="tab-western", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Waterloo", tab_id="tab-waterloo", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Queens", tab_id="tab-queens", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
            ],
            id="tabs",
            active_tab="tab-mentions",
        ),
    ], className="mt-3"
)

app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1("GradeTrack", style={"textAlign": "center"}), width=12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    html.Div(id='content', children=[]),

    html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='GradeTrack',
            style={
                'textAlign': 'center',
                'color': colors['text']
            })
    ]),
    html.Div(children="View Your School Course Averages", style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div([
        dcc.Dropdown(["University of Western Ontario", "University of Toronto", "York University",
                      "University of British Columbia", "University of Waterloo", "McGill University",
                      "Wilfred Laurier University", "Queens University", "University of Guelph"],
                     placeholder="Select your school", id="schoolInput"
                     #style={"width": "50%", "left": "50%", "right": "50%" }

                     # dcc.Input(
                     #     id="schoolInput",
                     #     placeholder="Enter school",
                     #     value="",
                     #     style={"padding": 10}
                     ),

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

        html.Button("Add Mark", id="Add mark button", n_clicks=0),

        html.Button("Clear Input", id="Clear input button", n_clicks=0)],
        style={'backgroundColor': colors['background']}
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='gradesTable', children=[
            dash_table.DataTable(
            id="table",
            columns=[{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns],
            data=df.to_dict('records'),
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
        ),
    ]),
    dcc.Graph(id="graph")
])

# @app.callback(
#     Output('gradesTable', 'children'),
#     [Input('interval_pg', 'n_intervals')])
# def populate_datatable(n_intervals):
#     data = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).all()
#     df = pd.DataFrame(data)
#
#     return [
#         dash_table.DataTable(
#             id="table",
#             columns=[{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns],
#             data=df.to_dict('records'),
#             row_deletable=False,
#             sort_action="native",
#             sort_mode="multi",
#             page_action="none",
#             style_table={"height": "300px", "overflowY": "auto"},
#             style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
#         ),
#     ]


@app.callback(
    Output("table", 'data'),
    Output("Add mark button", "n_clicks"),
    Input("Add mark button", "n_clicks"),
    Input("table", "data"),
    Input("table", "columns"),
    Input("schoolInput", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
)
def add_rows(n_clicks, data, columns, schoolInput, courseInput, gradeInput):
    if n_clicks > 0:
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
    [Input("table", "data")])
def display_graph(data):
    df = pd.DataFrame(data)
    # df.columns = ['name', 'courseCode', 'mark']
    fig = px.box(df, x="name", y="mark", labels={"name": "School Name", "mark": "Final Course Marks"})
    return fig

# @app.callback(
#     Output("schoolInput", "value"),
#     # Output("courseInput", "value"),
#     # Output("gradeInput", "value"),
#     Input("Clear input button", "n_clicks")
# )
# def clearInput(n_clicks):
#     if n_clicks > 0:
#         return tuple("")

@app.callback(
    Output("content", "children"),
    [Input("tabs", "active_tab")]
)
def switch_tab(tab_chosen):
    if tab_chosen == "tab-western":
        return western_layout
    # elif tab_chosen == "tab-waterloo":
    #     return waterloo_layout
    # elif tab_chosen == "tab-queens":
    #     return queens_layout
    return html.P("This shouldn't be displayed for now...")

if __name__ == '__main__':
    app.run_server(debug=True)
