from dash import Dash, html
import plotly.express as px

# Initialize the app
app = Dash(__name__)
server = app.server # Expose the server variable for Gunicorn

# Define the app layout
app.layout = html.Div([
    html.H1(children='Dash MVP on Hugging Face Spaces! 🚀'),
    html.P(children='This is the foundation for the interactive audio widget.')
])