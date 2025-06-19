import time
import machine
import badger2040
import badger_os
import gc

# Game constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT
UI_HEIGHT = 25  # Height reserved for UI
CELL_SIZE = 4  # Each cell is 4x4 pixels
GRID_WIDTH = WIDTH // CELL_SIZE  # 74 cells wide
GRID_HEIGHT = (HEIGHT - UI_HEIGHT) // CELL_SIZE  # ~25 cells tall (adjusted for UI)

# Game state
state = {
    "paused": True,
    "pattern": 0,
    "generation": 0
}

# Create display
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_FAST)

# Button references for interrupt handling
button_a = machine.Pin(badger2040.BUTTON_A, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_b = machine.Pin(badger2040.BUTTON_B, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_c = machine.Pin(badger2040.BUTTON_C, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_up = machine.Pin(badger2040.BUTTON_UP, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_down = machine.Pin(badger2040.BUTTON_DOWN, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Global variables for button handling
button_pressed = None
last_update = 0

# Initialize grids - current and next generation
current_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
next_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Predefined patterns
patterns = [
    # R-pentomino - Chaotic growth pattern, runs for ~1100 generations
    {
        "name": "R-pentomino",
        "cells": [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)]
    },
    # Acorn - Small pattern that grows to 633 cells before stabilizing at gen 5206
    {
        "name": "Acorn",
        "cells": [(1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2)]
    },
    # Diehard - Dies out completely after exactly 130 generations
    {
        "name": "Diehard", 
        "cells": [(6, 0), (0, 1), (1, 1), (1, 2), (5, 2), (6, 2), (7, 2)]
    },
    # Gosper Glider Gun - Creates a stream of gliders
    {
        "name": "Glider Gun",
        "cells": [
            # Left block
            (0, 4), (0, 5), (1, 4), (1, 5),
            # Main body
            (10, 4), (10, 5), (10, 6), (11, 3), (11, 7), (12, 2), (12, 8),
            (13, 2), (13, 8), (14, 5), (15, 3), (15, 7), (16, 4), (16, 5), (16, 6),
            (17, 5),
            # Right section
            (20, 2), (20, 3), (20, 4), (21, 2), (21, 3), (21, 4), (22, 1), (22, 5),
            (24, 0), (24, 1), (24, 5), (24, 6),
            # Right block
            (34, 2), (34, 3), (35, 2), (35, 3)
        ]
    },
    # B-heptomino - Complex evolution
    {
        "name": "B-heptomino",
        "cells": [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2), (2, 2), (3, 2)]
    },
    # Spaceship (Lightweight spaceship)
    {
        "name": "Spaceship",
        "cells": [(0, 1), (3, 1), (4, 2), (0, 3), (4, 3), (1, 4), (2, 4), (3, 4), (4, 4)]
    },
    # 10-cell row - Evolves into complex stable pattern
    {
        "name": "10-cell row",
        "cells": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0)]
    },
    # Pulsar - Large 13x13 oscillator with period 3
    {
        "name": "Pulsar",
        "cells": [
            # Top
            (2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0),
            # Upper middle
            (0, 2), (5, 2), (7, 2), (12, 2),
            (0, 3), (5, 3), (7, 3), (12, 3),
            (0, 4), (5, 4), (7, 4), (12, 4),
            # Center gap
            (2, 5), (3, 5), (4, 5), (8, 5), (9, 5), (10, 5),
            (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
            # Lower middle
            (0, 8), (5, 8), (7, 8), (12, 8),
            (0, 9), (5, 9), (7, 9), (12, 9),
            (0, 10), (5, 10), (7, 10), (12, 10),
            # Bottom
            (2, 12), (3, 12), (4, 12), (8, 12), (9, 12), (10, 12)
        ]
    },
    # Random soup - High density for interesting interactions
    {
        "name": "Random",
        "cells": []  # Will be filled randomly
    }
]

def clear_grid():
    """Clear the grid"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            current_grid[y][x] = 0

def load_pattern(pattern_index):
    """Load a predefined pattern into the grid"""
    clear_grid()
    pattern = patterns[pattern_index]
    
    if pattern["name"] == "Random":
        # Create random pattern with higher density for more action
        import random
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                current_grid[y][x] = 1 if random.random() < 0.4 else 0
    else:
        # Load predefined pattern with better positioning
        if pattern["name"] == "Glider Gun":
            # Position glider gun in upper left to give gliders room to travel
            offset_x = 5
            offset_y = 2
        elif pattern["name"] == "Pulsar":
            # Center the pulsar
            offset_x = GRID_WIDTH // 2 - 6
            offset_y = GRID_HEIGHT // 2 - 6
        elif pattern["name"] == "10-cell row":
            # Center horizontally, place in upper third
            offset_x = GRID_WIDTH // 2 - 5
            offset_y = GRID_HEIGHT // 3
        else:
            # Center other patterns
            offset_x = GRID_WIDTH // 2 - 3
            offset_y = GRID_HEIGHT // 2 - 3
        
        for x, y in pattern["cells"]:
            grid_x = offset_x + x
            grid_y = offset_y + y
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                current_grid[grid_y][grid_x] = 1

def count_neighbors(x, y):
    """Count living neighbors for a cell"""
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                count += current_grid[ny][nx]
    return count

def update_game():
    """Update the game state according to Conway's rules"""
    global current_grid, next_grid
    
    # Calculate next generation
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            neighbors = count_neighbors(x, y)
            current_cell = current_grid[y][x]
            
            if current_cell == 1:  # Living cell
                if neighbors < 2 or neighbors > 3:
                    next_grid[y][x] = 0  # Dies
                else:
                    next_grid[y][x] = 1  # Survives
            else:  # Dead cell
                if neighbors == 3:
                    next_grid[y][x] = 1  # Born
                else:
                    next_grid[y][x] = 0  # Stays dead
    
    # Swap grids
    current_grid, next_grid = next_grid, current_grid
    state["generation"] += 1

def draw_grid():
    """Draw the current grid state"""
    display.set_pen(15)  # White background
    display.clear()
    
    # Draw living cells (offset by UI height)
    display.set_pen(0)  # Black for living cells
    ui_height = 25
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if current_grid[y][x] == 1:
                pixel_x = x * CELL_SIZE
                pixel_y = y * CELL_SIZE + ui_height
                # Only draw if within screen bounds
                if pixel_y + CELL_SIZE <= HEIGHT:
                    display.rectangle(pixel_x, pixel_y, CELL_SIZE - 1, CELL_SIZE - 1)
    
    # Draw UI
    draw_ui()
    display.update()

def draw_ui():
    """Draw the user interface"""
    # Top status bar with white background for better contrast
    display.set_pen(15)  # White background
    display.rectangle(0, 0, WIDTH, 25)
    
    # Border around status bar
    display.set_pen(0)
    display.line(0, 24, WIDTH, 24)
    
    # Pattern name (left side)
    display.set_font("sans")
    pattern_name = patterns[state["pattern"]]["name"]
    display.text(pattern_name, 4, 15, WIDTH, 0.6)
    
    # Generation counter (right side)
    gen_text = f"Gen: {state['generation']}"
    gen_width = display.measure_text(gen_text, 0.6)
    display.text(gen_text, WIDTH - gen_width - 4, 15, WIDTH, 0.6)
    
    # Pause indicator (center, larger)
    if state["paused"]:
        pause_text = "PAUSED"
        pause_width = display.measure_text(pause_text, 0.8)
        # Dark background for pause indicator
        display.set_pen(12)
        display.rectangle((WIDTH - pause_width) // 2 - 2, 2, pause_width + 4, 20)
        display.set_pen(0)
        display.text(pause_text, (WIDTH - pause_width) // 2, 15, WIDTH, 0.8)

def button_handler(pin):
    """Handle button press interrupts"""
    global button_pressed
    time.sleep(0.01)  # Debounce
    if pin.value():
        button_pressed = pin
        
        # Check for A+C combination to exit to launcher
        if button_a.value() and button_c.value():
            badger_os.state_save("game_of_life", state)
            machine.reset()

# Set up button interrupts
button_a.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
button_b.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
button_c.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
button_up.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
button_down.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)

# Load saved state
badger_os.state_load("game_of_life", state)

# Initialize with first pattern
if state["pattern"] >= len(patterns):
    state["pattern"] = 0
load_pattern(state["pattern"])

# Main game loop
draw_grid()

while True:
    display.keepalive()
    
    current_time = time.ticks_ms()
    
    # Handle button presses
    if button_pressed:
        if button_pressed == button_a:
            # Previous pattern
            state["pattern"] = (state["pattern"] - 1) % len(patterns)
            state["generation"] = 0
            load_pattern(state["pattern"])
            draw_grid()
            
        elif button_pressed == button_b:
            # Toggle pause
            state["paused"] = not state["paused"]
            draw_grid()
            
        elif button_pressed == button_c:
            # Next pattern
            state["pattern"] = (state["pattern"] + 1) % len(patterns)
            state["generation"] = 0
            load_pattern(state["pattern"])
            draw_grid()
            
        elif button_pressed == button_up:
            # Step forward one generation (when paused)
            if state["paused"]:
                update_game()
                draw_grid()
                
        elif button_pressed == button_down:
            # Reset current pattern
            state["generation"] = 0
            load_pattern(state["pattern"])
            draw_grid()
        
        # Save state after any button press
        badger_os.state_save("game_of_life", state)
        button_pressed = None
    
    # Update game if not paused (every 500ms)
    if not state["paused"] and time.ticks_diff(current_time, last_update) > 500:
        update_game()
        draw_grid()
        last_update = current_time
        
        # Collect garbage periodically to avoid memory issues
        if state["generation"] % 10 == 0:
            gc.collect()
    
    time.sleep(0.01)  # Small delay to prevent excessive CPU usage