from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import re
from app import app
from models import School, Faculty, Course, Mark, db

colors = {
    'background': '#001D3D',
    "text": "#48CAE4",
}

home_layout = html.Div([

    dbc.Row([
        dbc.Col(
            dbc.DropdownMenu([],
                id="homeSchoolInput",
                label="School",
                toggle_style={"background": "#FFFFFF", "color": "#0096C7", "padding-top": "10px", "width": "150px"},
            )
        ),
        dbc.Col(
            dbc.DropdownMenu([],
                id="homeFacultyInput",
                label="Faculty",
                toggle_style={"background": "#FFFFFF", "color": "#0096C7", "padding-top": "10px", "width": "150px"},
            )
        ),
        dbc.Col(
            dbc.Input(
                id="homeCourseInput",
                placeholder="Enter course code",
                value="",
                #style={"padding": 10}
            )
        ),
        dbc.Col(
            dbc.Input(
                id="homeGradeInput",
                placeholder="Enter course grade",
                value='',
                #style={"padding": 10}
            )
        ),
        dbc.Col(
            dbc.Button("Add Mark", id="addHomeMarkButton", n_clicks=0, style={"background": "#0096C7"})
        ),
        dbc.Col(
            dbc.Button("Clear Input", id="Clear input button", n_clicks=0, style={"background": "#0096C7"})
        ),
        dcc.Interval(id='interval_pg', interval=99999999 * 7, n_intervals=0)]),

    html.Div([
        dbc.Button(
            "Show Data",
            id="collapseDataButton",
            className="mb-3",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(id='homeGradesTable', children=[
                dash_table.DataTable(
                    id="homeTable",
                    columns=[],
                    data=[],
                    row_deletable=False,
                    sort_action="native",
                    sort_mode="multi",
                    sort_by=[{"column_id": "School", "direction": "asc"}, {"column_id":"Faculty", "direction":"asc"}, {"column_id":"Course", "direction":"asc"}, {"column_id":"Mark", "direction":"asc"}],
                    page_action="none",
                    style_table={"height": "300px", "overflowY": "auto"},
                    style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
                ),
            ],
        ),
            id="collapseTable",
            is_open=False,
        ),
    ]),

    html.Div([
        dcc.Graph(figure={}, id="homeGraph", clickData=None),

        dbc.Card(
            dbc.CardBody(""),
            className="mb-3",
            id="homeGraphCard",
            color=colors["background"],
            inverse=True,
            outline=True,
        ),

        dcc.Checklist(id="homeGraphOptions", options=["Show Statistics"], style={"align": "right"})
    ])
], style={'backgroundColor': colors['background'], "color": colors["text"], "font-family": "Epilogue"})

@app.callback(
    Output("collapseTable", "is_open"),
    [Input("collapseDataButton", "n_clicks")],
    [State("collapseTable", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("homeGraphCard", "children"),
    Input("homeGraphOptions", "value"),
    Input("homeTable", "data"),
)
def showStatistics(value, data):
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
    Output("homeSchoolInput", "options"),
    Input("tabs", "active_tab"),
)
def updateSchoolDropdown(activeTab):
    schools = db.session.query(School.name).all()
    schools = sorted([school for sublist in schools for school in sublist])
    return schools

@app.callback(
    Output("homeFacultyInput", "options"),
    Input("homeSchoolInput", "value"),
)
def updateFacultyDropdown(schoolInput):
    faculties = db.session.query(Faculty.name).filter(School.id == Faculty.schoolID).filter(School.name == schoolInput).all()
    faculties = sorted([faculty for sublist in faculties for faculty in sublist])
    return faculties

@app.callback(
    Output("homeTable", "data"),
    Output("homeTable", "columns"),
    Output("addHomeMarkButton", "n_clicks"),
    Input("tabs", "active_tab"),
    Input("addHomeMarkButton", "n_clicks"),
    Input("homeSchoolInput", "value"),
    Input("homeFacultyInput", "value"),
    Input("homeCourseInput", "value"),
    Input("homeGradeInput", "value"),
)
def updateHomeTable(activeTab, addClicks, schoolInput, facultyInput, courseInput, gradeInput):
    df = pd.DataFrame(db.session.query(School.name, Faculty.name, Course.courseCode, Mark.mark).join(Faculty, School.id == Faculty.schoolID).join(Course, Course.facultyID == Faculty.id).join(Mark, Mark.courseID == Course.id).all(), columns=["School", "Faculty", "Course", "Mark"])
    columns = [{'name': str(x), 'id': str(x), 'deletable': False} for x in df.columns]

    if addClicks > 0:
        tempFacultyID = db.session.query(Faculty.id).filter(School.id == Faculty.schoolID).filter(Faculty.name == facultyInput).filter(School.name == schoolInput).first()[0]

        courseExists = db.session.query(Course.id).filter(Course.courseCode == courseInput).filter(Course.facultyID == tempFacultyID).first()
        if courseExists is not None:
            tempCourseID = courseExists[0]
        else:
            tempYearLevel = re.findall('\d+|$', courseInput)[0][0]
            course = Course(courseCode=courseInput, yearLevel = tempYearLevel, facultyID=tempFacultyID)
            db.session.add(course)
            db.session.commit()
            tempCourseID = db.session.query(Course.id).filter_by(courseCode=courseInput, facultyID=tempFacultyID).first()[0]

        mark = Mark(mark=gradeInput, courseID=tempCourseID)
        db.session.add(mark)
        db.session.commit()
        df = df.append({"School": schoolInput, "Faculty": facultyInput, "Course": courseInput, "Mark": gradeInput}, ignore_index=True)

    return df.to_dict('records'), columns, 0

@app.callback(
    Output("homeGraph", "figure"),
    Input("homeTable", "data"),
    )
def display_graph(data):
    df = pd.DataFrame(data)
    fig = px.box(df, x="School", y="Mark", title="Grades by School", category_orders={"School": sorted(df['School'].unique())}, labels={"Mark": "Final Course Marks"})
    return fig.update_layout(paper_bgcolor="#001D3D", plot_bgcolor="#CAF0F8", font_family="Epilogue", font_color="#90E0EF")

# @app.callback(
#     Output("tabs", "active_tab"),
#     Input("homeGraph", "clickData"),
# )
# def switchTab(clickData):
#     if clickData is not None:
#         return clickData["points"][0]["x"].replace(" ", "") + "Tab"
#     return "homeTab"
