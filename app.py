import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import re

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLALCHEMY DATABASE URI CONFIGURATION HERE

db = SQLAlchemy(app.server)

class School(db.Model):
    __tablename__ = "school"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    courses = db.relationship("Course", backref='school')
    schoolList = []

    def __init__(self):
        self.schoolList.append(self.name)

    def exists(self):
        if self.name in self.schoolList:
            return self.id
        else:
            return False

class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    courseCode = db.Column(db.String(40), nullable=False)
    yearLevel = db.Column(db.Integer, nullable=False)
    schoolID = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    marks = db.relationship("Mark", backref='course')
    courseList = {}

    def __init__(self):
        self.courseList[self.courseCode] = self.schoolID;

    def exists(self):
        if self.courseCode in self.courseList:
            if self.courseList[self.courseCode] == self.schoolID:
                return self.id
        else:
            return False

class Mark(db.Model):
    __tablename__ = "mark"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)
    courseID = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

# db.create_all()
#
# western = School(name="Western University")
# course = Course(courseCode="CS1026", yearLevel=1, schoolID=1)
# course2 = Course(courseCode="CS1027", yearLevel=1, schoolID=1)
# mark = Mark(mark=91, courseID=1)
# mark2 = Mark(mark=85, courseID=1)
# mark3 = Mark(mark=62, courseID=1)
# mark4 = Mark(mark=50, courseID=2)
# mark5 = Mark(mark=99, courseID=2)
# mark6 = Mark(mark=78, courseID=2)
#
# db.session.add(western)
# db.session.add(course)
# db.session.add(course2)
# db.session.add(mark)
# db.session.add(mark2)
# db.session.add(mark3)
# db.session.add(mark4)
# db.session.add(mark5)
# db.session.add(mark6)
#
# db.session.commit()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
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
        dcc.Input(
            id="schoolInput",
            placeholder="Enter school",
            value="",
            style={"padding": 10}
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
    style={"height": 50, "left": "50%", "right": "50%"}),

    dcc.Interval(id='interval_pg', interval=99999999*7, n_intervals=0),
    html.Div(id='gradesTable', children=[]),

    dcc.Graph(id="graph")
])

    # html.Div(children=[
    #     html.Label('Dropdown'),
    #     dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
    #
    #     html.Br(),
    #     html.Label('Multi-Select Dropdown'),
    #     dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
    #                  ['Montréal', 'San Francisco'],
    #                  multi=True),
    #
    #     html.Br(),
    #     html.Label('Radio Items'),
    #     dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
    # ], style={'padding': 10, 'flex': 1}),

    # html.Div(children=[
    #     html.Label('Checkboxes'),
    #     dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
    #                   ['Montréal', 'San Francisco']
    #     ),
    #
    #     html.Br(),
    #     html.Label('Slider'),
    #     dcc.Slider(
    #         min=0,
    #         max=9,
    #         marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
    #         value=5,
    #     ),
    # ], style={'padding': 10, 'flex': 1}),

# @app.callback(
#     Output("store", "data"),
#     Input("Add mark button", "n_clicks"),
#     [State("our-table","data"),
#      State("store","data")]
# )
# def save_df(n_clicks, dataset, s):
#     input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
#     if n_clicks > 0:
#         s = 6
#         pg = pd.DataFrame(dataset)
#         pg.to_sql("school", con=db.engine, if_exists='replace', index=False)
#         return s

@app.callback(
    Output('gradesTable', 'children'),
    [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    data = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id==Course.schoolID).join(Mark, Mark.courseID==Course.id).all()
    #df = pd.read_sql('data', con=db.engine)
    df = pd.DataFrame(data)

    return [
        dash_table.DataTable(
            id="table",
            columns=[{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
        ),
    ]

@app.callback(
    Output("table", 'data'),
    Input("Add mark button", "n_clicks"),
    Input("table", "data"),
    Input("table", "columns"),
    Input("schoolInput", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
)
def add_rows(n_clicks, data, columns, schoolInput, courseInput, gradeInput):
    school = School(name=schoolInput)
    if school.exists():
        tempSchoolID = school.exists()
        del school
    else:
        tempSchoolID = school.id
        db.session.add(school)

    course = Course(courseCode=courseInput, yearLevel=courseInput[re.search(r'\d+', courseInput).group()], schoolID=tempSchoolID)
    if course.exists():
        tempCourseID = course.exists()
        del course
    else:
        tempCourseID = course.id
        db.session.add(course)

    mark = Mark(mark=gradeInput, courseID=tempCourseID)
    db.session.add(mark)

    db.session.commit()

    if n_clicks > 0:
        data.append({"name": schoolInput, "courseCode": courseInput, "mark": gradeInput})
    return data

@app.callback(
    Output("graph", "figure"),
    [Input("table", "data")])
def display_graph(data):
    df = pd.DataFrame(data)
    print(df)
    #df.columns = ['name', 'courseCode', 'mark']
    fig = px.box(df, x="courseCode", y="mark")
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

if __name__ == '__main__':
    app.run_server(debug=True)
