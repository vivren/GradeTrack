from dash import Dash, html, dcc, Input, Output, dash_table, State
import plotly.express as px
import pandas as pd

app = Dash(__name__)

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

    dash_table.DataTable(
        id="Grades Table",
        columns=[{'name': 'School', 'id': 'School'},
                {'name': 'Course', 'id': 'Course'},
                {'name': 'Mark', 'id': 'Mark', 'type': 'numeric'}],
        data=[{'School': 'Western', 'Course': 'CS1026', 'Mark': 91},
            {'School': 'Western', 'Course': 'CS1026', 'Mark': 85},
            {'School': 'Western', 'Course': 'CS1026', 'Mark': 62},
            {'School': 'Western', 'Course': 'CS1027', 'Mark': 73},
            {'School': 'Western', 'Course': 'CS1027', 'Mark': 99}],
        editable=True,
        row_deletable=False,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_action="none",
        style_table={"height": "300px", "overflowY": "auto"},
        style_cell={'textAlign': 'left', "minWidth": "100px", "width": "100px", "maxWidth": "100px"}
        ),

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
    #     html.Label('Text Input'),
    #     dcc.Input(value='MTL', type='text'),
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

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

@app.callback(
    Output("Grades Table", 'data'),
    Input("Add mark button", "n_clicks"),
    Input("Grades Table", "data"),
    Input("Grades Table", "columns"),
    Input("schoolInput", "value"),
    Input("courseInput", "value"),
    Input("gradeInput", "value"),
)
def add_rows(n_clicks, data, columns, schoolInput, courseInput, gradeInput):
    if n_clicks > 0:
        #data.append({c['id']: schoolInput for c in columns})
        data.append({"School": schoolInput, "Course": courseInput, "Mark": gradeInput})
    return data

@app.callback(
    Output("graph", "figure"),
    [Input("Grades Table", "data")])
def display_graph(data):
    df_fig = pd.DataFrame(data)
    fig = px.box(df_fig, x="Course", y="Mark")
    return fig

@app.callback(
    Output("schoolInput", "value"),
    # Output("courseInput", "value"),
    # Output("gradeInput", "value"),
    Input("Clear input button", "n_clicks")
)
def clearInput(n_clicks):
    if n_clicks > 0:
        return tuple("")

if __name__ == '__main__':
    app.run_server(debug=True)
