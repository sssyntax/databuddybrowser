import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
import plotly.graph_objects as go
import io
import base64
import numpy as np
from datetime import datetime, timedelta
import copy

# Register the page (if using multi-page app)
dash.register_page(__name__, path="/visualisation_difference", title="Visualisation: Difference Plot", name="Visualisation: Difference Plot")

# Helper functions for data cleaning and processing
def clean_data(df):
    return df.dropna()

# Time adjustment and interpolation logic
def adjust_time(row, base_day, base_hour):
    minutes_seconds = datetime.strptime(row, '%M:%S.%f').time()
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
        emu_df_int[col] = np.interp(time_ADP_sec, time_emu_sec, np.array(df1[col], dtype=np.float64))
        
    return emu_df_int

# Layout
layout = html.Div([
    html.H2("Difference Graph", style={'textAlign': 'center'}),
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
    html.Div(id='upload-feedback-diff', style={'textAlign': 'center', 'color': 'green'}),
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
    html.Label("Select Scatter Plot Mode:"),
    dcc.Dropdown(
        id='scatter-mode-1',
        options=[
            {'label': 'Markers', 'value': 'markers'},
            {'label': 'Lines+Markers', 'value': 'lines+markers'}
        ],
        value='lines',
        style={'width': '300px'}),
    html.Br(),
        html.Label("Select Marker Size:"),
           dcc.Slider(
            id='marker-size-1',
            min=1, max=20, step=1, value=10,
            marks={i: str(i) for i in range(1, 21)},
            tooltip={'always_visible': True, 'placement': 'bottom'}
        ),
        html.Br(),
        html.Label("Select Marker Opacity:"),
        dcc.Slider(
            id='marker-opacity-1',
            min=0.1, max=1.0, step=0.1, value=0.8,
            marks={i/10: str(i/10) for i in range(1, 11)},
            tooltip={'always_visible': True, 'placement': 'bottom'}
        ),
    html.Br(),
    html.Label("Select Line Thickness:"),
    dcc.Slider(
        id='line-thickness',
        min=1, max=10, step=1, value=2,
        marks={i: str(i) for i in range(1, 11)},
        tooltip={'always_visible': True, 'placement': 'bottom'}
    ),
    html.Label("Select X-axis:"),
    dcc.Dropdown(id='x-axis-diff', style={'width': '300px'}),
    html.Label("Select Y-axis:"),
    dcc.Dropdown(id='primary-y-axis-diff', multi=False, style={'width': '300px'}),
    html.Br(),
    html.Label("Select Y-axis to minus:"),
    dcc.Dropdown(id='secondary-y-axis-diff', multi=False, style={'width': '300px'}),
    html.Br(),
    dash_table.DataTable(
    id='stats-table-diff',
    style_table={'overflowX': 'auto'},
    style_cell={'textAlign': 'left', 'padding': '5px'},
    style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold', 'textAlign':'center'}
    ),
    html.Br(),
    dcc.Graph(id='graph-output-diff', style={'height': '800px'}),
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

@callback(
    Output('scatter-mode-1', 'style'),  # Scatter mode option
    Output('marker-size-1', 'style'),  # Marker size option
    Output('marker-opacity-1', 'style'),  # Marker opacity option
    Input('graph-type', 'value')  # Graph type selection
)
def toggle_line_options(graph_type):
    # Default styles: hide all options
    hidden = {'display': 'none'}
    visible = {'display': 'block'}
    
    if graph_type == 'line':
        return [visible, hidden, hidden]  # Only line thickness visible
    elif graph_type == 'scatter':
        return [visible, visible, visible]  # All scatter options visible
    elif graph_type in ['bar', 'histogram', 'heatmap']:  # Other graph types
        return [hidden, hidden, hidden]  # Hide all options
    return [hidden, hidden, hidden]  # Default: Hide all options

@callback(
    [
        Output('upload-feedback-diff', 'children'),
        Output('x-axis-diff', 'options'),
        Output('x-axis-diff', 'value'),
        Output('primary-y-axis-diff', 'options'),
        Output('primary-y-axis-diff', 'value'),
        Output('secondary-y-axis-diff', 'options'),
        Output('secondary-y-axis-diff', 'value')
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
    [
        Output('graph-output-diff', 'figure'),
        Output('stats-table-diff', 'data'),
        Output('stats-table-diff', 'columns')
    ],
    [
        Input('graph-type', 'value'),
        Input('x-axis-diff', 'value'),
        Input('primary-y-axis-diff', 'value'),
        Input('secondary-y-axis-diff', 'value'),
        Input('scatter-mode-1', 'value'),
        Input('marker-size-1', 'value'),
        Input('marker-opacity-1', 'value'),
        Input('line-thickness', 'value')
    ],
    State('upload-data', 'contents')
)
def update_graph_and_table(graph_type, x_col, primary_y_cols, secondary_y_cols, scatter_mode, marker_size, marker_opacity, line_thickness, contents):
    if contents is None or not x_col or not primary_y_cols or not secondary_y_cols:
        return go.Figure(), [], []

    # Ensure primary_y_cols and secondary_y_cols are lists
    primary_y_cols = [primary_y_cols] if isinstance(primary_y_cols, str) else primary_y_cols
    secondary_y_cols = [secondary_y_cols] if isinstance(secondary_y_cols, str) else secondary_y_cols

    # Decode and process uploaded files
    dfs = []
    for content in contents:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        dfs.append(df)

    if len(dfs) != 2:
        raise ValueError("Please upload exactly two CSV files.")

    # Clean and interpolate data
    df_cleaned = clean_data(dfs[0])
    df1_cleaned = clean_data(dfs[1])
    interpolated_df = interpolate(df_cleaned, df1_cleaned)

    # Validate selected columns exist
    primary_y_cols = [col for col in primary_y_cols if col in interpolated_df.columns]
    secondary_y_cols = [col for col in secondary_y_cols if col in interpolated_df.columns]

    if not primary_y_cols or not secondary_y_cols:
        return go.Figure(), [], []

    # Compute differences
    diff_data = interpolated_df[primary_y_cols].subtract(interpolated_df[secondary_y_cols].values, axis=0)

    # Calculate statistics
    stats = {
        "Mean": diff_data.mean(),
        "Standard Deviation": diff_data.std(),
        "Maximum": diff_data.max(),
        "Minimum": diff_data.min()
    }

    # Prepare table data
    table_data = []
    for col in diff_data.columns:
        row = {
            "Column": col,
            "Mean": stats["Mean"][col],
            "Std Dev": stats["Standard Deviation"][col],
            "Max": stats["Maximum"][col],
            "Min": stats["Minimum"][col]
        }
        table_data.append(row)

    table_columns = [
        {"name": "Column", "id": "Column"},
        {"name": "Mean", "id": "Mean"},
        {"name": "Std Dev", "id": "Std Dev"},
        {"name": "Maximum", "id": "Max"},
        {"name": "Minimum", "id": "Min"}
    ]

    # Create figure
    fig = go.Figure()

    if graph_type == 'line':
        for col in diff_data.columns:
            fig.add_trace(go.Scatter(x=interpolated_df[x_col], y=diff_data[col], mode='lines', line=dict(width=line_thickness), name=f'Difference: {col}'))
    elif graph_type == 'scatter':
        for col in diff_data.columns:
            fig.add_trace(go.Scatter(x=interpolated_df[x_col], y=diff_data[col], mode=scatter_mode, marker=dict(size=marker_size, opacity=marker_opacity), name=f'Difference: {col}'))
    elif graph_type == 'bar':
        for col in diff_data.columns:
            fig.add_trace(go.Bar(x=interpolated_df[x_col], y=diff_data[col], name=f'Difference: {col}'))
    elif graph_type == 'histogram':
        for col in diff_data.columns:
            fig.add_trace(go.Histogram(x=diff_data[col], name=f'Difference: {col}'))
    elif graph_type == 'heatmap':
        fig.add_trace(go.Heatmap(
            z=diff_data.values,
            x=interpolated_df[x_col],
            y=diff_data.columns,
            colorscale="Viridis",
            name="Differences"
        ))

    # Update layout
    fig.update_layout(
        title=f"Difference Plot: {', '.join(primary_y_cols)} vs {', '.join(secondary_y_cols)}",
        xaxis_title=x_col,
        yaxis_title="Difference"
    )

    return fig, table_data, table_columns
