from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from home import home_layout
from school import school_layout
from app import app

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
}

selectedTabStyle = {
    "background": '#7FDBFF',
    'color': 'white',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding': '6px'
}

app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Home", tab_id="homeTab", active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="Queens University", tab_id="QueensUniversityTab", active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="University of Toronto", tab_id="UniversityofTorontoTab",
                        active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="University of Waterloo", tab_id="UniversityofWaterlooTab",
                        active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="University of Western Ontario", tab_id="UniversityofWesternOntarioTab",
                        active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="Wilfred Laurier University", tab_id="WilfredLaurierUniversityTab",
                        active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
                dbc.Tab(label="York University", tab_id="YorkUniversityTab", active_tab_style=selectedTabStyle,
                        labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger",
                        tab_style={"padding": "5px"}),
            ],
            id="tabs",
            active_tab="homeTab",
        ),
    ], className="mt-3"
)

app.layout = html.Div([
    html.Div(children=[

        html.Div("", id="school", style={"color": "black"}),

        html.H1(
            children='GradeTrack',
        ),

        html.H5(
            children="Ontario University Course Averages"),

        dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    ]),

    html.Div(id='content', children=[]),
], style={'backgroundColor': colors['background'], "color": colors['text'], "textAlign": "center",
          "font-family": 'Trebuchet MS', "padding": "10px"})

@app.callback(
    Output("school", "children"),
    Output("content", "children"),
    Input("tabs", "active_tab"),
)
def switch_tab(tab_chosen):
    if tab_chosen == "homeTab":
        return "", home_layout
    elif tab_chosen == "QueensUniversityTab":
        return "Queens University", school_layout
    elif tab_chosen == "UniversityofTorontoTab":
        return "University of Toronto", school_layout
    elif tab_chosen == "UniversityofWaterlooTab":
        return "University of Waterloo", school_layout
    elif tab_chosen == "UniversityofWesternOntarioTab":
        return "University of Western Ontario", school_layout
    elif tab_chosen == "WilfredLaurierUniversityTab":
        return "Wilfred Laurier University", school_layout
    elif tab_chosen == "YorkUniversityTab":
        return "York University", school_layout

if __name__ == '__main__':
    app.run_server(debug=True)
