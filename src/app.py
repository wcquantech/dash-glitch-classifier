from dash import Dash, dcc, html, Input, Output, State, callback_context as ctx, no_update
import dash_bootstrap_components as dbc
import dash_uploader as du
from dash.exceptions import PreventUpdate
import os
import uuid
from dotenv import load_dotenv
from helpers import find_gps, plot_4s_strain, plot_final_spectrogram
from classifier import classify

load_dotenv()

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.COSMO, dbc.icons.FONT_AWESOME], 
           suppress_callback_exceptions=True
           )

server = app.server

app.title = "GW Glitch Classifier"

# Global variables
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
project_directory = os.path.dirname(current_directory)
upload_path = os.environ.get('UPLOAD_PATH')
du.configure_upload(app, os.path.join(project_directory, upload_path))
gps = 0
strain_path = ""

# Define the class names
glitch_class_list = [
    "1080Lines", "1400Ripples", "Air_Compressor", "Blip", "Chirp", "Extremely_Loud", "Helix",
    "Koi_Fish", "Light_Modulation", "Low_Frequency_Burst", "Low_Frequency_Lines", "No_Glitch",
    "Paired_Doves", "Power_Line", "Repeating_Blips", "Scattered_Light", "Scratchy", "Tomte",
    "Violin_Mode", "Wandering_Light", "Whistle"
]

