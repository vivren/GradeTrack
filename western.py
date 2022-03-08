import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_bootstrap_components as dbc
import re

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app.server)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

western_layout = html.Div([
    dbc.Row(dbc.Col(html.H1("Western", style={"textAlign": "center"}), width=12)),
    html.Hr(),

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
        #style={"height": 50, "left": "50%", "right": "50%"}
        ),

    dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    html.Div(id='gradesTable', children=[]),

    dcc.Graph(id="graph")
])

@app.callback(
    Output('gradesTable', 'children'),
    [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    data = db.session.query(School.name, Course.courseCode, Mark.mark).join(Course, School.id == Course.schoolID).join(Mark, Mark.courseID == Course.id).all()
    df = pd.DataFrame(data)

    return [
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
    ]


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
