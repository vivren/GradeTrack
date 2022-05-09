import dash
from dash import html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import re
from app import app
from models import School, Faculty, Course, Mark, db

colors = {
    'background': '#001D3D',
    "titleText": "#48CAE4",
    "text": "#0096C7"
}

school_layout = html.Div([
    html.Div([
        html.H5(
            children="Filter Data",
            style={"color": colors["titleText"], "padding-top": "20px"}
        ),
        dcc.Checklist(
            ["1st Year", "2nd Year", "3rd Year", "4th Year"],
            id="courseYearFilter",
            inputStyle={"margin-left": "10px", "margin-right": "5px"}
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown([],
                placeholder="Filter by Faculty",
                id="facultyFilter",
                multi=True,
                style={"width": "220px", "font-size": "12px", "text-align": "center"})
        ),
        dbc.Col(
            dcc.Dropdown([],
                placeholder="Filter by Course Code",
                id="courseNameFilter",
                multi=True,
                style={"width": "200px", "font-size": "12px"})
        ),
        dbc.Col(
            dbc.Button(
                "Clear Filters",
                id="clearFilterButton",
                className="mb-3",
                n_clicks=0,
                size="sm",
                style={"background": colors["text"]},
            ),
        ),
    ], style={"display": "inline-flex", "align-items": "center"},),

        html.H5(
            children="Add Mark",
            style={"color": colors["titleText"], "padding-top": "15px"}
        ),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown([],
                placeholder="Select Faculty",
                id="schoolFacultyInput",
                multi=True,
                style={"width": "220px", "font-size": "12px", "text-align": "center"}
            ),
        ),
        dbc.Col(
            dbc.Input(
                id="schoolCourseInput",
                placeholder="Course Code",
                value="",
                style={"width": "120px", "font-size": "12px"}
            ),
        ),
        dbc.Col(
            dbc.Input(
                id="schoolGradeInput",
                placeholder="Course Grade",
                value='',
                style={"width": "120px", "font-size": "12px"}
            ),
        ),
        dbc.Col(
            dbc.Button(
                "Add Mark",
                id="addSchoolMarkButton",
                n_clicks=0,
                size="sm",
                style={"background": colors["text"]}
            ),
        ),
        dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),
    ], style={"display": "inline-flex", "align-items": "center"},
    ),
    html.Div([
        dbc.Checklist(
            id="schoolGraphOptions",
            options=[
                {"label": "Show Data", "value": 1},
                {"label": "Show Graph Statistics", "value": 2}
            ],
            style={"color": colors["text"], "padding-top": "10px", "padding-bottom": "20px"},
            inline=True,
            switch=True,
        ),
        dbc.Collapse(
            html.Div(id='schoolTable', children=[
                dash_table.DataTable(
                    id="schoolTable",
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
            id="schoolCollapseTable",
            is_open=False,
        ),
    ]),
    html.Div([
        html.Div(
            "",
            id="noDataError",
            style={"color": "red"},
        ),
       dcc.Graph(
            id="schoolGraph",
            clickData=None
        ),
        dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolGraphCard",
            color=colors["background"],
            style={"color": colors["text"], "white-space": "pre-line", "font-size": "12px"},
            inverse=True,
            outline=True,
        ),
        dcc.Graph(
            id="schoolFacultyGraph",
            clickData=None
        ),
        dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolFacultyGraphCard",
            color=colors["background"],
            style={"color": colors["text"], "white-space": "pre-line", "font-size": "12px"},
            inverse=True,
            outline=True,
        ),
        dcc.Graph(
            id="schoolCourseGraph"
        ),
        dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolCourseGraphCard",
            color=colors["background"],
            style={"color": colors["text"], "white-space": "pre-line", "font-size": "12px"},
            inverse=True,
            outline=True,
        ),
    ]),
], style={'backgroundColor': colors['background'], "color": colors["text"], "font-family": "Epilogue"})

@app.callback(
    Output("schoolCollapseTable", "is_open"),
    [Input("schoolGraphOptions", "value")],
    [State("schoolCollapseTable", "is_open")],
)
def toggle_collapse(value, is_open):
    if value is not None:
        if 1 in value:
            return True
    return False

@app.callback(
    Output("schoolFacultyInput", "options"),
    Output("facultyFilter", "options"),
    Input("tabs", "active_tab"),
    Input("school", "children")
)
def updateFacultyFilter(activeTab, school):
    faculties = db.session.query(Faculty.name).filter(School.id == Faculty.schoolID).filter(School.name == school).all()
    faculties = sorted([faculty for sublist in faculties for faculty in sublist])
    return faculties, faculties

