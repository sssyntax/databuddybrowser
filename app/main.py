import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Create Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], use_pages=True, pages_folder='/workspaces/databuddybrowser/pages', suppress_callback_exceptions=True)

# Define the main layout (only for the home page)
app.layout = html.Div([
    html.H1("DataBuddy", style={'textAlign': 'center'}),
    dash.page_container  # This will render the content of the current page
])

if __name__ == '__main__':
    app.run(debug=True)

server = app.server
handler = serverless_wsgi.create_handler(server)