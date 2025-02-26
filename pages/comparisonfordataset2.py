import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import io
import base64
import numpy as np
from datetime import datetime, timedelta
import copy

# Register the page (if using multi-page app)
dash.register_page(__name__, path="/visualisation_combined", title="Visualisation: Combined Graph", name="Visualisation: Combined Graph")

# Helper functions for data cleaning and processing
def clean_data(df):
    return df.dropna()

def normalise(df):
    return (df - df.min()) / (df.max() - df.min())

# Time adjustment and interpolation logic
def adjust_time(row, base_day, base_hour):
    minutes_seconds = datetime.strptime(row, '%H:%M:%S.%f').time()
    if minutes_seconds == datetime.strptime('00:00:00.000', '%H:%M:%S.%f').time():
        base_hour += 1
    combined_time = datetime.combine(base_day, minutes_seconds) + timedelta(hours=base_hour)
    return combined_time

def convert_time(df, df1): #2nd one is redundant but works
    global base_hour
    cols = df.columns
    cols1 = df1.columns

    df[cols[0]] = pd.to_datetime(df[cols[0]], format='%Y-%m-%dT%H:%M:%S.%fZ')

    # Adjust time for df1
    base_date = df[cols[0]].iloc[0]
    base_day = base_date.date()
    base_hour = base_date.hour

    df1[f'Adjusted {cols1[0]}'] = (df1[cols1[0]].apply(adjust_time, args=(base_day, base_hour)))
    # df1.to_csv(r'c:\Users\GAdmin\Desktop\internship\Sindya\app\new.csv')

    time_ADP = df[cols[0]]
    time_emu = df1[f'Adjusted {cols1[0]}']

    # Convert datetime to seconds since epoch
    time_ADP_sec = np.array([(ts - datetime(1970, 1, 1)).total_seconds() for ts in time_ADP.to_list()], dtype=np.float64)
    time_emu_sec = np.array([(ts - datetime(1970, 1, 1)).total_seconds() for ts in time_emu.to_list()], dtype=np.float64)

    return time_ADP_sec, time_emu_sec

def interpolate(df, df1):
    time_ADP_sec, time_emu_sec = convert_time(df, df1)
    emu_df_int = copy.copy(df)
    for col in df1.columns[1:]:
        # print(col)
        # print(len(df1[col])) #debugging
        emu_df_int[col] = np.interp(time_ADP_sec, time_emu_sec, np.array(df1[col], dtype=np.float64))
        
    return emu_df_int

