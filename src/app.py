from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import dash_uploader as du
import time

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

page = html.Div([
    html.Br(),
    html.H1("Glitch Classifier", style={"textAlign": "center"})
])

app.layout = page

if __name__ == "__main__":
    app.run_server(debug=True)