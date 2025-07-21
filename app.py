"""Audio Dashboard - A Dash app for visualizing audio annotations."""
import dash
from dash import dcc, html, Input, Output, State
import dash_mantine_components as dmc
from plotly.subplots import make_subplots

import bnl

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
        row_heights=[0.1, 0.45, 0.45],
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
        title=f"{track.jam.file_metadata.title}: {track.jam.file_metadata.artist}",
    )
    
    # Set explicit ranges for all x-axes with autorange constraints
    fig.update_xaxes(
        autorangeoptions=dict(
            minallowed=ref.start.time,
            maxallowed=ref.end.time
        )
    )

    return fig

def create_track_selector(track_ids):
    """Create a track selector dropdown."""
    return dmc.Select(
                id="track-selector",
                label="Select Salami Track",
                placeholder="Select a track",
                value=str(track_ids[0]) if track_ids else None,
                data=[{"label": str(tid), "value": str(tid)} for tid in track_ids],
                searchable=True,
                clearable=False,
            )

def create_app_layout(track_ids):
    """Create the main app layout with the given track IDs for selection."""
    return dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Burger(id="navbar-burger", size="sm", hiddenFrom="sm", opened=False),
                        dmc.Title("𝄆🎶𝄇", order=2),
                    ],
                    h="100%",
                    px="md",
                )
            ),
            dmc.AppShellNavbar(
                p="md",
                children=create_track_selector(track_ids),
            ),
            dmc.AppShellMain(
                dmc.Container(
                    dcc.Graph(
                    id="annotation-graph",
                    config={
                        'responsive': True,
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
                    },
                    style={'height': '80vh', 'min-height': '450px', 'width': '100%'},
                    ),
                    size="md",
                    p="sm",
                )
            ),
        ],
        id="app-shell",
        padding="md",
        header={"height": 50},
        navbar={"width": 300, "breakpoint": "sm", "collapsed": {"mobile": True}},
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

### Initialize the app
GLOBAL_SLM_DS =  bnl.data.Dataset()
app = create_app()
server = app.server  # Expose the server variable for Gunicorn

### Interactivity
@app.callback(
    Output("app-shell", "navbar"),
    Input("navbar-burger", "opened"),
    State("app-shell", "navbar"),
)
def toggle_navbar(burger_is_open, current_navbar_config):
    """Callback to control the navbar's collapsed state on mobile."""
    current_navbar_config["collapsed"] = {"mobile": not burger_is_open}
    return current_navbar_config

@app.callback(
    Output("annotation-graph", "figure"),
    Input("track-selector", "value"),
)
def update_graph(selected_track_id):
    """Callback to update the annotation graph based on selected track ID."""
    if selected_track_id is None:
        # On initial load, use the first available track ID
        if not GLOBAL_SLM_DS.track_ids:
            return {}
        selected_track_id = GLOBAL_SLM_DS.track_ids[0]

    track = GLOBAL_SLM_DS[str(selected_track_id)]
    return create_annotation_plot(track)

### For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)
