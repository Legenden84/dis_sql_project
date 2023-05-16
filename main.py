import pandas as pd

from dash import dash, dash_table, html, dcc
import dash_auth

# creates the dash application opject
app = dash.Dash(__name__)
server = app.server

auth = dash_auth.BasicAuth(
    app,
    {"legenden": "qwe123"}
)

if __name__ == '__main__':
    app.run_server(debug=True)