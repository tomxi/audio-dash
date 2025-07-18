"""Audio Dashboard - A Dash app for visualizing audio annotations."""
import dash
from dash import dcc, html, _dash_renderer
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
from plotly.subplots import make_subplots

import bnl
_dash_renderer._set_react_version("18.2.0")

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
            categoryarray=[layer.name for layer in reversed(ref)],
        ),
        yaxis2=dict(
            categoryorder="array",
            categoryarray=[layer.name for layer in reversed(est)],
        ),
        legend_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
        title=track.info['title']
    )

    return fig


def create_app_layout(track_ids):
    """Create the main app layout with the given track IDs for selection."""
    return dmc.Container(
        [
            dmc.Title("🎶Music Structure Analysis Dashboard 🎶", order=1, ta="center"),
            dmc.Text("Interactive audio annotation visualization", ta="center", c="dimmed", mb="lg"),
            dmc.Select(
                label="Select Track",
                placeholder="Select a track",
                id="track-select-dropdown",
                value=str(track_ids[8]),  # Set initial value, ensure it's a string
                data=[{"label": str(tid), "value": str(tid)} for tid in track_ids],
                searchable=True,
                clearable=False,
                style={"width": 200, "marginBottom": 20},
            ),
            dcc.Graph(
                id="annotation-graph",  # Add an ID for callback targeting
                config={'responsive': True},
                style={'height': '800px', 'minWidth': '450px'}
            ),
        ],
        size="lg",
        p="md"
    )


def create_app():
    """Create and configure the Dash application."""
    app = dash.Dash(__name__)
    dmc.add_figure_templates(default="mantine_light")
    # Set up layout with dmc theme
    app.layout = dmc.MantineProvider(
        create_app_layout(GLOBAL_SLM_DS.track_ids),
        theme={"colorScheme": "light"}
    )
    
    return app


# Initialize the app

GLOBAL_SLM_DS = load_ds()
app = create_app()
server = app.server  # Expose the server variable for Gunicorn

@app.callback(
    Output("annotation-graph", "figure"),
    Input("track-select-dropdown", "value"),
)
def update_graph(selected_track_id):
    """Callback to update the annotation graph based on selected track ID."""
    if selected_track_id is None:
        # Return an empty figure or handle the case where no track is selected
        return {}
    
    track = GLOBAL_SLM_DS[selected_track_id]
    fig = create_annotation_plot(track)
    return fig

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)