@app.callback(
    Output("courseNameFilter", "options"),
    Input("tabs", "active_tab"),
    Input("school", "children")
)
def updateCourseNameFilter(activeTab, school):
    df = pd.DataFrame(db.session.query(Course.courseCode).filter(Course.facultyID == Faculty.id).filter(Faculty.schoolID == School.id).filter(School.name == school))["courseCode"].unique().tolist()
    df = sorted(df)
    return df

@app.callback(
    Output("schoolTable", "data"),
    Output("schoolTable", "columns"),
    Output("addSchoolMarkButton", "n_clicks"),
    Input("tabs", "active_tab"),
    Input("clearFilterButton", "n_clicks"),
    Input("addSchoolMarkButton", "n_clicks"),
    Input("courseYearFilter", "value"),
    Input("facultyFilter", "value"),
    Input("facultyFilter", "options"),
    Input("courseNameFilter", "value"),
    Input("courseNameFilter", "options"),
    Input("schoolFacultyInput", "value"),
    Input("schoolCourseInput", "value"),
    Input("schoolGradeInput", "value"),
    Input("school", "children"),
)
def updateSchoolTable(activeTab, clearFilterClicks, addClicks, courseYearFilter, facultyFilter, faculties, courseNameFilter, courses, facultyInput, courseInput, gradeInput, school):
    if (courseYearFilter != [] or courseNameFilter is not None or facultyFilter is not None) and clearFilterClicks == 0:
        if not courseYearFilter:
            courseYearFilter = [1,2,3,4]
        else:
            for i in range(len(courseYearFilter)):
                courseYearFilter[i] = int(courseYearFilter[i][0])
        if courseNameFilter is None:
            courseNameFilter = courses
        if facultyFilter is None or facultyFilter is None:
            facultyFilter = faculties
        returnData = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(Course.facultyID == Faculty.id).filter(Faculty.schoolID == School.id).filter(School.name == school).filter(Faculty.name.in_(facultyFilter)).filter(Course.courseCode.in_(courseNameFilter)).filter(Course.yearLevel.in_(courseYearFilter)).all(), columns=["School", "Faculty", "Course", "Mark"])
        if returnData.empty:
            return [], [], 0
    else:
        returnData = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).filter(Mark.courseID == Course.id).filter(Course.facultyID == Faculty.id).filter(School.id == Faculty.schoolID).filter(School.name == school).all(), columns=["School", "Faculty", "Course", "Mark"])
        if addClicks > 0:
            tempFacultyID = db.session.query(Faculty.id).filter(School.id == Faculty.schoolID).filter(Faculty.name == facultyInput[0]).filter(School.name == school).first()[0]

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
            returnData = returnData.append({"School": school, "Faculty": facultyInput[0], "Course": courseInput, "Mark": gradeInput}, ignore_index=True)

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
        return 0, None, [], None
    return 0, None, [], None

@app.callback(
    Output("schoolGraph", "figure"),
    Output("noDataError", "children"),
    Output("schoolTable", "children"),
    Input("schoolTable", "data"),
    Input("school", "children")
)
def displayMainGraph(data, school):
    df = pd.DataFrame(data)
    if df.empty:
        return {}, "Filters Returned No Results", None
    else:
        fig = px.box(df, x="Faculty", y="Mark", title=f"Grade Distribution By Faculty - {school}", category_orders={"Faculty": sorted(df['Faculty'].unique())}, labels={"mark": "Final Course Marks"})
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue", font_color="#90E0EF"), "", dash.no_update

@app.callback(
    Output("schoolGraphCard", "children"),
    Input("schoolGraphOptions", "value"),
    Input("schoolTable", "data"),
)
def showSchoolStatistics(value, data):
    if value is not None:
        if 2 in value:
            stats = pd.DataFrame(data)["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H6("Summary of Data", className="card-subtitle"),
                    html.P(
                        f"Mean: {stats[1]:.2f}\nMedian: {stats[5]:.2f}\nStandard Deviation: {stats[2]:.2f}\nMinimum: {stats[3]:.2f}\nMaximum: {stats[7]:.2f}",
                        className="card-text"),
                ]
            )
    return ""

