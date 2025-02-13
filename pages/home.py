import dash
from dash import html, dcc

# Register the homepage
dash.register_page(__name__, path="/", title="Homepage", name="Home")

# Define the homepage layout
layout = html.Div([
    # Title Section
    html.Div([
        html.H1("Welcome to DataBuddy Browser!", style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.P("What would you like to do?", style={'textAlign': 'center'}),
    ], style={'padding': '50px 10px', 'backgroundColor': '#f4f4f4'}),
    
    # Navigation Section
    html.Div([
        html.H2("Navigation", style={'textAlign': 'center', 'marginTop': '20px'}),
        html.Div([
            dcc.Link("Visualisation: 2 Separate Graphs", href="/visualisation_2_sep", style={'fontSize': '18px'}),
            html.Br(),
            dcc.Link("Visualisation: Combined Graph", href="/visualisation_combined", style={'fontSize': '18px'}),
            html.Br(),
            dcc.Link("Visualisation: Difference Plot", href="/visualisation_difference", style={'fontSize': '18px'})
        ], style={'textAlign': 'center', 'marginTop': '10px'}),
    ], style={'padding': '20px'}),

    # About Section
    html.Div([
        html.H2("About", style={'textAlign': 'center', 'marginTop': '20px'}),
        html.P(
            "This dashboard is designed to help you visualize and compare datasets. "
            "You can create dynamic graphs, and interact with visualizations easily.",
            style={'textAlign': 'center', 'maxWidth': '800px', 'margin': 'auto'}
        )
    ], style={'padding': '20px'}),

    # Footer Section
    html.Div([
        html.Hr(),
        html.P("© 2025 DataBuddy Browser. All rights reserved.", style={'textAlign': 'center', 'marginTop': '10px'}),
    ], style={'marginTop': '30px', 'backgroundColor': '#f4f4f4', 'padding': '10px'}),
])