# Layout
layout = html.Div([
    html.H2("Comparison Graph", style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px auto',
        },
        multiple=True
    ),
    html.Div(id='upload-feedback', style={'textAlign': 'center', 'color': 'green'}),
    html.Br(),
    html.Label("Select Graph Type:"),
    dcc.Dropdown(
        id='graph-type',
        options=[
            {'label': 'Line Graph', 'value': 'line'},
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Histogram', 'value': 'histogram'},
            {'label':'Heatmap', 'value':'heatmap'}
        ],
        value='line',
        style={'width': '300px'}
    ),
    html.Br(),
    html.Div(id='line-options', children=[
        html.Div([
        html.Label("Select Scatter Plot Mode:"),
        dcc.Dropdown(
            id='scatter-mode',
            options=[
                {'label': 'Markers', 'value': 'markers'},
                {'label': 'Lines+Markers', 'value': 'lines+markers'}
            ],
            value='lines',
            style={'width': '300px'}
        )
    ], id='scatter-mode-group', style={'display': 'none'}),
        html.Div([
                html.Label("Select Marker Size:"),
                dcc.Slider(
                    id='marker-size',
                    min=1, max=20, step=1, value=10,
                    marks={i: str(i) for i in range(1, 21)},
                    tooltip={'always_visible': True, 'placement': 'bottom'}
                )
            ], id='marker-size-group', style={'display': 'none'}),
        html.Div([
            html.Label("Select Marker Opacity:"),
            dcc.Slider(
                id='marker-opacity',
                min=0.1, max=1.0, step=0.1, value=0.8,
                marks={i/10: str(i/10) for i in range(1, 11)},
                tooltip={'always_visible': True, 'placement': 'bottom'}
            )
        ], id='marker-opacity-group', style={'display': 'none'}),

        html.Div([
            html.Label("Select Line Thickness for Primary Y-Axis:"),
            dcc.Slider(
                id='primary-line-thickness',
                min=1, max=10, step=1, value=2,
                marks={i: str(i) for i in range(1, 11)},
                tooltip={'always_visible': True, 'placement': 'bottom'}
            )], id='primary-line-thickness-group'),
        html.Div([
        html.Label("Select Line Thickness for Secondary Y-Axis:"),
        dcc.Slider(
            id='secondary-line-thickness',
            min=1, max=10, step=1, value=2,
            marks={i: str(i) for i in range(1, 11)},
            tooltip={'always_visible': True, 'placement': 'bottom'}
        ),
    ], id = 'secondary-line-thickness-group'),
    html.Label("Select X-axis:"),
    dcc.Dropdown(id='x-axis', style={'width': '300px'}),
    html.Br(),
    html.Label("Select Y-axis for Primary Axis (can select multiple):"),
    dcc.Dropdown(id='primary-y-axis', multi=True, style={'width': '300px'}),
    html.Br(),
    html.Label("Select Y-axis for Secondary Axis (can select multiple):"),
    dcc.Dropdown(id='secondary-y-axis', multi=True, style={'width': '300px'}),
    dcc.Graph(id='graph-output', style={'height': '800px'}),
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
])

@callback(
    Output('scatter-mode-group', 'style'),
    Output('marker-size-group', 'style'),
    Output('marker-opacity-group', 'style'),
    Input('graph-type', 'value')
)
def toggle_scatter_options(graph_type):
    hidden = {'display': 'none'}
    visible = {'display': 'block'}
    
    if graph_type == 'scatter':
        return visible, visible, visible
    else:
        return hidden, hidden, hidden

@callback(
    Output('primary-line-thickness-group', 'style'),
    Output('secondary-line-thickness-group', 'style'),
    Input('graph-type', 'value')
)
def toggle_line_options(graph_type):
    return [{'display': 'block'}, {'display':'block'}] if graph_type in ['line'] else [{'display': 'none'},{'display': 'none'}]
    
@callback(
    [
        Output('upload-feedback', 'children'),
        Output('x-axis', 'options'),
        Output('x-axis', 'value'),
        Output('primary-y-axis', 'options'),
        Output('primary-y-axis', 'value'),
        Output('secondary-y-axis', 'options'),
        Output('secondary-y-axis', 'value'),
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_upload(contents, filenames):
    """
    Handles the file upload and prepares the dropdown options dynamically.
    """
    if contents is not None:
        # Process uploaded files
        dfs = []
        for content, filename in zip(contents, filenames):
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            try:
                # Try to read the CSV into a DataFrame
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                dfs.append(df)
                # print(f"File '{filename}' successfully read with columns: {df.columns.tolist()}")  # Debugging print
            except Exception as e:
                return f"Error reading file {filename}: {e}", [], None, [], None, [], None

        # Ensure exactly two files are uploaded
        if len(dfs) != 2:
            return "Please upload exactly two CSV files.", [], None, [], None, [], None

        # Extract the two datasets
        df, df1 = dfs

        # Check if there are numeric columns in df1, rename them
        df1.columns = [str(col) if isinstance(col, (int, float)) else col for col in df1.columns]

        # Clean and normalize data
        df_cleaned = clean_data(df)
        df1_cleaned = clean_data(df1)

        # Debugging to show cleaned columns
        # print(f"Cleaned df columns: {df_cleaned.columns.tolist()}")
        # print(f"Cleaned df1 columns: {df1_cleaned.columns.tolist()}")

        # Call interpolate with the additional arguments
        emu_df_int = interpolate(df_cleaned, df1_cleaned)

        # emu_df_int.to_csv(r'c:\Users\GAdmin\Desktop\internship\Sindya\app\skibidi.csv')
        
        
        # Combine all column names from both dataframes for dropdowns
        # all_cols = list(df.columns) + list(df1.columns)
        emu_cols = list(emu_df_int.columns) 
        adp_cols = list(df_cleaned.columns)
        all_cols = adp_cols + emu_cols

        # print(all_cols)
        # print(emu_df)
        # Prepare Y-axis options from both dataframes (add both df and df1 columns)
        primary_y_options = all_cols
        secondary_y_options = all_cols

        return (
            "Files uploaded successfully!",
            all_cols, 
            df_cleaned.columns[0],  # Default X-axis value (time column from first dataframe)
            primary_y_options,  # Default primary Y-axis value
            [list(all_cols)[1]],  # Default primary Y-axis value
            secondary_y_options,  # Default secondary Y-axis value
            []  # Default secondary Y-axis value
        )

    return "Please upload valid CSV files.", [], None, [], None, [], None

@callback(
    Output('graph-output', 'figure'),
    [
        Input('graph-type', 'value'),
        Input('scatter-mode', 'value'),
        Input('primary-line-thickness', 'value'),
        Input('secondary-line-thickness', 'value'),
        Input('marker-size', 'value'),  # Add marker size
        Input('marker-opacity', 'value'),  # Add marker opacity
        Input('x-axis', 'value'),
        Input('primary-y-axis', 'value'),
        Input('secondary-y-axis', 'value')
    ],
    State('upload-data', 'contents')  # State for uploaded files
)

def update_graph(graph_type, scatter_style, primary_thickness, secondary_thickness, marker_size, marker_opacity, x_col, primary_y_cols, secondary_y_cols, contents):
    if contents is None or not x_col or not primary_y_cols:
        return go.Figure()

    # Decode and process the uploaded data
    dfs = []
    for content in contents:
        content_type, content_string = content.split(',')  # content_type doesn't matter, it's like .csv
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        dfs.append(df)

    if len(dfs) != 2:
        raise ValueError("Please upload exactly two CSV files.")
    
    df = dfs[0]  # First dataframe
    df1 = dfs[1]  # Second dataframe

    df_cleaned = clean_data(df)  # cleaned first dataframe
    df_cleaned_1 = clean_data(df1)  # cleaned second dataframe

    try:
        # Process and interpolate the data
        emu_df_int = interpolate(df_cleaned, df_cleaned_1)
    except Exception as e:
        print(f"Error while interpolating data: {e}")
        return go.Figure()

    # Create the figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])  # Enable secondary y-axis

    # Validate x_col exists in emu_df
    if x_col not in emu_df_int:
        raise KeyError(f"Time data for {x_col} not found in processed data.")
    
    if x_col not in df_cleaned:
        raise KeyError(f"Time data for {x_col} not found in processed data.")

    # Convert the time to seconds since the epoch for both dataframes
    time_ADP_sec, time_emu_sec = convert_time(df_cleaned, df_cleaned_1)
    x_data = time_ADP_sec  # Use the processed time as your X-axis
    time_ADP = df_cleaned[x_col]

    # Ensure all Y-axis columns are numeric and plot
    for col in primary_y_cols + secondary_y_cols:
        if col in emu_df_int.columns:
            try:
                emu_df_int[col] = pd.to_numeric(emu_df_int[col], errors='coerce')
            except Exception as e:
                print(f"Error converting column {col} to numeric: {e}")
                continue
        if col in df_cleaned.columns:
            try:
                df_cleaned[col] = pd.to_numeric(emu_df_int[col], errors='coerce')
            except Exception as e:
                print(f"Error converting column {col} to numeric: {e}")
                continue

    # Plot primary Y-axis data
    for col in primary_y_cols:
        if col in emu_df_int:
            if graph_type == 'line':
                fig.add_trace(go.Scatter(
                    x=time_ADP,  # Use original time values for labels
                    y=emu_df_int[col],
                    name=f"{col}", mode='lines', line=dict(width=primary_thickness),
                ), secondary_y=False)
            elif graph_type == 'scatter':
                fig.add_trace(go.Scatter(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}", mode=scatter_style,
                    marker=dict(size=marker_size, opacity=marker_opacity)
                ), secondary_y=False)
            elif graph_type == 'bar':
                fig.add_trace(go.Bar(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}"
                ), secondary_y=False)
            elif graph_type == 'histogram':
                fig.add_trace(go.Histogram(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}"
                ), secondary_y=False)
            elif graph_type == 'heatmap':
                fig.add_trace(go.Heatmap(
                    z=emu_df_int[col].values.reshape(-1, 1),
                    x=time_ADP,
                    y=[col],
                    name=f"{col}"
                ), secondary_y=False)

    # Plot secondary Y-axis data
    for col in secondary_y_cols:
        if col in emu_df_int:
            if graph_type == 'line':
                fig.add_trace(go.Scatter(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}",
                    line=dict(dash='dash', width=secondary_thickness)
                ), secondary_y=True)
            elif graph_type == 'scatter':
                fig.add_trace(go.Scatter(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}", mode=scatter_style,
                    marker=dict(size=marker_size, opacity=marker_opacity)
                ), secondary_y=True)
            elif graph_type == 'bar':
                fig.add_trace(go.Bar(
                    x=time_ADP,
                    y=emu_df_int[col],
                    name=f"{col}", marker=dict(opacity=0.5)
                ), secondary_y=True)
            elif graph_type == 'histogram':
                fig.add_trace(go.Histogram(
                    x=emu_df_int[col],
                    name=f"{col}", marker=dict(opacity=0.5)
                ), secondary_y=True)
            elif graph_type == 'heatmap':
                fig.add_trace(go.Heatmap(
                    z=emu_df_int[col].values.reshape(-1, 1),
                    x=time_ADP,
                    y=[col],
                    name=f"{col}"
                ), secondary_y=True)


    # Update layout for titles and axis labels
    graph_title = f"Graph: X-axis : {x_col}, Y-axis : {', '.join(primary_y_cols)}"
    if secondary_y_cols:
        graph_title += f", Secondary Y-axis : {', '.join(secondary_y_cols)}"

    # Update layout for titles and axis labels based on selected columns
    fig.update_layout(
        title=graph_title,  # Dynamically set the graph title
        xaxis_title=f"{x_col}",
        yaxis_title=f"{', '.join(primary_y_cols)}",  # Titles for primary Y-axis
        yaxis2_title=f"{', '.join(secondary_y_cols)}"  # Titles for secondary Y-axis
    )

    return fig