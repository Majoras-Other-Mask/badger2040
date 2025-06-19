import badger2040
import badger_os

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

ARROW_THICKNESS = 3
ARROW_WIDTH = 18
ARROW_HEIGHT = 14
ARROW_PADDING = 2

TEXT_PADDING = 4
TEXT_WIDTH = WIDTH - TEXT_PADDING - TEXT_PADDING - ARROW_WIDTH

# ASCII art file path
ASCII_ART_FILE = "/ascii_art/misc_art.txt"

# ------------------------------
#      Drawing functions
# ------------------------------

def draw_up(x, y, width, height, thickness, padding):
    """Draw an upward arrow"""
    border = (thickness // 4) + padding
    display.line(x + border, y + height - border,
                 x + (width // 2), y + border)
    display.line(x + (width // 2), y + border,
                 x + width - border, y + height - border)

def draw_down(x, y, width, height, thickness, padding):
    """Draw a downward arrow"""
    border = (thickness // 2) + padding
    display.line(x + border, y + border,
                 x + (width // 2), y + height - border)
    display.line(x + (width // 2), y + height - border,
                 x + width - border, y + border)

def draw_frame():
    """Draw the frame with navigation arrows"""
    display.set_pen(15)
    display.clear()
    display.set_pen(12)
    display.rectangle(WIDTH - ARROW_WIDTH, 0, ARROW_WIDTH, HEIGHT)
    display.set_pen(0)
    
    # Draw up arrow if not on first art piece
    if state["current_art"] > 0:
        draw_up(WIDTH - ARROW_WIDTH, (HEIGHT // 4) - (ARROW_HEIGHT // 2),
                ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
    
    # Draw down arrow if not on last art piece
    if state["current_art"] < len(ascii_arts) - 1:
        draw_down(WIDTH - ARROW_WIDTH, ((HEIGHT * 3) // 4) - (ARROW_HEIGHT // 2),
                  ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)

def parse_ascii_arts(file_content):
    """Parse the ASCII art file into individual art pieces"""
    arts = []
    current_art = []
    current_name = ""
    
    lines = file_content.strip().split('\n')
    
    for line in lines:
        line = line.rstrip()  # Remove trailing whitespace
        
        # Check if this line looks like a name (all caps, no special chars except spaces)
        if line and line.isupper() and not any(c in line for c in '/\\()[]{}|*^_.,<>@#~&%-+='):
            # If we have accumulated art, save it
            if current_art:
                arts.append({
                    'name': current_name.strip(),
                    'art': current_art
                })
                current_art = []
            current_name = line
        else:
            # This is part of the ASCII art
            if line or current_art:  # Add line if it's not empty, or if we've already started collecting art
                current_art.append(line)
    
    # Don't forget the last piece
    if current_art:
        arts.append({
            'name': current_name.strip(),
            'art': current_art
        })
    
    return arts

def display_ascii_art():
    """Display the current ASCII art piece"""
    draw_frame()
    
    if not ascii_arts:
        display.set_pen(0)
        display.set_font("bitmap8")
        display.text("No ASCII art found!", TEXT_PADDING, HEIGHT // 2, WIDTH, 0.5)
        display.update()
        return
    
    current = ascii_arts[state["current_art"]]
    art_lines = current['art']
    name = current['name']
    
    # Display the name at the top
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text(name, TEXT_PADDING, 10, TEXT_WIDTH, 0.4)
    
    # Calculate starting position for the art to center it
    line_height = 10
    total_art_height = len(art_lines) * line_height
    start_y = max(25, (HEIGHT - total_art_height) // 2)
    
    # Display the ASCII art
    display.set_font("bitmap6")  # Smaller font for the art
    y_pos = start_y
    
    for line in art_lines:
        if y_pos < HEIGHT - 10:  # Make sure we don't go off screen
            # Center the line horizontally
            line_width = display.measure_text(line, 0.7)
            x_pos = max(TEXT_PADDING, (TEXT_WIDTH - line_width) // 2)
            display.text(line, x_pos, y_pos, TEXT_WIDTH, 0.7)
            y_pos += line_height
    
    # Show current position indicator
    position_text = f"{state['current_art'] + 1}/{len(ascii_arts)}"
    pos_width = display.measure_text(position_text, 0.4)
    display.text(position_text, TEXT_WIDTH - pos_width, HEIGHT - 15, TEXT_WIDTH, 0.4)
    
    display.update()

# ------------------------------
#        Program setup
# ------------------------------

# Global variables
state = {
    "current_art": 0
}
badger_os.state_load("ascii_art", state)

# Create display
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_FAST)

# Load ASCII arts
ascii_arts = []
try:
    with open(ASCII_ART_FILE, "r") as f:
        file_content = f.read()
    ascii_arts = parse_ascii_arts(file_content)
    print(f"Loaded {len(ascii_arts)} ASCII art pieces")
except OSError as e:
    print(f"Error loading ASCII art file: {e}")
    ascii_arts = []

# Make sure current_art is within bounds
if state["current_art"] >= len(ascii_arts):
    state["current_art"] = 0

changed = True

# ------------------------------
#       Main program loop
# ------------------------------

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    # Navigation buttons
    if display.pressed(badger2040.BUTTON_UP):
        if state["current_art"] > 0:
            state["current_art"] -= 1
            changed = True

    if display.pressed(badger2040.BUTTON_DOWN):
        if state["current_art"] < len(ascii_arts) - 1:
            state["current_art"] += 1
            changed = True
    
    # Alternative navigation with A and C buttons
    if display.pressed(badger2040.BUTTON_A):
        if state["current_art"] > 0:
            state["current_art"] -= 1
            changed = True
    
    if display.pressed(badger2040.BUTTON_C):
        if state["current_art"] < len(ascii_arts) - 1:
            state["current_art"] += 1
            changed = True

    # Button B could cycle through different display modes in the future
    if display.pressed(badger2040.BUTTON_B):
        # For now, just refresh the display
        changed = True

    if changed:
        display_ascii_art()
        badger_os.state_save("ascii_art", state)
        changed = False

    display.halt()