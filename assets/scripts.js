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
        // Use a custom 100ms timer for smoother playhead updates
        let updateInterval;
        
        const updatePlayhead = () => {
            if (!audioEl.paused && !audioEl.ended) {
                const currentTime = audioEl.currentTime;
                // Use requestAnimationFrame for smooth rendering sync
                window.requestAnimationFrame(() => {
                    Plotly.relayout(graphEl, {
                        'shapes[0].x0': currentTime,
                        'shapes[0].x1': currentTime,
                    });
                });
            }
        };
        
        // Start/stop timer based on audio play/pause events
        audioEl.addEventListener('play', () => {
            if (updateInterval) clearInterval(updateInterval);
            updateInterval = setInterval(updatePlayhead, 100); // 100ms updates
        });
        
        audioEl.addEventListener('pause', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        });
        
        audioEl.addEventListener('ended', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        });
        
        // Also update on seek
        audioEl.addEventListener('seeked', updatePlayhead);
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