@app.callback(
    Output("schoolFacultyGraph", "figure"),
    [Input("schoolGraph", "clickData"),
    Input("schoolTable", "data"),
    Input("facultyFilter", "value"),
    Input("school", "children"),
    Input("clearFilterButton", "n_clicks"),
    ]
)
def displayFacultyGraph(clickData, data, facultyFilter, school, clearFilterClicks):
    df = pd.DataFrame(data)
    if clearFilterClicks != 0 or df.empty:
        return {}
    if clickData is not None:
        faculty = clickData["points"][0]["x"]
        df = df.loc[df["Faculty"] == faculty]
        fig = px.box(df, x="Course", y="Mark", category_orders={"Course": sorted(df['Course'].unique())}, title=f"Grade Distribution By Course - {faculty}, {school}", labels={"mark": "Final Course Marks"})
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue", font_color="#90E0EF")
    if facultyFilter is not None:
        fig = px.box(df, x="Course", y="Mark",  category_orders={"Course": sorted(df['Course'].unique())}, title=f"Grade Distribution By Course - {df['Faculty'].unique().tolist()[0]}, {school}", labels={"mark": "Final Course Marks"})
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue",
                                 font_color="#90E0EF")
    return dash.no_update

@app.callback(
    Output("schoolFacultyGraphCard", "children"),
    Input("schoolGraphOptions", "value"),
    Input("schoolFacultyGraph", "figure"),
    Input("schoolTable", "data")
)
def showFacultyStatistics(value, figure, data):
    if value is not None and figure is not None:
        if 2 in value:
            courses = list(set(figure["data"][0]["x"]))
            df = pd.DataFrame(data)
            stats = df.loc[df["Course"].isin(courses)]["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H6("Summary of Data", className="card-subtitle"),
                    html.P(f"Mean: {stats[1]:.2f}\nMedian: {stats[5]:.2f}\nStandard Deviation: {stats[2]:.2f}\nMinimum: {stats[3]:.2f}\nMaximum: {stats[7]:.2f}", className="card-text"),
                ]
            )
    return ""

@app.callback(
    Output("schoolCourseGraph", "figure"),
    Input("schoolCourseGraph", "figure"),
    Input("schoolFacultyGraph", "clickData"),
    Input("schoolTable", "data"),
    Input("courseNameFilter", "value"),
    Input("school", "children"),
    Input("clearFilterButton", "n_clicks"),
)
def displayCourseGraph(figure, clickData, data, courseFilter, school, clearFilterClicks):
    df = pd.DataFrame(data)
    if clearFilterClicks != 0 or df.empty:
        return {}
    if courseFilter != "":
        fig = ff.create_distplot([df["Mark"]], [df["Course"].iloc[0]], bin_size=3).update_layout(title_text=f"{df['Course'].iloc[0]} Grade Distribution - {df['Faculty'].iloc[0]}, {school}")
    if clickData is not None:
        course = clickData["points"][0]["x"]
        if figure == {} or figure is None:
            fig = ff.create_distplot([df.loc[df["Course"] == course]["Mark"].tolist()], [df.loc[df["Course"] == course]["Course"].iloc[0]], bin_size=3).update_layout(title_text=f"{course} Grade Distribution - {df.loc[df['Course'] == course]['Faculty'].iloc[0]}, {school}")
            return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue",
                                     font_color="#90E0EF")
        else:
            originalCourse = []
            originalData = []
            for i in range(1, len(figure["data"])):
                originalCourse.append(figure["data"][-i]["name"])
            for j in range(1, len(set(originalCourse))+1):
                originalData.append(figure["data"][-j]["x"])
            if course in originalCourse:
                originalCourse = list(set(originalCourse))
                for k in range(len(originalCourse)):
                    if originalCourse[k] == course:
                        originalData.pop(k)
                originalCourse.remove(course)
                if len(originalCourse) == 0:
                    return dash.no_update
            else:
                originalData.append(df.loc[df["Course"] == course]["Mark"].tolist())
                originalCourse.append(course)
            fig = ff.create_distplot(originalData, list(set(originalCourse)), bin_size=3).update_layout(title_text=f"{set(originalCourse)} Grade Distribution - {df.loc[df['Course'] == course]['Faculty'].iloc[0]}, {school}")
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue",
                                 font_color="#90E0EF")
    return dash.no_update

@app.callback(
    Output("schoolCourseGraphCard", "children"),
    Input("schoolGraphOptions", "value"),
    Input("schoolCourseGraph", "figure"),
    Input("schoolTable", "data")
)
def showCourseStatistics(value, figure, data):
    if value is not None and figure is not None:
        if 2 in value:
            courses = figure["layout"]["title"]["text"].split(" Grade", 1)[0].replace("'", "").replace("{", "").replace("}", "").split(", ")
            df = pd.DataFrame(data)
            stats = df.loc[df["Course"].isin(courses)]["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H6("Summary of Data", className="card-subtitle"),
                    html.P(f"Mean: {stats[1]:.2f}\nMedian: {stats[5]:.2f}\nStandard Deviation: {stats[2]:.2f}\nMinimum: {stats[3]:.2f}\nMaximum: {stats[7]:.2f}", className="card-text")
                ]
            )
    return ""
