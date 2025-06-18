import badger2040
import jpegdec
import pngdec
import os
import badger_os

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 104

COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

BADGE_DIR = "/badges"
BADGE_PATTERN = "badge"

# Badge state
state = {
    "current_badge": 0
}

# List to store badge files
badge_files = []

# Badge data storage
badges = []

# ------------------------------
#      Utility functions
# ------------------------------

def truncatestring(text, text_size, width):
    """Reduce the size of a string until it fits within a given width"""
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            return text

def load_badge_files():
    """Find all badge files in the badges directory"""
    global badge_files
    try:
        files = os.listdir(BADGE_DIR)
        # Filter for .txt files that start with our pattern
        badge_files = [f for f in files if f.startswith(BADGE_PATTERN) and f.endswith('.txt')]
        badge_files.sort()  # Sort alphabetically
        print(f"Found {len(badge_files)} badge files: {badge_files}")
    except OSError:
        print("Badges directory not found, creating with default badge")
        try:
            os.mkdir(BADGE_DIR)
        except OSError:
            pass
        create_default_badge()
        badge_files = ["badge.txt"]

def create_default_badge():
    """Create a default badge file if none exist"""
    default_text = """mustelid inc
H. Badger
RP2040
2MB Flash
E ink
296x128px
/badges/badge.jpg
"""
    try:
        with open(f"{BADGE_DIR}/badge.txt", "w") as f:
            f.write(default_text)
            f.flush()
    except OSError:
        print("Could not create default badge file")

def load_badge_data(filename):
    """Load badge data from a specific file"""
    try:
        badge_path = f"{BADGE_DIR}/{filename}"
        with open(badge_path, "r") as badge_file:
            company = badge_file.readline().strip()
            name = badge_file.readline().strip()
            detail1_title = badge_file.readline().strip()
            detail1_text = badge_file.readline().strip()
            detail2_title = badge_file.readline().strip()
            detail2_text = badge_file.readline().strip()
            badge_image = badge_file.readline().strip()
            
            return {
                'company': company,
                'name': name,
                'detail1_title': detail1_title,
                'detail1_text': detail1_text,
                'detail2_title': detail2_title,
                'detail2_text': detail2_text,
                'badge_image': badge_image,
                'filename': filename
            }
    except OSError:
        print(f"Could not load badge file: {filename}")
        return None

def load_all_badges():
    """Load data for all badge files"""
    global badges
    badges = []
    for filename in badge_files:
        badge_data = load_badge_data(filename)
        if badge_data:
            badges.append(badge_data)
    
    if not badges:
        print("No valid badges found!")
        create_default_badge()
        load_badge_files()
        badge_data = load_badge_data(badge_files[0])
        if badge_data:
            badges.append(badge_data)

# ------------------------------
#      Drawing functions
# ------------------------------

def has_valid_image(badge_data):
    """Check if the badge has a valid image file"""
    image_path = badge_data.get('badge_image', '').strip()
    
    # No image path provided or empty
    if not image_path:
        return False
    
    # Check if file exists
    try:
        with open(image_path, 'rb'):
            pass
        return True
    except OSError:
        return False

