"""
Flask REST API for controlling Pimoroni Unicorn HAT 8x8 LED Matrix.
Accepts an 8x8 grid of RGB colors and displays them on the HAT.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from collections import deque
import threading

# Try to import unicornhat - will fail on non-Raspberry Pi systems
try:
    import unicornhat as unicorn
    UNICORN_AVAILABLE = True
except ImportError:
    UNICORN_AVAILABLE = False
    print("WARNING: unicornhat module not available. Running in simulation mode.")

app = Flask(__name__)

# CORS configuration - only allow requests from the production frontend
ALLOWED_ORIGIN = 'https://lights-ui.vercel.app'
CORS(app, 
     origins=[ALLOWED_ORIGIN], 
     allow_headers=['Content-Type', 'ngrok-skip-browser-warning', 'User-Agent'],
     methods=['GET', 'POST', 'OPTIONS'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Grid dimensions
GRID_WIDTH = 8
GRID_HEIGHT = 8

# Store last 10 grids in memory
MAX_HISTORY = 10
grid_history = deque(maxlen=MAX_HISTORY)

# Auto-off timer settings
AUTO_OFF_SECONDS = 10
auto_off_timer = None
timer_lock = threading.Lock()

def schedule_auto_off():
    """Schedule the display to turn off after AUTO_OFF_SECONDS."""
    global auto_off_timer
    
    with timer_lock:
        # Cancel any existing timer
        if auto_off_timer is not None:
            auto_off_timer.cancel()
        
        # Schedule new timer
        auto_off_timer = threading.Timer(AUTO_OFF_SECONDS, auto_off_callback)
        auto_off_timer.daemon = True
        auto_off_timer.start()
        logger.info(f"Auto-off scheduled in {AUTO_OFF_SECONDS} seconds")

def cancel_auto_off():
    """Cancel the auto-off timer."""
    global auto_off_timer
    
    with timer_lock:
        if auto_off_timer is not None:
            auto_off_timer.cancel()
            auto_off_timer = None
            logger.info("Auto-off timer cancelled")

def auto_off_callback():
    """Callback function to turn off the display."""
    global auto_off_timer
    
    with timer_lock:
        auto_off_timer = None
    
    clear()
    logger.info("Display auto-off triggered")

def save_grid_to_history(grid: list):
    """Save a grid to the history with timestamp."""
    entry = {
        'id': datetime.now().isoformat(),
        'grid': grid,
        'timestamp': datetime.now().isoformat()
    }
    grid_history.appendleft(entry)
    logger.info(f"Grid saved to history. Total entries: {len(grid_history)}")

def init_unicorn():
    """Initialize the Unicorn HAT."""
    if UNICORN_AVAILABLE:
        unicorn.set_layout(unicorn.AUTO)
        unicorn.rotation(0)
        unicorn.brightness(0.5)
        logger.info("Unicorn HAT initialized successfully")

def set_pixel(x: int, y: int, r: int, g: int, b: int):
    """Set a single pixel on the Unicorn HAT."""
    if UNICORN_AVAILABLE:
        unicorn.set_pixel(x, y, r, g, b)
    else:
        logger.debug(f"Simulation: Set pixel ({x}, {y}) to RGB({r}, {g}, {b})")

def show():
    """Update the Unicorn HAT display."""
    if UNICORN_AVAILABLE:
        unicorn.show()
    else:
        logger.debug("Simulation: Display updated")

def clear():
    """Clear all pixels on the Unicorn HAT."""
    if UNICORN_AVAILABLE:
        unicorn.off()
        logger.info("Unicorn HAT turned off")
    else:
        logger.info("Simulation: Display cleared")

def validate_color(color: dict) -> tuple:
    """
    Validate and extract RGB values from a color dict.
    Returns (r, g, b) tuple or raises ValueError.
    """
    if not isinstance(color, dict):
        raise ValueError("Color must be an object with r, g, b keys")
    
    r = color.get('r', 0)
    g = color.get('g', 0)
    b = color.get('b', 0)
    
    for val, name in [(r, 'r'), (g, 'g'), (b, 'b')]:
        if not isinstance(val, int) or val < 0 or val > 255:
            raise ValueError(f"Color component '{name}' must be an integer between 0 and 255")
    
    return (r, g, b)

def validate_grid(grid: list) -> list:
    """
    Validate the grid structure.
    Expects an 8x8 array of color objects {r, g, b}.
    Returns validated grid or raises ValueError.
    """
    if not isinstance(grid, list) or len(grid) != GRID_HEIGHT:
        raise ValueError(f"Grid must be an array of {GRID_HEIGHT} rows")
    
    validated_grid = []
    for y, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != GRID_WIDTH:
            raise ValueError(f"Row {y} must be an array of {GRID_WIDTH} colors")
        
        validated_row = []
        for x, color in enumerate(row):
            try:
                validated_row.append(validate_color(color))
            except ValueError as e:
                raise ValueError(f"Invalid color at position ({x}, {y}): {e}")
        
        validated_grid.append(validated_row)
    
    return validated_grid

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'unicorn_available': UNICORN_AVAILABLE,
        'grid_size': {'width': GRID_WIDTH, 'height': GRID_HEIGHT}
    })

@app.route('/grid', methods=['POST'])
def update_grid():
    """
    Update the entire 8x8 grid.
    
    Expected JSON body:
    {
        "grid": [
            [{"r": 255, "g": 0, "b": 0}, ...],  // Row 0 (8 colors)
            ...                                   // 8 rows total
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'grid' not in data:
            return jsonify({'error': 'Request must include "grid" field'}), 400
        
        validated_grid = validate_grid(data['grid'])
        
        # Apply colors to the Unicorn HAT
        for y, row in enumerate(validated_grid):
            for x, (r, g, b) in enumerate(row):
                set_pixel(x, y, r, g, b)
        
        show()
        
        # Schedule auto-off after 10 seconds
        schedule_auto_off()
        
        # Save the original grid data (with dict format) to history
        save_grid_to_history(data['grid'])
        
        logger.info("Grid updated successfully")
        return jsonify({'status': 'success', 'message': 'Grid updated'})
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating grid: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/pixel', methods=['POST'])
def update_pixel():
    """
    Update a single pixel.
    
    Expected JSON body:
    {
        "x": 0,
        "y": 0,
        "color": {"r": 255, "g": 0, "b": 0}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        x = data.get('x')
        y = data.get('y')
        color = data.get('color')
        
        if x is None or y is None:
            return jsonify({'error': 'x and y coordinates required'}), 400
        
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return jsonify({'error': f'Coordinates must be within 0-{GRID_WIDTH-1}'}), 400
        
        if color is None:
            return jsonify({'error': 'color object required'}), 400
        
        r, g, b = validate_color(color)
        set_pixel(x, y, r, g, b)
        show()
        
        # Schedule auto-off after 10 seconds
        schedule_auto_off()
        
        logger.info(f"Pixel ({x}, {y}) updated to RGB({r}, {g}, {b})")
        return jsonify({'status': 'success', 'message': f'Pixel ({x}, {y}) updated'})
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating pixel: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear', methods=['POST'])
def clear_grid():
    """Clear all pixels (turn off all LEDs)."""
    try:
        # Cancel any pending auto-off timer
        cancel_auto_off()
        clear()
        logger.info("Grid cleared")
        return jsonify({'status': 'success', 'message': 'Grid cleared'})
    except Exception as e:
        logger.error(f"Error clearing grid: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/brightness', methods=['POST'])
def set_brightness():
    """
    Set display brightness.
    
    Expected JSON body:
    {
        "brightness": 0.5  // Value between 0.0 and 1.0
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'brightness' not in data:
            return jsonify({'error': 'brightness value required'}), 400
        
        brightness = data['brightness']
        
        if not isinstance(brightness, (int, float)) or brightness < 0 or brightness > 1:
            return jsonify({'error': 'brightness must be a number between 0 and 1'}), 400
        
        if UNICORN_AVAILABLE:
            unicorn.brightness(brightness)
            show()
        
        logger.info(f"Brightness set to {brightness}")
        return jsonify({'status': 'success', 'message': f'Brightness set to {brightness}'})
    
    except Exception as e:
        logger.error(f"Error setting brightness: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    Get the last 10 submitted grids.
    
    Returns:
    {
        "grids": [
            {
                "id": "2024-12-05T10:30:00.000000",
                "grid": [[{"r": 255, "g": 0, "b": 0}, ...], ...],
                "timestamp": "2024-12-05T10:30:00.000000"
            },
            ...
        ]
    }
    """
    try:
        return jsonify({'grids': list(grid_history)})
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Initialize Unicorn HAT on startup
init_unicorn()

if __name__ == '__main__':
    # Run on all interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=False)
