import dash
from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

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
