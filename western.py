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
    html.Div(id='gradesTable', children=[
        dash_table.DataTable(
            id="table",
            columns=[{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns],
            data=df.loc[df["name"] == "University of Western Ontario"].to_dict('records'),
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
#     Output("table", 'data'),
#     Output("Add mark button", "n_clicks"),
#     Input("Add mark button", "n_clicks"),
#     Input("table", "data"),
#     Input("table", "columns"),
#     Input("schoolInput", "value"),
#     Input("courseInput", "value"),
#     Input("gradeInput", "value"),
# )
# def add_rows(n_clicks, data, columns, schoolInput, courseInput, gradeInput):
#     if n_clicks > 0:
#         schoolID = db.session.query(School.id).filter_by(name=schoolInput).first()
#         tempSchoolID = schoolID.id
#
#         courseExists = db.session.query(Course.id).filter_by(courseCode=courseInput, schoolID=tempSchoolID).first()
#         if courseExists != None:
#             tempCourseID = courseExists.id
#         else:
#             yearLevel = re.findall('\d+|$', courseInput)[0][0]
#             course = Course(courseCode=courseInput, yearLevel=1, schoolID=tempSchoolID)
#             tempCourseID = course.id
#             db.session.add(course)
#             db.session.commit()
#
#         mark = Mark(mark=gradeInput, courseID=tempCourseID)
#         db.session.add(mark)
#         db.session.commit()
#         data.append({"name": schoolInput, "courseCode": courseInput, "mark": gradeInput})
#
#     return data, 0
#
#
# @app.callback(
#     Output("graph", "figure"),
#     [Input("table", "data")])
# def display_graph(data):
#     df = pd.DataFrame(data)
#     # df.columns = ['name', 'courseCode', 'mark']
#     fig = px.box(df, x="name", y="mark", labels={"name": "School Name", "mark": "Final Course Marks"})
#     return fig
#
# # @app.callback(
# #     Output("schoolInput", "value"),
# #     # Output("courseInput", "value"),
# #     # Output("gradeInput", "value"),
# #     Input("Clear input button", "n_clicks")
# # )
# # def clearInput(n_clicks):
# #     if n_clicks > 0:
# #         return tuple("")
#
# if __name__ == '__main__':
#     app.run_server(debug=True)
