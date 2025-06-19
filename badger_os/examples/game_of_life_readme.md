# Conway's Game of Life for Badger 2040

A feature-rich implementation of Conway's Game of Life designed specifically for the Pimoroni Badger 2040 e-ink display. This version includes fascinating patterns, proper button handling, and a clean user interface optimized for the e-ink screen.

## Features

- **9 Built-in Patterns**: From simple spaceships to complex chaotic growers
- **Interrupt-driven Controls**: Reliable button handling without input conflicts
- **State Persistence**: Remembers your last pattern and settings between runs
- **Visual Feedback**: Clear UI showing pattern name, generation count, and status
- **Memory Optimized**: Includes garbage collection to prevent memory issues
- **E-ink Optimized**: High contrast display with readable fonts

## Installation

1. Copy `game_of_life.py` to your Badger 2040's `/examples` directory
2. Create an icon file `icon-game_of_life.png` (optional, for launcher integration)
3. Reset your Badger 2040 or launch from the file menu

## Controls

| Button | Function |
|--------|----------|
| **A** | Previous pattern |
| **B** | Toggle pause/play |
| **C** | Next pattern |
| **UP** | Step forward one generation (when paused) |
| **DOWN** | Reset current pattern |

## Pattern Gallery

### 1. R-pentomino
- **Description**: The most famous chaotic pattern in Conway's Game of Life
- **Behavior**: Starts with just 5 cells, grows chaotically for over 1,100 generations
- **Why it's interesting**: Completely unpredictable evolution from a tiny seed

### 2. Acorn
- **Description**: A 7-cell pattern that creates explosive growth
- **Behavior**: Grows to 633 cells before stabilizing after 5,206 generations
- **Why it's interesting**: Demonstrates how small patterns can create lasting complexity

### 3. Diehard
- **Description**: A pattern that lives exactly 130 generations before dying
- **Behavior**: Creates complex structures that eventually fade to nothing
- **Why it's interesting**: Perfect example of finite-lived patterns with dramatic evolution

### 4. Glider Gun
- **Description**: The famous Gosper Glider Gun
- **Behavior**: Continuously produces gliders that travel across the screen
- **Why it's interesting**: Creates infinite growth and demonstrates period-30 oscillation

### 5. B-heptomino
- **Description**: A 7-cell pattern that creates chaotic evolution
- **Behavior**: Grows and changes unpredictably before stabilizing
- **Why it's interesting**: Another example of small patterns with complex behavior

### 6. Spaceship
- **Description**: A lightweight spaceship that travels
- **Behavior**: Moves diagonally across the grid while maintaining its shape
- **Why it's interesting**: Demonstrates moving patterns that don't grow

### 7. 10-cell row
- **Description**: A simple horizontal line of 10 cells
- **Behavior**: Evolves into a complex stable configuration
- **Why it's interesting**: Shows how simple initial conditions can create intricate final states

### 8. Pulsar
- **Description**: A large, symmetric oscillator
- **Behavior**: "Breathes" with period 3, expanding and contracting
- **Why it's interesting**: Beautiful symmetric pattern that demonstrates stable oscillation

### 9. Random
- **Description**: 40% density random configuration
- **Behavior**: Creates chaotic interactions and emergent patterns
- **Why it's interesting**: Every run is different; demonstrates emergent complexity

## Technical Details

### Display Specifications
- **Grid Size**: 74 × 25 cells (adjusted for UI space)
- **Cell Size**: 4×4 pixels per cell
- **Display Resolution**: 296×128 pixels
- **UI Height**: 25 pixels reserved for status information

### Performance
- **Update Rate**: 500ms per generation when running
- **Memory Management**: Automatic garbage collection every 10 generations
- **Button Debouncing**: 10ms debounce with interrupt-driven handling

### Code Structure
```
game_of_life.py
├── Pattern definitions (9 built-in patterns)
├── Grid management (current/next generation buffers)
├── Game logic (Conway's rules implementation)
├── Display rendering (optimized for e-ink)
├── Button handling (interrupt-driven)
└── State persistence (saves between sessions)
```

## Conway's Game of Life Rules

The simulation follows the classic Conway's Game of Life rules:

1. **Birth**: A dead cell with exactly 3 living neighbors becomes alive
2. **Survival**: A living cell with 2 or 3 living neighbors stays alive
3. **Death**: A living cell with fewer than 2 or more than 3 neighbors dies

These simple rules create surprisingly complex behaviors and patterns.

## Usage Tips

### For Best Experience
- Start with **R-pentomino** or **Acorn** for fascinating long-term evolution
- Use **Glider Gun** to see continuous pattern generation
- Try **Diehard** for a dramatic countdown experience
- Use **UP button** when paused to step through interesting moments slowly

### Button Handling
- The game uses interrupt-driven button handling to prevent input conflicts
- All button presses are debounced and processed cleanly
- State is automatically saved after each button press

### Performance Notes
- The game automatically manages memory to prevent crashes
- Complex patterns may slow down slightly on very dense configurations
- E-ink display updates are optimized for readability over speed

## Customization

### Adding New Patterns
To add your own patterns, modify the `patterns` list in the code:

```python
{
    "name": "Your Pattern",
    "cells": [(x1, y1), (x2, y2), ...]  # List of living cell coordinates
}
```

### Adjusting Speed
Change the update interval by modifying this line:
```python
if not state["paused"] and time.ticks_diff(current_time, last_update) > 500:
```
Replace `500` with your desired milliseconds between generations.

### Grid Size
Modify these constants to change the grid resolution:
```python
CELL_SIZE = 4  # Pixels per cell
UI_HEIGHT = 25  # Pixels reserved for UI
```

## Troubleshooting

### Common Issues
- **Buttons not responding**: The game uses interrupt-driven buttons - if stuck, reset the device
- **Memory errors**: The game includes automatic garbage collection, but very long runs on complex patterns may require a reset
- **Pattern appears cut off**: Some patterns are positioned optimally for the small screen - this is normal

### Reset Options
- **Soft reset**: Press DOWN button to reset current pattern
- **Pattern reset**: Use A/C buttons to cycle to a different pattern
- **Full reset**: Restart the Badger 2040

## Credits

- **Conway's Game of Life**: Created by mathematician John Conway
- **Badger 2040**: Hardware by Pimoroni
- **Implementation**: Optimized for e-ink displays with interrupt-driven controls
- **Pattern Sources**: Classic Life patterns from the Conway's Life community

## License

This implementation is provided under the same MIT license as the Badger 2040 firmware examples.