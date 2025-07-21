"""Audio Dashboard - A Dash app for visualizing audio annotations."""
import dash
from dash import dcc, html, Input, Output, State, clientside_callback, ClientsideFunction
import dash_mantine_components as dmc
from dash_player import DashPlayer
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

def create_track_selector(slm_ds):
    """Create a track selector dropdown."""
    track_ids = getattr(slm_ds, "track_ids", [])
    return dmc.Select(
                id="track-selector",
                label="Select Salami Track",
                placeholder="Select a track",
                value=None,
                data=[{"label": str(tid), "value": str(tid)} for tid in track_ids],
                searchable=True,
                clearable=False,
            )

def create_app_layout(dataset):
    """Create the main app layout with the given dataset."""
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
                children=[
                    create_track_selector(dataset),
                    DashPlayer(
                        id='audio-player',
                        controls=True,
                        width='100%',
                        height='50px',
                        intervalCurrentTime=100,
                        style={'marginBottom': '20px'}
                    ),
                ],
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
                    style={'height': '80vh', 'min-height': '450px', 'max-height': '950px', 'width': '100%'},
                    ),
                    size="md",
                    p="xs",
                )
            ),
            dcc.Store(id="init-complete"),
            html.Div(id='clientside-dummy-output'),
        ],
        id="app-shell",
        padding="md",
        header={"height": 50},
        navbar={"width": 300, "breakpoint": "sm", "collapsed": {"mobile": True}},
    )

def register_callbacks(app, dataset):
    """Register all app callbacks in one place."""
    
    @app.callback(
        Output("app-shell", "navbar"),
        Input("navbar-burger", "opened"),
        State("app-shell", "navbar"),
    )
    def toggle_navbar(burger_is_open, current_navbar_config):
        """Toggle navbar on mobile."""
        current_navbar_config["collapsed"] = {"mobile": not burger_is_open}
        return current_navbar_config

    @app.callback(
        Output("annotation-graph", "figure"),
        Output("audio-player", "url"),
        Output("audio-player", "playing"),
        Input("track-selector", "value"),
    )
    def update_graph_and_audio(selected_track_id):
        """Update graph and audio based on selected track."""
        if not selected_track_id or not dataset.track_ids:
            return dash.no_update, dash.no_update, dash.no_update
        track = dataset[selected_track_id]
        return create_annotation_plot(track), track.info['audio_mp3_path'], True

    @app.callback(
        Output("track-selector", "value"),
        Input("init-complete", "data"),
    )
    def load_init_track(_):
        """Load initial track on app startup."""
        return dataset.track_ids[8] if dataset.track_ids else dash.no_update

    # Clientside callback for playhead updates
    clientside_callback(
        ClientsideFunction(
            namespace='audioPlayback',
            function_name='updatePlayhead'
        ),
        Output('clientside-dummy-output', 'children'),
        Input('audio-player', 'currentTime'),
        State('annotation-graph', 'id'),
        State('annotation-graph', 'figure'),
    )

def create_app():
    """Create and configure the Dash application."""
    # Initialize dataset
    dataset = bnl.data.Dataset()
    
    # Create app
    app = dash.Dash(__name__)
    dmc.add_figure_templates(default="mantine_light")
    
    # Set layout
    app.layout = dmc.MantineProvider(
        create_app_layout(dataset),
        theme={"colorScheme": "light"}
    )
    
    # Register all callbacks
    register_callbacks(app, dataset)
    
    return app, dataset

# Initialize the app
app, dataset = create_app()
server = app.server  # For Gunicorn

### For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)
