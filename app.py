"""Audio Dashboard - A Dash app for visualizing audio annotations."""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

import bnl


def load_ds():
    """Load sample audio data with annotations."""
    R2_BUCKET_PUBLIC_URL = "https://pub-05e404c031184ec4bbf69b0c2321b98e.r2.dev"
    return bnl.data.Dataset(manifest_path=f"{R2_BUCKET_PUBLIC_URL}/manifest_cloud_boolean.csv")

def create_annotation_plot(track):
    """Create a multi-row subplot comparing estimated and reference annotations."""
    est = track.load_annotation("adobe-mu1gamma1")
    ref = track.load_annotation("reference")

    fig_est = est.plot(colorscale="D3")
    fig_ref = ref.plot(colorscale="D3")

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.15, 0.4, 0.45],
    )

    # Add traces to subplots
    for trace in fig_ref.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in fig_est.data:
        fig.add_trace(trace, row=2, col=1)
    for trace in est.to_contour('prob').plot().data:
        fig.add_trace(trace, row=3, col=1)

    # Configure layout
    fig.update_layout(
        xaxis3_range=[ref.start.time, ref.end.time],
        barmode="overlay",
        yaxis1=dict(
            categoryorder="array",
            categoryarray=[layer.name for layer in reversed(est)],
        ),
        yaxis2=dict(
            categoryorder="array",
            categoryarray=[layer.name for layer in reversed(ref)],
        ),
        legend_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


def create_app_layout(figure):
    """Create the main app layout with the given figure."""
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(children='Dash MVP on Hugging Face Spaces! 🚀'),
                        html.P(children='This is the foundation for the interactive audio widget.'),
                        dcc.Graph(
                            figure=figure, 
                            config={'responsive': True}, 
                            style={'height': '800px', 'minWidth': '450px'}
                        ),
                    ],
                    width=12,  # Full width on all screen sizes
                    lg=8,      # 8 columns on large screens and up
                    md=10,     # 10 columns on medium screens and up
                    className="text-center"
                ),
                justify="center",  # Center the column horizontally
            )
        ],
        fluid=True,
        className="p-3"
    )


def create_app():
    """Create and configure the Dash application."""
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Load data and create visualization
    slm_ds = load_ds()
    fig = create_annotation_plot(slm_ds[11])
    
    # Set up layout
    app.layout = create_app_layout(fig)
    
    return app


# Initialize the app
app = create_app()
server = app.server  # Expose the server variable for Gunicorn

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)