def draw_badge():
    """Draw the current badge"""
    if not badges:
        return
    
    current_badge = badges[state["current_badge"]]
    has_image = has_valid_image(current_badge)
    
    # Determine text width based on whether we have an image
    if has_image:
        available_text_width = TEXT_WIDTH
        name_available_width = TEXT_WIDTH - NAME_PADDING
    else:
        available_text_width = WIDTH - (LEFT_PADDING * 2)
        name_available_width = WIDTH - (LEFT_PADDING * 2)
    
    display.set_pen(0)
    display.clear()

    # Draw image only if it exists and is valid
    if has_image:
        try:
            # Try PNG first, then JPEG
            try:
                png.open_file(current_badge['badge_image'])
                png.decode(WIDTH - IMAGE_WIDTH, 0)
            except (OSError, RuntimeError):
                jpeg.open_file(current_badge['badge_image'])
                jpeg.decode(WIDTH - IMAGE_WIDTH, 0)
            
            # Draw a border around the image area
            display.set_pen(0)
            display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
            display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
            display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
            display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)
        except (OSError, RuntimeError):
            # Image failed to load, treat as no image
            has_image = False
            available_text_width = WIDTH - (LEFT_PADDING * 2)
            name_available_width = WIDTH - (LEFT_PADDING * 2)

    # Draw the company
    display.set_pen(15)  # White background
    display.set_font("serif")
    company_text = truncatestring(current_badge['company'], COMPANY_TEXT_SIZE, available_text_width)
    display.text(company_text, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, WIDTH, COMPANY_TEXT_SIZE)

    # Draw a white background behind the name
    name_bg_width = available_text_width if not has_image else TEXT_WIDTH
    display.set_pen(15)
    display.rectangle(1, COMPANY_HEIGHT + 1, name_bg_width, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    display.set_pen(0)
    display.set_font("sans")
    name_size = 2.0  # Starting scale
    name_text = current_badge['name']
    while True:
        name_length = display.measure_text(name_text, name_size)
        if name_length >= name_available_width and name_size >= 0.1:
            name_size -= 0.01
        else:
            # Center the name in the available space
            if has_image:
                x_pos = (TEXT_WIDTH - name_length) // 2
            else:
                x_pos = (WIDTH - name_length) // 2
            display.text(name_text, x_pos, (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1, WIDTH, name_size)
            break

    # Draw white backgrounds behind the details
    details_bg_width = available_text_width if not has_image else TEXT_WIDTH
    display.set_pen(15)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT * 2, details_bg_width, DETAILS_HEIGHT - 1)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT, details_bg_width, DETAILS_HEIGHT - 1)

    # Draw the first detail's title and text
    display.set_pen(0)
    display.set_font("sans")
    detail1_title = truncatestring(current_badge['detail1_title'], DETAILS_TEXT_SIZE, available_text_width)
    title1_length = display.measure_text(detail1_title, DETAILS_TEXT_SIZE)
    detail1_text = truncatestring(current_badge['detail1_text'], DETAILS_TEXT_SIZE,
                                  available_text_width - DETAIL_SPACING - title1_length)
    
    display.text(detail1_title, LEFT_PADDING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), WIDTH, DETAILS_TEXT_SIZE)
    display.text(detail1_text, LEFT_PADDING + title1_length + DETAIL_SPACING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), WIDTH, DETAILS_TEXT_SIZE)

    # Draw the second detail's title and text
    detail2_title = truncatestring(current_badge['detail2_title'], DETAILS_TEXT_SIZE, available_text_width)
    title2_length = display.measure_text(detail2_title, DETAILS_TEXT_SIZE)
    detail2_text = truncatestring(current_badge['detail2_text'], DETAILS_TEXT_SIZE,
                                  available_text_width - DETAIL_SPACING - title2_length)
    
    display.text(detail2_title, LEFT_PADDING, HEIGHT - (DETAILS_HEIGHT // 2), WIDTH, DETAILS_TEXT_SIZE)
    display.text(detail2_text, LEFT_PADDING + title2_length + DETAIL_SPACING, HEIGHT - (DETAILS_HEIGHT // 2), WIDTH, DETAILS_TEXT_SIZE)

    # Draw badge indicator if multiple badges
    if len(badges) > 1:
        # Draw dots to show current badge
        for i in range(len(badges)):
            x = WIDTH - 20 - (len(badges) - 1 - i) * 8
            y = 5
            display.set_pen(0)
            if i == state["current_badge"]:
                display.circle(x, y, 3)  # Filled circle for current
            else:
                display.circle(x, y, 2)  # Smaller circle for others
                display.set_pen(15)
                display.circle(x, y, 1)  # Hollow center
    
    display.update()

# ------------------------------
#        Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)
display.set_thickness(2)

jpeg = jpegdec.JPEG(display.display)
png = pngdec.PNG(display.display)

# Load state
badger_os.state_load("badge_switcher", state)

# Load all badge files
load_badge_files()
load_all_badges()

# Ensure current_badge is within valid range
if state["current_badge"] >= len(badges):
    state["current_badge"] = 0

changed = True

# ------------------------------
#       Main program loop
# ------------------------------

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    # Navigate between badges with UP/DOWN arrows
    if display.pressed(badger2040.BUTTON_UP) and len(badges) > 1:
        state["current_badge"] = (state["current_badge"] - 1) % len(badges)
        changed = True
        print(f"Switched to badge {state['current_badge']}: {badges[state['current_badge']]['filename']}")

    if display.pressed(badger2040.BUTTON_DOWN) and len(badges) > 1:
        state["current_badge"] = (state["current_badge"] + 1) % len(badges)
        changed = True
        print(f"Switched to badge {state['current_badge']}: {badges[state['current_badge']]['filename']}")
    
    # Button A: Reload badge files (useful if you added new badges)
    if display.pressed(badger2040.BUTTON_A):
        print("Reloading badge files...")
        load_badge_files()
        load_all_badges()
        if state["current_badge"] >= len(badges):
            state["current_badge"] = 0
        changed = True
    
    # Update display if something changed
    if changed:
        draw_badge()
        badger_os.state_save("badge_switcher", state)
        changed = False

    # If on battery, halt the Badger to save power
    display.halt()