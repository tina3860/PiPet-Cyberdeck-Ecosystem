from time import sleep
from PIL import Image
import sys
import os

# Import Whisplay driver
sys.path.append("/home/tina386/Whisplay/Driver")
from WhisPlay import WhisPlayBoard

# Initialize board
board = WhisPlayBoard()
board.set_backlight(50)  # 50% brightness

def load_image_rgb565(filepath):
    """Convert image to RGB565 format for Whisplay"""
    img = Image.open(filepath).convert('RGB')
    
    # Resize to screen size if needed
    img = img.resize((board.LCD_WIDTH, board.LCD_HEIGHT))
    
    pixel_data = []
    for y in range(board.LCD_HEIGHT):
        for x in range(board.LCD_WIDTH):
            r, g, b = img.getpixel((x, y))
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])
    
    return pixel_data

# Load and display status page
try:
    print("Loading status page...")
    image_data = load_image_rgb565('assets/ui/Status_page.png')
    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, image_data)
    print("✓ Status page displayed!")
    
    print("Press Ctrl+C to exit...")
    while True:
        sleep(0.1)
        
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    board.cleanup()
