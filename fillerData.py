import dash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import random as r
import numpy as np
import string

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://master:password@gradetrack.cmoor2gacvn8.us-east-1.rds.amazonaws.com/gradetrack"

db = SQLAlchemy(app.server)

class School(db.Model):
    __tablename__ = "school"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    faculties = db.relationship("Faculty", backref='school')

class Faculty(db.Model):
    __tabelname__ = "faculty"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    schoolID = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    courses = db.relationship("Course", backref='faculty')

class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    courseCode = db.Column(db.String(40), nullable=False)
    yearLevel = db.Column(db.Integer, nullable=False)
    facultyID = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    marks = db.relationship("Mark", backref='course')

class Mark(db.Model):
    __tablename__ = "mark"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)
    courseID = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

db.create_all()

# western = School(name="University of Western Ontario")
# uoft = School(name="University of Toronto")
# york = School(name="York University")
# waterloo = School(name="University of Waterloo")
# laurier = School(name="Wilfred Laurier University")
# queens = School(name="Queens University")
#
# db.session.add(western)
# db.session.add(uoft)
# db.session.add(york)
# db.session.add(waterloo)
# db.session.add(laurier)
# db.session.add(queens)
# db.session.commit()

# westernArts = Faculty(name="Arts and Humanities", schoolID=1)
# westernEducation = Faculty(name="Faculty of Education", schoolID=1)
# westernEngineering = Faculty(name="Faculty of Engineering", schoolID=1)
# westernMedia= Faculty(name="Faculty of Information and Media Studies", schoolID=1)
# westernHealthSci = Faculty(name="Faculty of Health Science", schoolID=1)
# westernIvey = Faculty(name="Ivey School of Business", schoolID=1)
# westernLaw = Faculty(name="Faculty of Law", schoolID=1)
# westernMusic = Faculty(name="Don Wright Faculty of Music", schoolID=1)
# westernMedicine = Faculty(name="Schulich School of Medicine and Dentistry", schoolID=1)
# westernScience = Faculty(name="Faculty of Science", schoolID=1)
# westernSocialScience = Faculty(name="Faculty of Social Science", schoolID=1)
#
# db.session.add(westernArts)
# db.session.add(westernEducation)
# db.session.add(westernEngineering)
# db.session.add(westernMedia)
# db.session.add(westernHealthSci)
# db.session.add(westernIvey)
# db.session.add(westernLaw)
# db.session.add(westernMusic)
# db.session.add(westernMedicine)
# db.session.add(westernScience)
# db.session.add(westernSocialScience)
# db.session.commit()
#
# for i in range(2, 7):
#     science = Faculty(name="Faculty of Science", schoolID=i)
#     arts = Faculty(name="Faculty of Arts", schoolID=i)
#     eng = Faculty(name="Faculty of Engineering", schoolID=i)
#     bus = Faculty(name="School of Business", schoolID=i)
#     law = Faculty(name="Faculty of Law", schoolID=i)
#     db.session.add(science)
#     db.session.add(arts)
#     db.session.add(eng)
#     db.session.add(bus)
#     db.session.add(law)
#     db.session.commit()

# course = Course(courseCode="ENG 1020", yearLevel=1, facultyID=1)
# course2 = Course(courseCode="ES 2297", yearLevel=2, facultyID=3)
# course3 = Course(courseCode="MIT 2156", yearLevel=2, facultyID=4)
# course4 = Course(courseCode="HS 4120", yearLevel=4, facultyID=5)
# course5 = Course(courseCode="CS 1026", yearLevel=1, facultyID=10)
# course6 = Course(courseCode="CS 1027", yearLevel=1, facultyID=10)
# course7 = Course(courseCode="CS 2209", yearLevel=2, facultyID=10)
# course8 = Course(courseCode="CS 3340", yearLevel=3, facultyID=10)
# course9 = Course(courseCode="CS 3121", yearLevel=3, facultyID=10)
# course10 = Course(courseCode="BUS 2257", yearLevel=2, facultyID=11)
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
# db.session.add(course10)
# db.session.commit()
#
# for i in range(12, 37):
#     for j in range(0,2):
#         randomLetter1 = r.choice(string.ascii_letters).capitalize()
#         randomLetter2 = r.choice(string.ascii_letters).capitalize()
#         year = r.randint(1,4)
#         course = Course(courseCode=f"{randomLetter1}{randomLetter2} {year}{r.randint(0,9)}{r.randint(0,9)}{r.randint(0,9)}", yearLevel=year, facultyID=i)
#         db.session.add(course)
# db.session.commit()
#
# for i in range(1, 61):
#     mean = r.randint(50, 90)
#     stdDev = r.randint(1, 20)
#     marks = np.random.normal(mean, stdDev, 50)
#     marks[marks>100] = 100
#     for x in marks:
#         mark = Mark(mark=x, courseID=i)
#         db.session.add(mark)
# db.session.commit()

#TRUNCATE course, mark, school, faculty;

# ALTER SEQUENCE school_id_seq RESTART WITH 1;
# ALTER SEQUENCE faculty_id_seq RESTART WITH 1;
# ALTER SEQUENCE course_id_seq RESTART WITH 1;
# ALTER SEQUENCE mark_id_seq RESTART WITH 1;


