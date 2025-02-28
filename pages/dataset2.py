import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import io
import base64

dash.register_page(__name__, path="/visualisation_2_sep", title="Visualisation: 2 Separate Graphs", name="Visualisation: 2 Separate Graphs", order=1)

# Initialize global variables for datasets and names
df = pd.DataFrame()
df_1 = pd.DataFrame()
df_name = "Dataset 1"
df_1_name = "Dataset 2"

# Layout
layout = html.Div([
    # Upload sections for datasets
    html.Div([
        html.Div([
            html.H4("Upload Dataset 1"),
            dcc.Upload(
                id='upload-dataset-1',
                children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                style={
                    'width': '50%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin-bottom': '20px'
                },
                multiple=False
            ),
        html.Div(id='upload-feedback-1', style={'textAlign': 'center', 'color': 'green'}),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            html.H4("Upload Dataset 2"),
            dcc.Upload(
                id='upload-dataset-2',
                children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                style={
                    'width': '50%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin-bottom': '20px'
                },
                multiple=False
            ),
        html.Div(id='upload-feedback-2', style={'textAlign': 'center', 'color': 'green'}),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ]),

    # Graph section
    html.Div([
        # Graph for Dataset 1
        html.Div([
            html.H2(id='title-dataset-1', children=f"{df_name} Graph"),
            html.Label("Select Graph Type:"),
            html.Br(),
            dcc.Dropdown(
                id='graph-type-1',
                options=[
                    {'label': 'Line Graph', 'value': 'line'},
                    {'label': 'Scatter Plot', 'value': 'scatter'},
                    {'label': 'Histogram', 'value': 'histogram'},
                    {'label': 'Bar Graph', 'value': 'bar'},
                    {'label': 'Heatmap', 'value': 'heatmap'}
                ],
                placeholder="Select Graph Type",
                style={'width': '200px'}
            ),
            html.Div([
                html.Label("Scatter Mode:"),
                dcc.Dropdown(
                    id='scatter-mode-comp-1',
                    options=[
                        {'label': 'Markers', 'value': 'markers'},
                        {'label': 'Lines+Markers', 'value': 'lines+markers'}
                    ],
                    value='markers',
                    style={'width': '200px'}
                )
            ], id='scatter-mode-group-comp-1', style={'display': 'none'}),
            
            html.Div([
                html.Label("Marker Size:"),
                dcc.Slider(
                    id='marker-size-comp-1',
                    min=1, max=20, step=1, value=6,
                    marks={i: str(i) for i in range(1, 21, 2)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='marker-size-group-comp-1', style={'display': 'none'}),
            
            html.Div([
                html.Label("Marker Opacity:"),
                dcc.Slider(
                    id='marker-opacity-comp-1',
                    min=0, max=1, step=0.1, value=0.8,
                    marks={i/10: f"{i/10:.1f}" for i in range(0, 11, 2)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='marker-opacity-group-comp-1', style={'display': 'none'}),
            
            html.Div([
                html.Label("Line Thickness:"),
                dcc.Slider(
                    id='line-thickness-1',
                    min=1, max=10, step=1, value=2,
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='line-thickness-group-1', style={'display': 'none'}),

            html.Label("Select X-axis:"),
            html.Br(),
            dcc.Dropdown(
                id='x-axis-1',
                options=[],
                placeholder="Select X-axis",
                style={'width': '200px'}
            ),
            html.Label("Select Y-axis"),
            html.Br(),
            dcc.Dropdown(
                id='y-axis-1',
                options=[],
                placeholder="Select Y-axis",
                style={'width': '200px'}
            ),
            dcc.Graph(id='graph-dataset-1')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        # Graph for Dataset 2
        html.Div([
            html.H2(id='title-dataset-2', children=f"{df_1_name} Graph"),
            html.Label("Select Graph Type:"),
            html.Br(),
            dcc.Dropdown(
                id='graph-type-2',
                options=[
                    {'label': 'Line Graph', 'value': 'line'},
                    {'label': 'Scatter Plot', 'value': 'scatter'},
                    {'label': 'Histogram', 'value': 'histogram'},
                    {'label': 'Bar Graph', 'value': 'bar'},
                    {'label': 'Heatmap', 'value': 'heatmap'}
                ],
                placeholder="Select Graph Type",
                style={'width': '200px'}
            ),
            html.Div([
                html.Label("Scatter Mode:"),
                dcc.Dropdown(
                    id='scatter-mode-comp-2',
                    options=[
                        {'label': 'Markers', 'value': 'markers'},
                        {'label': 'Lines+Markers', 'value': 'lines+markers'}
                    ],
                    value='markers',
                    style={'width': '200px'}
                )
            ], id='scatter-mode-group-comp-2', style={'display': 'none'}),
            
            html.Div([
                html.Label("Marker Size:"),
                dcc.Slider(
                    id='marker-size-comp-2',
                    min=1, max=20, step=1, value=6,
                    marks={i: str(i) for i in range(1, 21, 2)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='marker-size-group-comp-2', style={'display': 'none'}),
            
            html.Div([
                html.Label("Marker Opacity:"),
                dcc.Slider(
                    id='marker-opacity-comp-2',
                    min=0, max=1, step=0.1, value=0.8,
                    marks={i/10: f"{i/10:.1f}" for i in range(0, 11, 2)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='marker-opacity-group-comp-2', style={'display': 'none'}),
            
            html.Div([
                html.Label("Line Thickness:"),
                dcc.Slider(
                    id='line-thickness-2',
                    min=1, max=10, step=1, value=2,
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={'placement': 'bottom'}
                )
            ], id='line-thickness-group-2', style={'display': 'none'}),
            html.Label("Select X-axis:"),
            dcc.Dropdown(
                id='x-axis-2',
                options=[],
                placeholder="Select X-axis",
                style={'width': '200px'}
            ),
            html.Label("Select Y-axis"),
            html.Br(),
            dcc.Dropdown(
                id='y-axis-2',
                options=[],
                placeholder="Select Y-axis",
                style={'width': '200px'}
            ),
            dcc.Graph(id='graph-dataset-2')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    #home
    html.Div([
        html.A(
            "Back to home",
            href="/",
            style={
                'textAlign': 'center',
                'display': 'block',
                'margin': '20px auto',
                'fontSize': '18px',
                'color': 'blue',
                'textDecoration': 'none'
            }
        )
    ])
])

# Helper function to parse uploaded file content
def parse_upload(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(f"Error parsing file {filename}: {e}")
    return pd.DataFrame()

@callback(
    [Output('upload-feedback-1', 'children'),
     Output('title-dataset-1', 'children'),
     Output('x-axis-1', 'options'),
     Output('y-axis-1', 'options'),
     Output('x-axis-1', 'value'),  # Add this
     Output('y-axis-1', 'value')],  # Add this
    [Input('upload-dataset-1', 'contents')],
    [State('upload-dataset-1', 'filename')]
)

def update_dataset_1(contents, filename):
    global df, df_name
    upload_message = "Dataset 1 Graph"
    options = []
    x_value = None
    y_value = None
    if contents:
        df = parse_upload(contents, filename)
        if not df.empty:
            df_name = filename.split('.')[0]
            options = [{'label': col, 'value': col} for col in df.columns]
            x_value = options[0]['value'] if options else None
            y_value = options[1]['value'] if len(options) > 1 else None
            upload_message = "Upload successful"
        else:
            upload_message = "Failed to load dataset (empty or invalid file)."
    else:
        upload_message = "Please upload a dataset."

    # Ensure all outputs are always returned
    return upload_message, f"{df_name} Graph", options, options, x_value, y_value

# Callbacks for Dataset 2 upload
@callback(
    [
        Output('upload-feedback-2', 'children'),
        Output('title-dataset-2', 'children'),
        Output('x-axis-2', 'options'),
        Output('y-axis-2', 'options'),
        Output('x-axis-2', 'value'),
        Output('y-axis-2', 'value')
    ],
    Input('upload-dataset-2', 'contents'),
    State('upload-dataset-2', 'filename')
)
def update_dataset_2(contents, filename):
    global df_1, df_1_name
    upload_message = "Dataset 2 Graph"
    options = []
    x_value = None
    y_value = None

    if contents:
        df_1 = parse_upload(contents, filename)
        if not df_1.empty:
            df_1_name = filename.split('.')[0]
            options = [{'label': col, 'value': col} for col in df_1.columns]
            x_value = options[0]['value'] if options else None
            y_value = options[1]['value'] if len(options) > 1 else None
            upload_message = "Upload successful"
        else:
            upload_message = "Failed to load dataset (empty or invalid file)."
    else:
        upload_message = "Please upload a dataset."

    return upload_message, f"{df_1_name} Graph", options, options, x_value, y_value

#callbacks for visibility for dataset 1

@callback(
    Output('scatter-mode-group-comp-1', 'style'),
    Output('marker-size-group-comp-1', 'style'),
    Output('marker-opacity-group-comp-1', 'style'),
    Output('line-thickness-group-1', 'style'),
    Input('graph-type-1', 'value')
)
def toggle_controls_1(graph_type):
    hidden = {'display': 'none'}
    visible = {'display': 'block'}
    if graph_type == 'scatter':
        return visible, visible, visible, visible
    elif graph_type == 'line':
        return hidden, hidden, hidden, visible
    else:
        return hidden, hidden, hidden, hidden
    
#callbacks for visibility for dataset 2
@callback(
    Output('scatter-mode-group-comp-2', 'style'),
    Output('marker-size-group-comp-2', 'style'),
    Output('marker-opacity-group-comp-2', 'style'),
    Output('line-thickness-group-2', 'style'),
    Input('graph-type-2', 'value')
)
def toggle_controls_2(graph_type):
    hidden = {'display': 'none'}
    visible = {'display': 'block'}
    if graph_type == 'scatter':
        return visible, visible, visible, visible
    elif graph_type == 'line':
        return hidden, hidden, hidden, visible
    else:
        return hidden, hidden, hidden, hidden

# Callbacks for Dataset 1 graph
@callback(
    Output('graph-dataset-1', 'figure'),
    [Input('graph-type-1', 'value'),
     Input('x-axis-1', 'value'),
     Input('y-axis-1', 'value')]
)
def update_graph_1(graph_type, x_col, y_col):
    if not df.empty and graph_type and x_col and y_col:
        if graph_type == 'line':
            return px.line(df, x=x_col, y=y_col, title=f"{df_name} - Line Graph")
        elif graph_type == 'scatter':
            return px.scatter(df, x=x_col, y=y_col, title=f"{df_name} - Scatter Plot")
        elif graph_type == 'histogram':
            return px.histogram(df, x=x_col, title=f"{df_name} - Histogram")
        elif graph_type == 'bar':
            return px.bar(df, x=x_col, y=y_col, title=f"{df_name} - Bar Graph")
        elif graph_type == 'heatmap':
            try:
                pivot = df.pivot_table(index=y_col, columns=x_col, aggfunc='size', fill_value=0)
                return px.imshow(pivot, labels={'color': 'Frequency'}, title=f"{df_name} - Heatmap")
            except Exception as e:
                print(f"Error creating heatmap: {e}")
    return {}

# Callbacks for Dataset 2 graph
@callback(
    Output('graph-dataset-2', 'figure'),
    [Input('graph-type-2', 'value'),
     Input('x-axis-2', 'value'),
     Input('y-axis-2', 'value')]
)
def update_graph_2(graph_type, x_col, y_col):
    if not df_1.empty and graph_type and x_col and y_col:
        if graph_type == 'line':
            return px.line(df_1, x=x_col, y=y_col, title=f"{df_1_name} - Line Graph")
        elif graph_type == 'scatter':
            return px.scatter(df_1, x=x_col, y=y_col, title=f"{df_1_name} - Scatter Plot")
        elif graph_type == 'histogram':
            return px.histogram(df_1, x=x_col, title=f"{df_1_name} - Histogram")
        elif graph_type == 'bar':
            return px.bar(df_1, x=x_col, y=y_col, title=f"{df_1_name} - Bar Graph")
        elif graph_type == 'heatmap':
            try:
                pivot = df_1.pivot_table(index=y_col, columns=x_col, aggfunc='size', fill_value=0)
                return px.imshow(pivot, labels={'color': 'Frequency'}, title=f"{df_1_name} - Heatmap")
            except Exception as e:
                print(f"Error creating heatmap: {e}")
    return {}