import dash_ag_grid as dag
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3

from dash import dash, html, dcc, Output, Input, State, no_update
from dash.exceptions import PreventUpdate


# importing datasets into pandas
df1 = pd.read_csv("datasets/games.csv")
df2 = pd.read_csv("datasets/video_game_films.csv")

# dropping duplicate entries
df1 = df1.drop_duplicates(subset=["Title"])
df2 = df2.drop_duplicates(subset=["Title"])

# Remove rows where Release Date is "releases on TBD"
df1 = df1.drop(df1[df1["Release Date"] == "releases on TBD"].index)

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
df2.to_sql("movies", conn, if_exists="replace", index=False)

df_sql_games = pd.read_sql_query("SELECT * FROM games", conn)
df_sql_movies = pd.read_sql_query("SELECT * FROM movies", conn)

conn.close()

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
                dbc.Button("SQL Query", id="load-btn", n_clicks=0,),
                html.Div(
                    [
                        html.H1("Search"),
                        html.Div(
                            [
                                dcc.Textarea(
                                    id="textarea",
                                    placeholder="Search...",
                                ),
                                html.Button(
                                    "Search",
                                    id="sql-search",
                                    n_clicks=0,
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Popular Video Games 1980 - 2023, and movie adaptions"),
                        dag.AgGrid(
                            id="ag_grid",
                            columnDefs=[{"field": col} for col in df_sql_games.columns],
                            rowData=df_sql_games.to_dict("records"),
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                                "filter": True,
                                "floatingFilter": True
                            }
                        ),
                        html.H1("Film Adaptations of Video Games"),
                        dag.AgGrid(
                            id="ag_grid-2",
                            columnDefs=[{"field": col} for col in df_sql_movies.columns],
                            rowData=df_sql_movies.to_dict("records"),
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                                "filter": True,
                                "floatingFilter": True
                            }
                        ),
                        html.H1("SQL QUERY"),
                        dag.AgGrid(
                            id="ag-sql",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "minWidth": 100,
                                "editable": True,
                                "resizable": True,
                                "flex": 1,
                                "wrapHeaderText": True,
                                "filter": True,
                                "floatingFilter": True
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
        Output(component_id="ag-sql", component_property="rowData"),
        Output(component_id="ag-sql", component_property="columnDefs"),
    ],
    Input(component_id="sql-search", component_property="n_clicks"),
    State(component_id="textarea", component_property="value")
)
def sql_query(n_clicks, textarea):
    conn = sqlite3.connect("database/database.db")
    conn.execute(
        '''
        DROP TABLE IF EXISTS query_result
        '''
    )
    conn.execute(
        '''
        CREATE TABLE query_result (
            Title TEXT
            Release Date DATETIME
        )
        '''
    )
    df_sql_games = pd.read_sql_query(f"SELECT Title FROM games WHERE Title LIKE '%{textarea}%'", conn)
    df_sql_movies = pd.read_sql_query(f"SELECT Title FROM movies WHERE Title LIKE '%{textarea}%'", conn)

    if df_sql_games.empty:
        no_update, no_update

    query = df_sql_movies.to_dict("records")

    columnDefs = [{"field": col} for col in df_sql_movies.columns]
    conn.close()

    return query, columnDefs

if __name__ == '__main__':
    app.run_server(debug=True)