import dash
from dash.dependencies import Output, Input, State
from dash import html, dcc
import plotly.graph_objs as go
import numpy as np
from datetime import datetime
from collections import deque
import time

# Initialize the Dash app
app = dash.Dash (__name__)

# Configure larger queues for smoother visualization
QUEUE_LENGTH = 50
X = deque (maxlen=QUEUE_LENGTH)
Y = deque (maxlen=QUEUE_LENGTH)
baseline = deque (maxlen=QUEUE_LENGTH)

# Initialize with starting values
X.append (time.time ())
Y.append (100)
baseline.append (100)

app.layout = html.Div ([
    html.Div ([
        html.H1 ("Real-Time Data Streaming Dashboard",
                 style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': 20}),

        html.Div ([
            dcc.Graph (id='live-graph', animate=True),
        ], style={'width': '100%', 'display': 'inline-block'}),

        html.Div ([
            html.Div ([
                html.H4 ("Stream Controls", style={'color': '#2C3E50'}),
                dcc.Dropdown (
                    id='update-speed',
                    options=[
                        {'label': 'Fast (100ms)', 'value': 100},
                        {'label': 'Medium (500ms)', 'value': 500},
                        {'label': 'Slow (1000ms)', 'value': 1000}
                    ],
                    value=100,
                    style={'width': '200px'}
                ),
            ], style={'width': '30%', 'display': 'inline-block'}),

            html.Div ([
                html.H4 ("Statistics", style={'color': '#2C3E50'}),
                html.Div (id='statistics')
            ], style={'width': '70%', 'display': 'inline-block'})
        ], style={'marginTop': '20px'}),

        dcc.Interval (
            id='graph-update',
            interval=100,
            n_intervals=0
        ),
    ], style={'padding': '20px'})
])


@app.callback (
    [Output ('live-graph', 'figure'),
     Output ('statistics', 'children')],
    [Input ('graph-update', 'n_intervals')]
)
def update_graph(n):
    # Add new data points
    X.append (time.time ())

    # Generate more dynamic data
    last_y = Y [-1] if Y else 100
    new_y = last_y + np.sin (time.time ()) * 2 + np.random.normal (0, 0.5)
    Y.append (new_y)

    # Generate baseline
    new_baseline = 100 + np.sin (time.time () * 0.5) * 10
    baseline.append (new_baseline)

    # Create the graph
    data = [
        # Main data trace
        go.Scatter (
            x=list (X),
            y=list (Y),
            name='Real-time Data',
            mode='lines',
            line=dict (
                color='#2E86C1',
                width=2,
            ),
            fill='tonexty',
            fillcolor='rgba(46, 134, 193, 0.1)'
        ),
        # Baseline trace
        go.Scatter (
            x=list (X),
            y=list (baseline),
            name='Baseline',
            mode='lines',
            line=dict (
                color='#E74C3C',
                width=2,
                dash='dash'
            )
        )
    ]

    # Layout
    layout = go.Layout (
        title=dict (
            text='Real-Time Data Stream',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict (
            title='Time',
            range=[min (X), max (X)],
            gridcolor='#E1E1E1',
            showgrid=True,
            showline=True,
            showticklabels=True,
        ),
        yaxis=dict (
            title='Value',
            range=[min (min (Y), min (baseline)) - 5, max (max (Y), max (baseline)) + 5],
            gridcolor='#E1E1E1',
            showgrid=True,
            showline=True,
            showticklabels=True,
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True,
        legend=dict (
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict (l=50, r=50, t=50, b=50)
    )

    # Create statistics
    stats = html.Div ([
        html.P (f"Current Value: {Y [-1]:.2f}"),
        html.P (f"Baseline: {baseline [-1]:.2f}"),
        html.P (f"Deviation: {(Y [-1] - baseline [-1]):.2f}",
                style={'color': '#E74C3C' if Y [-1] < baseline [-1] else '#27AE60'})
    ])

    return {'data': data, 'layout': layout}, stats


@app.callback (
    Output ('graph-update', 'interval'),
    [Input ('update-speed', 'value')]
)
def update_interval(value):
    return value


if __name__ == '__main__':
    app.run_server (debug=True)
