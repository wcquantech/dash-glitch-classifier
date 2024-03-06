from dash import Dash, dcc, html, Input, Output, callback_context as ctx, no_update
import dash_bootstrap_components as dbc
import dash_uploader as du
import time
import os
import uuid
from dotenv import load_dotenv
from helpers import find_gps, plot_4s_strain, plot_final_spectrogram

load_dotenv()

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.COSMO, dbc.icons.FONT_AWESOME], 
           suppress_callback_exceptions=True
           )

app.title = "GW Glitch Classifier"

# Global variables
upload_path = os.environ.get('UPLOAD_PATH')
du.configure_upload(app, upload_path)
gps = 0
strain_path = ""

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
                    disabled=False,
                    max_file_size=1000,
                    pause_button=True,
                    text_disabled="Upload successful!",
                    text_completed="Upload successful!",
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
            ], id="time-slider-minus", n_clicks=0, disabled=True),
            dcc.Slider(
                id="time-slider",
                min=2,
                max=4094,
                step=0.1,
                included=False,
                marks=None,
                value=2048,
                disabled=True,
                tooltip={"always_visible": True, "placement": "bottom"}
            ),
            html.Button([
                html.I(className="fa-solid fa-plus")
            ], id="time-slider-plus", n_clicks=0, disabled=True)
        ], className="time-slider-div")
    ]),
    html.Div([
        html.H4("4. Data preview"),
        html.Div(id="data-preview", children=[]),
    ]),
    html.Div([
        html.H4("5. Glitch classification"),
        html.P("Multi-duration Q-Transformed spectrogram of the selected time", style={"text-align": "center"}),
        html.Div(id="classification-result", children=[])
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

# Handle page change
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
    

# Handle strain data upload
@app.callback(Output("time-slider", "disabled"),
              Output("strain-uploader", "disabled"),
              Input("strain-uploader", "isCompleted"),
              Input("strain-uploader", "upload_id"),
              Input("strain-uploader", "fileNames"))
def strain_upload(isCompleted, upload_id, fileNames):
    global strain_path
    global gps
    if isCompleted:
        strain_path = os.path.join(upload_path, str(upload_id), fileNames[0])
        gps = find_gps(strain_path)
        return False, True
    return no_update, no_update


if __name__ == "__main__":
    app.run_server(debug=True)