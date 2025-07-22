// Register the namespace with Dash's clientside engine
window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.audioPlayback = {
    updatePlayhead: function(currentTime, graphId) {
        if (currentTime > 0 && graphId) {
            const graphDiv = document.getElementById(graphId).querySelector('.js-plotly-plot');
            if (!graphDiv || !graphDiv.layout || !graphDiv.layout.shapes) {
                return 'no_shapes';
            }

            const layout = graphDiv.layout;
            const playheadIndex = layout.shapes.findIndex(shape => shape.name === 'playhead');
            if (playheadIndex !== -1) {
                const update = {
                    [`shapes[${playheadIndex}].x0`]: currentTime,
                    [`shapes[${playheadIndex}].x1`]: currentTime
                };
                
                Plotly.relayout(graphDiv, update);
                return 'playhead_updated';
            }
        }
        return 'no_playhead';
    }
};