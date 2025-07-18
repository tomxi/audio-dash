import dash
from plotly.subplots import make_subplots
import bnl

# Initialize the app
app = dash.Dash(__name__)
server = app.server # Expose the server variable for Gunicorn

# Load some data
R2_BUCKET_PUBLIC_URL = "https://pub-05e404c031184ec4bbf69b0c2321b98e.r2.dev"
slm_ds = bnl.data.Dataset(manifest_path=f"{R2_BUCKET_PUBLIC_URL}/manifest_cloud_boolean.csv")
track = slm_ds[8]
est = track.load_annotation("adobe-mu1gamma1")
ref = track.load_annotation("reference")

# make a figure
fig_est = est.plot(colorscale="D3")
fig_ref = ref.plot(colorscale="D3")

fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.15, 0.4, 0.45],
)

for trace in fig_ref.data:
    fig.add_trace(trace, row=1, col=1)
for trace in fig_est.data:
    fig.add_trace(trace, row=2, col=1)
for trace in est.to_contour('prob').plot().data:
    fig.add_trace(trace, row=3, col=1)

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
)
fig.update_layout(height=800, width=650, legend_visible=False)

# Define the app layout
app.layout = dash.html.Div([
    dash.html.H1(children='Dash MVP on Hugging Face Spaces! 🚀'),
    dash.html.P(children='This is the foundation for the interactive audio widget.'),
    dash.dcc.Graph(figure=fig),
])
