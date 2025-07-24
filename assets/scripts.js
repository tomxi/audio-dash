// Event-driven Audio Controller with Observer Pattern
window.dash_clientside = window.dash_clientside || {};

class AudioController {
    constructor() {
        this.audioElement = null;
        this.graphElement = null;
        this.animationFrame = null;
        this.isInitialized = false;
        this.eventBus = new EventTarget();
    }

    init(audioSelector, graphSelector) {
        if (this.isInitialized) return;

        this.audioElement = document.querySelector(audioSelector);
        this.graphElement = document.querySelector(graphSelector)?.querySelector('.js-plotly-plot');

        if (!this.audioElement || !this.graphElement) {
            console.warn('AudioController: Required elements not found, retrying...');
            setTimeout(() => this.init(audioSelector, graphSelector), 100);
            return;
        }

        this.setupEventListeners();
        this.isInitialized = true;
        this.eventBus.dispatchEvent(new CustomEvent('initialized'));
    }

    setupEventListeners() {
        // User interaction state
        this.isUserInteracting = false;
        this.clickDebounceTimer = null;
        
        // Audio events
        this.audioElement.addEventListener('play', () => this.startPlayheadSync());
        this.audioElement.addEventListener('pause', () => this.stopPlayheadSync());
        this.audioElement.addEventListener('ended', () => this.resetPlayhead());
        this.audioElement.addEventListener('seeked', () => this.updatePlayhead());

        // Graph events with race condition prevention
        this.graphElement.on('plotly_click', (data) => this.handleGraphClick(data));
        this.graphElement.on('plotly_hover', (data) => this.handleGraphHover(data));
        
        // Mouse interaction tracking to prevent playhead updates during clicks
        this.graphElement.addEventListener('mousedown', () => {
            this.isUserInteracting = true;
            this.stopPlayheadSync(); // Pause updates during interaction
            clearTimeout(this.clickDebounceTimer);
        });
        
        this.graphElement.addEventListener('mouseup', () => {
            this.clickDebounceTimer = setTimeout(() => {
                this.isUserInteracting = false;
                if (!this.audioElement.paused) {
                    this.startPlayheadSync(); // Resume updates
                }
            }, 100); // Small delay to ensure click completes
        });
        
        this.graphElement.addEventListener('mouseleave', () => {
            this.isUserInteracting = false;
            if (!this.audioElement.paused) {
                this.startPlayheadSync();
            }
        });
    }

    startPlayheadSync() {
        const update = () => {
            if (!this.audioElement.paused && !this.audioElement.ended) {
                this.updatePlayhead();
                this.animationFrame = requestAnimationFrame(update);
            }
        };
        update();
    }

    stopPlayheadSync() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
    }

    updatePlayhead(time = null) {
        if (!this.graphElement || this.isUserInteracting) return;
        
        const currentTime = time ?? this.audioElement.currentTime;
        Plotly.relayout(this.graphElement, {
            'shapes[0].x0': currentTime,
            'shapes[0].x1': currentTime,
        }).catch(err => {
            // Suppress benign relayout errors during user interaction
            if (!err.message.includes('undefined')) {
                console.warn('Playhead update failed:', err);
            }
        });
    }

    resetPlayhead() {
        this.updatePlayhead(0);
    }

    handleGraphClick(data) {
        if (!data?.points?.[0]) return;
        
        // Ensure we're not in a race condition state
        clearTimeout(this.clickDebounceTimer);
        this.isUserInteracting = false;
        
        const point = data.points[0];
        const targetTime = point.hasOwnProperty('base') ? point.base : point.x;
        
        if (this.audioElement) {
            this.audioElement.currentTime = targetTime;
            this.eventBus.dispatchEvent(new CustomEvent('seek', { detail: { time: targetTime } }));
            
            // Resume playhead sync after seek
            setTimeout(() => {
                if (!this.audioElement.paused) {
                    this.startPlayheadSync();
                }
            }, 50);
        }
    }

    handleGraphHover(data) {
        // Future: Show tooltip with time info
        this.eventBus.dispatchEvent(new CustomEvent('hover', { detail: data }));
    }

    // Public API
    seekTo(time) {
        if (this.audioElement) {
            this.audioElement.currentTime = time;
        }
    }

    getCurrentTime() {
        return this.audioElement?.currentTime ?? 0;
    }

    destroy() {
        this.stopPlayheadSync();
        this.isInitialized = false;
        this.audioElement = null;
        this.graphElement = null;
    }
}

// Initialize global controller
window.AudioController = new AudioController();

// Dash clientside callback integration
window.dash_clientside.audioPlayback = {
    init: function(trigger_time) {
        window.AudioController.init('#audio-player', '#annotation-graph');
        return trigger_time;
    }
};
