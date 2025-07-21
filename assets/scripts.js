// Register the namespace with Dash's clientside engine
window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.audioPlayback = {
    updatePlayhead: function(currentTime, graphId, figure) {
        if (currentTime > 0 && graphId && figure && figure.layout) {
            const graphDiv = document.getElementById(graphId);
            // console.log('graphDiv:', graphDiv);
            // console.log('figure.layout:', figure.layout);

            // Find the playhead shape by name, or create a new one if it doesn't exist
            let playheadIndex = -1;
            const shapes = (figure.layout.shapes || []).map((s, idx) => {
                if (s.name === 'playhead') {
                    playheadIndex = idx;
                    return {
                        ...s,
                        x0: currentTime,
                        x1: currentTime,
                        y0: figure.layout.yaxis3.range[0],
                        y1: figure.layout.yaxis3.range[1],
                    };
                }
                return s;
            });

            if (playheadIndex === -1) {
                // Playhead doesn't exist, create it
                const newPlayhead = {
                    type: 'line',
                    name: 'playhead',
                    xref: 'x',
                    yref: 'y3',
                    x0: currentTime,
                    x1: currentTime,
                    y0: figure.layout.yaxis3.range[0],
                    y1: figure.layout.yaxis3.range[1],
                    line: {
                        color: 'rgba(255, 0, 0, 0.8)',
                        width: 2,
                        dash: 'solid',
                    }
                };
                shapes.push(newPlayhead);
            }
            
            // Use Plotly.relayout to update only the shapes
            Plotly.relayout(graphId, { shapes: shapes });
        }
        return null;
    }
};