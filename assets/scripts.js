// Lean Audio-Graph Controller
window.dash_clientside = window.dash_clientside || {};

class AudioController {
    constructor() {
        this.audio = null;
        this.graph = null;
        this.frame = null;
        this.userActive = false;
        this.lastUpdate = Date.now();
    }

    init(audioSelector = '#audio-player', graphSelector = '#annotation-graph') {
        this.audio = document.querySelector(audioSelector);
        this.graph = document.querySelector(graphSelector)?.querySelector('.js-plotly-plot');
        
        if (!this.audio || !this.graph) {
            setTimeout(() => this.init(audioSelector, graphSelector), 100);
            return;
        }

        this.setupEvents();
    }

    setupEvents() {
        const startPlayhead = () => {
            if (!this.audio.paused && !this.userActive) {
                let now = Date.now();
                if (now - this.lastUpdate >= 250) { // 4Hz = 250ms
                    const time = this.getTime();
                    Plotly.relayout(this.graph, {
                        'shapes[0].x0': time,
                        'shapes[0].x1': time
                    }).catch(() => {});
                    this.lastUpdate = now;
                }
            }
            this.frame = this.audio.paused ? null : requestAnimationFrame(startPlayhead);
        };

        const stopPlayhead = () => this.frame && (cancelAnimationFrame(this.frame), this.frame = null);

        // Audio events
        this.audio.addEventListener('play', startPlayhead);
        this.audio.addEventListener('pause', stopPlayhead);
        this.audio.addEventListener('ended', stopPlayhead);

        // Interaction management
        const handleInteraction = (active) => {
            this.userActive = active;
            stopPlayhead();
            if (!active && !this.audio.paused) startPlayhead();
        };

        this.graph.addEventListener('mousedown', () => handleInteraction(true));
        this.graph.addEventListener('mouseup', () => handleInteraction(false));
        this.graph.addEventListener('mouseleave', () => handleInteraction(false));
        
        // Plotly double-click recovery
        this.graph.on('plotly_doubleclick', () => {
            handleInteraction(false); // Reset interaction state
            if (!this.audio.paused) {
                setTimeout(() => startPlayhead(), 100); // Delay to allow Plotly to finish
            }
        });

        // Click-to-seek and auto-play
        this.graph.on('plotly_click', (data) => {
            if (!data?.points?.[0]) return;
            
            handleInteraction(false); // Reset interaction state
            this.seekTo(data.points[0].base ?? data.points[0].x);
            
            // Auto-play after seek and start playhead
            if (this.audio.paused) this.audio.play();
            startPlayhead();
        });

        // startPlayhead if already playing
        if (!this.audio.paused) startPlayhead();
    }

    // Public API for external use
    seekTo(time) { this.audio && (this.audio.currentTime = time); }
    getTime() { return this.audio?.currentTime ?? 0; }

}

// Initialize
window.AudioController = new AudioController();
window.dash_clientside.audioPlayback = {
    init: () => window.AudioController.init('#audio-player', '#annotation-graph')
};
