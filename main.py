import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd

from dash import dash, dash_table, html, dcc, Output, Input
from dash.exceptions import PreventUpdate

# creates the dash application opject
app = dash.Dash(__name__)
server = app.server

# importing datasets
df1 = pd.read_csv("dataset/games.csv")
df2 = pd.read_csv("dataset/Video_game_films.csv")

auth = dash_auth.BasicAuth(
    app,
    {"legenden": "qwe123"}
)

# layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Button("Load Data", id="load-btn", n_clicks=0,)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Popular Video Games 1980 - 2023 "),
                        dag.AgGrid(
                            id="ag_grid",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                            }
                        ),
                        html.H1("Film Adaptations of Video Games"),
                        dag.AgGrid(
                            id="ag_grid_2",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "filter": "agTextColumnFilter",
                                "floatingFilter": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                            }
                        ),
                    ]
                )
            ]
        ),
    ]
)

# callbacks
@app.callback(
    [
        Output(component_id="ag_grid", component_property="rowData"),
        Output(component_id="ag_grid", component_property="columnDefs"),
        Output(component_id="ag_grid_2", component_property="rowData"),
        Output(component_id="ag_grid_2", component_property="columnDefs"),
    ],
    [
        Input(component_id="load-btn", component_property="n_clicks")
    ]
)
def update_output(n_clicks):
    if n_clicks <= 0:
        raise PreventUpdate
    else:
        columnDefs_df1 = [{"field": col} for col in df1.columns]
        rowData_df1 = df1.to_dict("records")
        columnDefs_df2 = [{"field": col} for col in df2.columns]
        rowData_df2 = df2.to_dict("records")

    return rowData_df1, columnDefs_df1, rowData_df2, columnDefs_df2


if __name__ == '__main__':
    app.run_server(debug=True)