from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from home import home_layout
from school import school_layout
from app import app

colors = {
    'background': '#001D3D',
    "text": "#CAF0F8",
}

selectedTabStyle = {
    "background": "linear-gradient(#e66465, #9198e5)",
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
}

text = {
    "font-family": 'Sora',
}

tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Home", tab_id="homeTab", active_tab_style=selectedTabStyle, active_label_style={"colour": "0077B6"},                      tab_style={"padding": "5px"}, label_style={"colour": "#0077B6"}),
                dbc.Tab(label="Queens University", tab_id="QueensUniversityTab", active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"}, label_style={"colour": "#0077B6"}),
                dbc.Tab(label="University of Toronto", tab_id="UniversityofTorontoTab",
                        active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"},  label_style={"colour": colors["text"]}),
                dbc.Tab(label="University of Waterloo", tab_id="UniversityofWaterlooTab",
                        active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"},  label_style={"colour": colors["text"]}),
                dbc.Tab(label="University of Western Ontario", tab_id="UniversityofWesternOntarioTab",
                        active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"},  label_style={"colour": colors["text"]}),
                dbc.Tab(label="Wilfred Laurier University", tab_id="WilfredLaurierUniversityTab",
                        active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"},  label_style={"colour": colors["text"]}),
                dbc.Tab(label="York University", tab_id="YorkUniversityTab", active_tab_style=selectedTabStyle,
                        tab_style={"padding": "5px"},  label_style={"colour": "#0077B6"}),
            ],
            id="tabs",
            active_tab="homeTab",
        ),
    ],
)

app.layout = html.Div([
    html.Div(children=[

        html.Div("", id="school"),

        html.H1(children='GradeTrack'),

        html.H5(children="Ontario University Course Averages"),

        dbc.Row(tabs, justify="center"),
    ]),

    html.Div(id='content', children=[])],

    style={'backgroundColor': colors['background'], "color": colors['text'], "textAlign": "center",
        "font-family": "Sora", "padding": "10px"})

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
