import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3

from dash import dash, html, dcc, Output, Input
from dash.exceptions import PreventUpdate


# importing datasets into pandas
df1 = pd.read_csv("datasets/games.csv")
df2 = pd.read_csv("datasets/video_game_films.csv")

# Remove rows where Release Date is "releases on TBD"
df1 = df1.drop(df1[df1['Release Date'] == 'releases on TBD'].index)

# dropping deprecated column
df1.drop("Unnamed: 0", axis=1, inplace=True)

# converting datetime to format that re regognized by sql
df1["Release Date"] = pd.to_datetime(df1["Release Date"])
df1["Release Date"] = df1["Release Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
df2["Release date"] = pd.to_datetime(df2["Release date"])
df2["Release date"] = df2["Release date"].dt.strftime("%Y-%m-%d %H:%M:%S")

# setting up sql database
conn = sqlite3.connect("database/database.db")
cursor = conn.cursor()

df1.to_sql("games", conn, if_exists="replace", index=False)
df2.to_sql("adaptions", conn, if_exists="replace", index=False)

df_sql_games = pd.read_sql_query("SELECT * FROM games", conn)
df_sql_movie = pd.read_sql_query("SELECT * FROM adaptions", conn)

# creates the dash application opject
app = dash.Dash(__name__)
server = app.server

# dash auththetication
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
                        html.H1("Popular Video Games 1980 - 2023, and movie adaptions"),
                        dag.AgGrid(
                            id="ag_grid",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                            }
                        ),
                        html.H1("Film Adaptations of Video Games"),
                        dag.AgGrid(
                            id="ag_grid-2",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
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
        Output(component_id="ag_grid-2", component_property="rowData"),
        Output(component_id="ag_grid-2", component_property="columnDefs"),
    ],
    [
        Input(component_id="load-btn", component_property="n_clicks")
    ]
)
def update_output(n_clicks):
    if n_clicks <= 0:
        raise PreventUpdate
    else:
        rowData_games = df_sql_games.to_dict("records")
        columnDefs_games = [{"field": col} for col in df_sql_games.columns]
        rowData_movie = df_sql_movie.to_dict("records")
        columnDefs_movie = [{"field": col} for col in df_sql_movie.columns]
    return rowData_games, columnDefs_games, rowData_movie, columnDefs_movie

if __name__ == '__main__':
    app.run_server(debug=True)