about = html.Div([
    html.H1("About This App"),
    html.Br(),
    html.H2("Background"),
    html.P([
        "This app is a simple web application that allows you to upload a gravitational wave signal (in HDF5 format) and classify it into one of the ",
        html.A("23 classes of glitches (including 'No Glitch')", href="https://arxiv.org/pdf/2208.12849.pdf#pagemode=thumbs"),
        "."
    ]),
    html.P([
        "Glitches are noise signals recorded in auxiliary channels by the Michelson interferometers during the gravitational wave detection. " + 
        "The presence of glitches surrounding the candidate events will negatively impact the searching sensitivity of potential gravitational wave events. " + 
        "Due to the importance of identification and removal of glitches signals from the strain data, a science project called ",
        html.A("Gravity Spy", href="https://www.zooniverse.org/projects/zooniverse/gravity-spy/about/research", target="_blank"),
        " was hosted on the Zooniverse platform, " +
        "aims to gather knowledge from citizens and scientists around the world to improve the efficiency and accuracy in glitch classification problem using deep learning methods. "
    ]),
    html.P([
        "The app uses pre-trained deep learning models to classify the signal. These models were trained by Jianqi Yan and Alex P Leung, " + 
            "utilizing Generative Adversarial Networks (GANs) to augment the original Gravity Spy dataset with additional training data. " +
            "For more detailed insights, we encourage users to explore their works ",
        html.Span("'On improving the performance of glitch classification for gravitational wave detection by using Generative Adversarial Networks'", style={"font-weight": "bold"}),
            ", available at ",
        html.A("@https://doi.org/10.1093/mnras/stac1996", href="https://doi.org/10.1093/mnras/stac1996", target="_blank"),
        "."
    ]),
    html.Br(),
    html.H2("How to use this app"),
    html.P("To use this app, you need to follow the steps below:"),
    html.Ul([
        html.Li(html.Span(["Upload a .hdf5 file of strain data from ", html.A('Gravitational Wave Open Science Center (GWOSC)', href='https://www.gw-openscience.org/data', target='_blank')])),
        html.Li("Select a model for glitch classification"),
        html.Li("Select your interested time of the strain data"),
        html.Li("Click the 'Submit' button to see the multi-duration (1.0s + 2.0s + 4.0s) Q-Transformed spectrogram of the selected time and the classification result")
    ])
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
                {"label": "Inception-V3", "value": "Inception-V3"},
                {"label": "GoogLeNet", "value": "GoogLeNet"},
            ],
            value="Inception-V3",
            clearable=False
        ),
    ]),
    html.Div([
        html.H4("3. Select your interested time of the strain data"),
        html.Div([
            html.Div([
                html.Button("-1", id="time-slider-minus-1", n_clicks=0, disabled=True),
                html.Button("-0.1", id="time-slider-minus-01", n_clicks=0, disabled=True),
            ], className="time-slider-buttons"),
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
            html.Div([
                html.Button("+0.1", id="time-slider-plus-01", n_clicks=0, disabled=True),
                html.Button("+1", id="time-slider-plus-1", n_clicks=0, disabled=True)
            ], className="time-slider-buttons")
        ], className="time-slider-div"),
        html.Div([
            html.H5(f"GPS Time: -", id="gps-time")
        ], className="time-input-div")
    ]),
    html.Div([
        html.H4("4. Data preview"),
        dbc.Spinner(html.Div(id="data-preview", children=[]), color="primary"),
    ]),
    html.Div([
        html.H4("5. Glitch classification"),
        dbc.Spinner(html.Div(id="classification-result", children=[]), color="primary")
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
        return about
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
              Output("time-slider-minus-01", "disabled"),
              Output("time-slider-plus-01", "disabled"),
              Output("time-slider-minus-1", "disabled"),
              Output("time-slider-plus-1", "disabled"),
              Input("strain-uploader", "isCompleted"),
              Input("strain-uploader", "upload_id"),
              Input("strain-uploader", "fileNames"))
def strain_upload(isCompleted, upload_id, fileNames):
    global strain_path
    global gps
    if isCompleted:
        strain_path = os.path.join(upload_path, str(upload_id), fileNames[0])
        gps = find_gps(strain_path)
        return False, True, False, False, False, False
    return no_update, no_update, no_update, no_update, no_update, no_update

# Handle showing GPS time
@app.callback(Output("gps-time", "children"),
              Input("time-slider", "value"))
def update_gps_time(value):
    global gps
    if gps == 0:
        return "GPS: -"
    return f"GPS Time: {gps + value}"

# Handle time buttons
@app.callback(Output("time-slider", "value"),
              Input("time-slider-minus-1", "n_clicks"),
              Input("time-slider-minus-01", "n_clicks"),
              Input("time-slider-plus-1", "n_clicks"),
              Input("time-slider-plus-01", "n_clicks"),
              State("time-slider", "value"))
def time_update(minus_1_n_clicks, minus_01_n_clicks, plus_1_n_clicks, plus_01_n_clicks, value):
    if not ctx.triggered:
        return no_update
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "time-slider-minus-1":
        if value-1 >= 2:
            return value - 1
        else: 
            return value
    elif button_id == "time-slider-minus-01":
        if value-0.1 >= 2:
            return value - 0.1
        else: 
            return value
    elif button_id == "time-slider-plus-1":
        if value+1 <= 4094:
            return value + 1
        else:
            return value
    elif button_id == "time-slider-plus-01":
        if value+0.1 <= 4094:
            return value + 0.1
        else:
            return value
    else:
        return no_update

# Handle data preview
@app.callback(Output("data-preview", "children"),
              Input("time-slider", "value"))
def data_preview(value):
    global strain_path
    if value:
        try:
            image = plot_4s_strain(strain_path, value-2, value+2)
            return [
                html.Img(src=image),
                html.Button("Submit", id="submit", n_clicks=0)
            ]
        except Exception as e:
            return f"Error: {e}. Please try again."
    return no_update

# Handle multi-duaration Q transform and classification
@app.callback(Output("classification-result", "children"),
              Input("submit", "n_clicks"),
              Input("time-slider", "value"),
              Input("model-dropdown", "value"))
def classification(n_clicks, value, model):
    global strain_path
    global gps
    if not n_clicks:
        raise PreventUpdate
    try:
        imgsrc = plot_final_spectrogram(hdf5=strain_path, start=value-2, end=value+2)
        buf = plot_final_spectrogram(hdf5=strain_path, start=value-2, end=value+2, to_predict=True)
        prediction, prob_1, prob_2 = classify(model, buf, glitch_class_list)

        text = html.Div([
            html.P("Multi-duration Q-Transformed spectrogram of the selected time:"),
            html.P(f"{(value-2):.1f}s to {(value+2):.1f}s from GPS time {gps}")
        ])
        if prob_2 is None:
            msg = html.Div([html.P("{} ({:.3%})".format(prediction, prob_1))])
        else:
            msg = html.Div([
                html.P("{} ({:.3%})".format(prediction, prob_1)),
                html.P("{} ({:.3%})".format(prob_2[1], prob_2[0]))
            ])
    except Exception as e:
        return f"Error: {e}. Please try again."
    return [text, html.Img(src=imgsrc), msg]



if __name__ == "__main__":
    app.run()