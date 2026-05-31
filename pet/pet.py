from time import sleep
from PIL import Image, ImageDraw
import sys
import os
import threading

# Import Whisplay driver
sys.path.append("/home/tina386/Whisplay/Driver")
from WhisPlay import WhisPlayBoard

# Initialize board
board = WhisPlayBoard()
board.set_backlight(50)

# ============================================
# CONFIGURATION
# ============================================

# Menu structure
MENUS = {
    "top": ["stats", "feed", "play", "sleep"],
    "bottom": ["attention", "medicine", "clean", "pause"]
}

# Icon positions on screen (32x32 icons)
ICON_POSITIONS = {
    "top": [
        (15, 20, 35, 35),
        (65, 15, 45, 45),
        (125, 20, 35, 35),
        (185, 20, 35, 35),
    ],
    "bottom": [
        (15, 229, 35, 35),
        (65, 220, 45, 45),
        (125, 227, 35, 35),
        (185, 227, 40, 40),
    ]
}

# Game state
game_state = {
    "current_menu": "top",
    "selected_index": 0,
    "running": True,
}

# Animation state
animation_frame = 0
stop_animation = False
overlay_img = None  # Cached overlay

# ============================================
# IMAGE LOADING FUNCTIONS
# ============================================

def rgb565_to_pil(rgb565_data):
    """Convert RGB565 byte array to PIL Image"""
    img = Image.new('RGB', (board.LCD_WIDTH, board.LCD_HEIGHT))
    pixels = []
    for i in range(0, len(rgb565_data), 2):
        rgb565 = (rgb565_data[i] << 8) | rgb565_data[i + 1]
        r = ((rgb565 >> 11) & 0x1F) << 3
        g = ((rgb565 >> 5) & 0x3F) << 2
        b = (rgb565 & 0x1F) << 3
        pixels.append((r, g, b))
    img.putdata(pixels)
    return img

def pil_to_rgb565(img):
    """Convert PIL Image to RGB565 byte array"""
    pixel_data = []
    for y in range(board.LCD_HEIGHT):
        for x in range(board.LCD_WIDTH):
            r, g, b = img.getpixel((x, y))
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])
    return pixel_data

def load_gif_frames_pil(filepath):
    """Load GIF frames as PIL Images"""
    gif = Image.open(filepath)
    frames = []

    for frame_num in range(gif.n_frames):
        gif.seek(frame_num)
        frame_img = gif.convert('RGB')
        frame_img = frame_img.resize((board.LCD_WIDTH, board.LCD_HEIGHT))
        frames.append(frame_img)

    return frames

def load_icon_rgba(filepath, size=(32, 32)):
    """Load icon with transparency as PIL Image"""
    img = Image.open(filepath).convert('RGBA')
    img = img.resize(size, Image.Resampling.NEAREST)
    return img

def create_overlay():
    """Create menu overlay with border"""
    global overlay_img

    overlay_img = Image.new('RGBA', (board.LCD_WIDTH, board.LCD_HEIGHT), (0, 0, 0, 0))

    # Paste menu bars
    overlay_img.paste(top_bar_img, (0, 0), top_bar_img)
    overlay_img.paste(bottom_bar_img, (0, board.LCD_HEIGHT - bottom_bar_img.height), bottom_bar_img)

    # Paste icons
    for menu_type in ["top", "bottom"]:
        for idx, icon_name in enumerate(MENUS[menu_type]):
            if icon_name in icons:
                x, y, w, h = ICON_POSITIONS[menu_type][idx]
                icon = icons[icon_name].resize((w, h), Image.Resampling.NEAREST)
                overlay_img.paste(icon, (x, y), icon)

    # Draw selection border
    draw = ImageDraw.Draw(overlay_img)
    x, y, w, h = ICON_POSITIONS[game_state["current_menu"]][game_state["selected_index"]]
    border_color = (134, 101, 101, 255)  # #866565
    border_width = 3
    draw.rectangle([x, y, x+w, y+h], outline=border_color, width=border_width)

# ============================================
# LOAD ASSETS
# ============================================

print("Loading assets...")

# Load pet animation as PIL Images
pet_frames = load_gif_frames_pil("assets/animations/idle.gif")
print(f"✓ Pet animation ({len(pet_frames)} frames)")

# Show first frame immediately
board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, pil_to_rgb565(pet_frames[0]))
print("Display on! Continuing to load assets...")

# Load menu bars
top_bar_img = Image.open("assets/ui/stats/menu-bars/top-menu-bar.png").convert('RGBA')
bottom_bar_img = Image.open("assets/ui/stats/menu-bars/bottom-menu-bar.png").convert('RGBA')
print("✓ Menu bars")

# Load icons
icons = {}
icon_files = {
    "stats": "stats-icon.png",
    "feed": "fish-icon.png",
    "play": "yarnball-icon.png",
    "sleep": "lightning-icon.png",
    "attention": "heart-icon.png",
    "medicine": "pill-icon.png",
    "clean": "bubble-icon.png",
    "pause": "vacation-icon.png"
}

for name, filename in icon_files.items():
    icons[name] = load_icon_rgba(f"assets/animations/{filename}", size=(32, 32))
    print(f"✓ {name} icon")

print("\nAssets loaded! Creating overlay...")

# Create initial overlay
create_overlay()

# ============================================
# ANIMATION THREAD
# ============================================

def animation_loop():
    """Animate the display"""
    global animation_frame, stop_animation

    while not stop_animation:
        if len(pet_frames) > 0 and overlay_img is not None:
            # Get current animation frame (already PIL Image)
            frame_img = pet_frames[animation_frame].copy()

            # Composite overlay on top
            frame_img.paste(overlay_img, (0, 0), overlay_img)

            # Convert to RGB565 and draw
            pixel_data = pil_to_rgb565(frame_img)
            board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, pixel_data)

            # Next frame
            animation_frame = (animation_frame + 1) % len(pet_frames)

        sleep(0.15)  # 6-7 FPS

anim_thread = threading.Thread(target=animation_loop, daemon=True)
anim_thread.start()

# ============================================
# INPUT HANDLING
# ============================================

def on_button_pressed():
    """Whisplay button pressed"""
    pass

def on_button_released():
    """Whisplay button released - cycle through menu items"""

    # Update menu state
    if game_state["current_menu"] == "top":
        game_state["selected_index"] = (game_state["selected_index"] + 1) % 4
        if game_state["selected_index"] == 0:
            game_state["current_menu"] = "bottom"
    else:
        game_state["selected_index"] = (game_state["selected_index"] + 1) % 4
        if game_state["selected_index"] == 0:
            game_state["current_menu"] = "top"

    # Rebuild overlay (fast!)
    create_overlay()

    menu_name = MENUS[game_state["current_menu"]][game_state["selected_index"]]
    print(f"Now on: {menu_name}")

# Register Whisplay button callbacks
board.on_button_press(on_button_pressed)
board.on_button_release(on_button_released)

# ============================================
# MAIN GAME LOOP
# ============================================

print("\n=== PiPet Game Started ===")
print("Press the Whisplay button to navigate!")

try:
    while game_state["running"]:
        sleep(0.1)

except KeyboardInterrupt:
    print("\nInterrupted!")

# Cleanup
print("\nShutting down...")
stop_animation = True
sleep(0.2)
board.cleanup()
print("Goodbye!")