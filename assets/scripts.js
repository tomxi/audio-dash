// Register the namespace with Dash's clientside engine
window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.audioPlayback = {
    init: function(trigger_time) {
        const audioEl = document.getElementById('audio-player');
        const graphEl = document.getElementById('annotation-graph').querySelector('.js-plotly-plot');
        // Exit if our elements don't exist yet
        if (!audioEl || !graphEl) {
            console.error("Audio Controller: Audio or Graph element not found.");
            return;
        }

        // Set up the two-way interactivity
        this.setupTimeUpdateListener(audioEl, graphEl);
        this.setupSeekListener(audioEl, graphEl);

        console.log("Audio Controller Initialized", trigger_time);
    },
    setupTimeUpdateListener: function(audioEl, graphEl) {
        audioEl.addEventListener('timeupdate', () => {
            // Schedule the Plotly update to run just before the next repaint.
            window.requestAnimationFrame(() => {
                const currentTime = audioEl.currentTime;
                Plotly.relayout(graphEl, {
                    'shapes[0].x0': currentTime,
                    'shapes[0].x1': currentTime,
                });
            });
        });
    },
    setupSeekListener: function(audioEl, graphEl) {
        graphEl.on('plotly_click', (clickData) => {
            if (clickData && clickData.points) {
                // The 'x' coordinate of the click gives us the target time
                const point = clickData.points[0]
                audioEl.currentTime = point.hasOwnProperty('base') ? point.base : point.x;
            }
        });
    },
};
