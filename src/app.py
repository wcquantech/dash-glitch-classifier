from dash import Dash, dcc, html, Input, Output, callback_context as ctx
import dash_bootstrap_components as dbc
import dash_uploader as du
import time
import uuid

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.COSMO, dbc.icons.FONT_AWESOME], 
           suppress_callback_exceptions=True
           )

app.title = "GW Glitch Classifier"

about = html.Div([
    html.H1("About This App"),
    html.P("This app is a simple web application that allows you to upload a gravitational wave signal and classify it as a glitch or not a glitch.")
])

classifier_content = html.Div([
    html.Div([
        html.H4("1. Please upload a .hdf5 file of strain data from GWOSC"),
        html.Div([
            html.P([
                "Hint: You can download the public strain data from ", 
                html.A('Gravitational Wave Open Science Center', href='https://www.gw-openscience.org/data', target='_blank')
            ]),
            dbc.Container(
                du.Upload(
                    id="strain-uploader",
                    text="Drag or Click",
                    upload_id=uuid.uuid4(),
                    filetypes=["hdf5"],
                    max_files=1,
                    disabled=False
                )
            )
        ]),
    ]),
    html.Div([
        html.H4("2. Select a model for glitch classification"),
        dcc.Dropdown(
            id="model-dropdown",
            options=[
                {"label": "Model 1", "value": "model1"},
                {"label": "Model 2", "value": "model2"},
            ],
            value="model1"
        ),
    ]),
    html.Div([
        html.H4("3. Select your interested time of the strain data"),
        html.Div([
            html.Button([
                html.I(className="fa-solid fa-minus")
            ], id="time-slider-minus", n_clicks=0),
            dcc.Slider(
                id="time-slider",
                min=2,
                max=4094,
                step=0.1,
                included=False,
                marks=None,
                value=2048,
                tooltip={"always_visible": True, "placement": "bottom"}
            ),
            html.Button([
                html.I(className="fa-solid fa-plus")
            ], id="time-slider-plus", n_clicks=0)
        ], className="time-slider-div")
    ]),
    html.Div([
        html.H4("4. Data preview"),
        html.Div(id="data-preview", children=[])
    ]),
    html.Div([
        html.H4("5. Prediction"),
        html.P("Multi-duration Q-Transformed spectrogram of the selected time", style={"text-align": "center"}),
        html.Div(id="prediction", children=[])
    ])

], className="classifier-content")

classifier = html.Div([
    html.H1("Classifier"),
    html.Div(id="classifier-content", children=classifier_content)
])



page = html.Div([
    html.Nav([
        html.H2("GW Glitch Classifier"),
        html.Div([
            html.Button("About This App", id="about", n_clicks=0),
            html.Button("Classifier", id="classifier", n_clicks=0)
        ], className="nav-bar-buttons")
    ], className="nav-bar"),
    html.Div(id="page-content", children=[])
], className="page")




app.layout = page


@app.callback(Output("page-content", "children"),
              Input("about", "n_clicks"),
              Input("classifier", "n_clicks"))
def page_change(about_n_clicks, classifier_n_clicks):
    if not ctx.triggered:
        return classifier
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "about":
        return about
    elif button_id == "classifier":
        return classifier
    else:
        return html.P("This page does not exist.")


if __name__ == "__main__":
    app.run_server(debug=True)