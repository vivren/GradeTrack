import dash
from dash import html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import re
from app import app
from models import School, Faculty, Course, Mark, db

colors = {
    'background': '#001D3D',
    "titleText": "#48CAE4",
    "text": "#0096C7"
}

school_layout = html.Div([
    # html.Div(style={'backgroundColor': colors['background']}, children=[
    #     html.H2(
    #         children=school,
    #         id="title",
    #         style={
    #             'textAlign': 'center',
    #             'color': colors['text']
    #         })
    # ]),

    html.Div([
        html.H5(
            children="Filter Data",
            style={"color": colors["titleText"]}
        ),

        dcc.Checklist(["1st Year", "2nd Year", "3rd Year", "4th Year"], id="courseYearFilter"),

        dcc.Dropdown([], placeholder="Filter by Faculty", id="facultyFilter", multi=True, style={"width": "30%"}),
        dcc.Dropdown([], placeholder="Filter by Course Code", id="courseNameFilter", multi=True, style={"width": "30%"}),

        dbc.Button(
            "Clear Filters",
            id="clearFilterButton",
            className="mb-3",
            n_clicks=0,
        )]),

    html.Div([
        html.H5(
            children="Add Mark",
            style = {"color": colors["titleText"]}
),

        dcc.Dropdown([], placeholder="Select Course Faculty", id="schoolFacultyInput", multi=True),

        dbc.Input(
            id="schoolCourseInput",
            placeholder="Enter course code",
            value="",
            style={"padding": 10}
        ),

        dbc.Input(
            id="schoolGradeInput",
            placeholder="Enter course grade",
            value='',
            style={"padding": 10}
        ),

        dbc.Button("Add Mark", id="addSchoolMarkButton", n_clicks=0, style={"background": "#0096C7"}),

        dbc.Button("Clear Input", id="clearSchoolInputButton", n_clicks=0, style={"background": "#0096C7"}),

        dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0),

    ]),

    html.Div([
        dbc.Button(
            "Show Data",
            id="collapseDataButton",
            className="mb-3",
            n_clicks=0,
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
            id="collapseTable",
            is_open=False,
        ),
    ]),

    html.Div([

    dcc.Checklist(id="schoolGraphOptions", options=["Show Graph Statistics"])

    ]),

    html.Div("", id="noDataError", style={"padding": 50, "color": "red"}),

    dcc.Graph(id="schoolGraph", clickData=None),

    dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolGraphCard",
            inverse=True,
            outline=True,
    ),

    dcc.Graph(id="schoolFacultyGraph", clickData=None),

    dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolFacultyGraphCard",
            inverse=True,
            outline=True,
    ),

    dcc.Graph(id="schoolCourseGraph"),

    dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="schoolCourseGraphCard",
            inverse=True,
            outline=True,
    ),


], style={'backgroundColor': colors['background'], "color": colors["text"], "font-family": "Epilogue"})

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
    Input("school", "children")
)
def updateHomeTable(activeTab, clearFilterClicks, addClicks, courseYearFilter, facultyFilter, faculties, courseNameFilter, courses, facultyInput, courseInput, gradeInput, school):
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
        return 0, "", [], ""
    return 0, "", [], ""

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
        if "Show Statistics" in value:
            stats = pd.DataFrame(data)["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H4("Summary of Data", className="card-title"),
                    html.H6(f"Mean:{stats[1]:.2f}", className="card-subtitle"),
                    html.H6(f"Median:{stats[5]:.2f}", className="card-subtitle"),
                    html.H6(f"Standard Deviation:{stats[2]:.2f}", className="card-subtitle"),
                    html.H6(f"Minimum:{stats[3]:.2f}", className="card-subtitle"),
                    html.H6(f"Maximum:{stats[7]:.2f}", className="card-subtitle"),
                ]
            )
    return ""

@app.callback(
    Output("schoolFacultyGraph", "figure"),
    [Input("schoolGraph", "clickData"),
    Input("schoolTable", "data"),
    Input("facultyFilter", "value"),
    Input("school", "children")]
)
def displayFacultyGraph(clickData, data, facultyFilter, school):
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    if clickData is not None:
        faculty = clickData["points"][0]["x"]
        df = df.loc[df["Faculty"] == faculty]
        fig = px.box(df, x="Course", y="Mark", category_orders={"Course": sorted(df['Course'].unique())}, title=f"Grade Distribution By Course - {faculty}, {school}", labels={"mark": "Final Course Marks"})
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue", font_color="#90E0EF")

    if facultyFilter != "":
        fig = px.box(df, x="Course", y="Mark",  category_orders={"Course": sorted(df['Course'].unique())}, title=f"Grade Distribution By Course - {df['Course'].unique().tolist()[0]}, {school}", labels={"mark": "Final Course Marks"})
        return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue",
                                 font_color="#90E0EF")
    return {}

@app.callback(
    Output("schoolFacultyGraphCard", "children"),
    Input("schoolGraphOptions", "value"),
    Input("schoolFacultyGraph", "figure"),
    Input("schoolTable", "data")
)
def showFacultyStatistics(value, figure, data):
    if value is not None and figure != {}:
        if "Show Statistics" in value:
            courses = list(set(figure["data"][0]["x"]))
            df = pd.DataFrame(data)
            stats = df.loc[df["Course"].isin(courses)]["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H4("Summary of Data", className="card-title"),
                    html.H6(f"Mean:{stats[1]:.2f}", className="card-subtitle"),
                    html.H6(f"Median:{stats[5]:.2f}", className="card-subtitle"),
                    html.H6(f"Standard Deviation:{stats[2]:.2f}", className="card-subtitle"),
                    html.H6(f"Minimum:{stats[3]:.2f}", className="card-subtitle"),
                    html.H6(f"Maximum:{stats[7]:.2f}", className="card-subtitle"),
                ]
            )
    return ""

@app.callback(
    Output("schoolCourseGraph", "figure"),
    Input("schoolCourseGraph", "figure"),
    Input("schoolFacultyGraph", "clickData"),
    Input("schoolTable", "data"),
    Input("courseNameFilter", "value"),
    Input("school", "children")
)
def displayCourseGraph(figure, clickData, data, courseFilter, school):
    df = pd.DataFrame(data)
    if df.empty:
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
                    return {}
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
    if value is not None and figure != {}:
        if "Show Statistics" in value:
            courses = figure["layout"]["title"]["text"].split(" Grade", 1)[0].replace("'", "").replace("{", "").replace("}", "").split(", ")
            print(courses)
            df = pd.DataFrame(data)
            stats = df.loc[df["Course"].isin(courses)]["Mark"].describe()
            return dbc.CardBody(
                [
                    html.H4("Summary of Data", className="card-title"),
                    html.H6(f"Mean:{stats[1]:.2f}", className="card-subtitle"),
                    html.H6(f"Median:{stats[5]:.2f}", className="card-subtitle"),
                    html.H6(f"Standard Deviation:{stats[2]:.2f}", className="card-subtitle"),
                    html.H6(f"Minimum:{stats[3]:.2f}", className="card-subtitle"),
                    html.H6(f"Maximum:{stats[7]:.2f}", className="card-subtitle"),
                ]
            )
    return ""
