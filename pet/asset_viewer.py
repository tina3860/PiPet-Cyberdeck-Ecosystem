from time import sleep
from PIL import Image
import sys
import os
import threading

# Import Whisplay driver
sys.path.append("/home/tina386/Whisplay/Driver")
from WhisPlay import WhisPlayBoard

# Initialize board
board = WhisPlayBoard()
board.set_backlight(50)

def load_image_rgb565(filepath):
    """Convert PNG to RGB565 for Whisplay"""
    img = Image.open(filepath).convert('RGB')
    img = img.resize((board.LCD_WIDTH, board.LCD_HEIGHT))

    pixel_data = []
    for y in range(board.LCD_HEIGHT):
        for x in range(board.LCD_WIDTH):
            r, g, b = img.getpixel((x, y))
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])
    return pixel_data

def load_gif_frames_rgb565(filepath):
    """Convert GIF frames to RGB565"""
    gif = Image.open(filepath)
    frames = []

    for frame_num in range(gif.n_frames):
        gif.seek(frame_num)
        frame_img = gif.convert('RGB')
        frame_img = frame_img.resize((board.LCD_WIDTH, board.LCD_HEIGHT))

        pixel_data = []
        for y in range(board.LCD_HEIGHT):
            for x in range(board.LCD_WIDTH):
                r, g, b = frame_img.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixel_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])
        frames.append(pixel_data)

    return frames

# Asset list
assets = [
    ("Status Page", "ui/stats/Status_page.png", "image"),
    ("Top Menu Bar", "ui/stats/menu-bars/top-menu-bar.png", "image"),
    ("Bottom Menu Bar", "ui/stats/menu-bars/bottom-menu-bar.png", "image"),

    # Stat Icons
    ("Heart Icon (Attention)", "animations/heart-icon.png", "image"),
    ("Fish Icon (Hunger)", "animations/fish-icon.png", "image"),
    ("Yarn Icon (Boredom)", "animations/yarnball-icon.png", "image"),
    ("Lightning Icon (Energy)", "animations/lightning-icon.png", "image"),
    ("Bubble Icon (Clean)", "animations/bubble-icon.png", "image"),

    # Menu Icons
    ("Pill Icon (Medicine)", "animations/pill-icon.png", "image"),
    ("Stats Icon", "animations/stats-icon.png", "image"),
    ("Vacation Icon", "animations/vacation-icon.png", "image"),

    # Pet Animations
    ("Bored Animation", "animations/Bored.gif", "gif"),
    ("Celebrate Pet", "animations/cat_celebrate_pet.gif", "gif"),
    ("Sleep Animation", "animations/Cat_Sleep.gif", "gif"),
    ("Hide & Seek", "animations/hide&seek.gif", "gif"),
    ("Hungry Animation", "animations/Hungry.gif", "gif"),
    ("Low Energy", "animations/Low_energy.gif", "gif"),
    ("Need Attention", "animations/Need_attention.gif", "gif"),
    ("Need Bath", "animations/need_bath.gif", "gif"),
    ("Need Medicine", "animations/Need_medicine.gif", "gif"),
]

current_index = 0
loaded_assets = {}
animation_running = False
stop_animation = False

# Pre-load all assets
print("Loading assets...")
for name, path, asset_type in assets:
    full_path = f"assets/{path}"
    try:
        if asset_type == "image":
            loaded_assets[name] = (load_image_rgb565(full_path), "image")
            print(f"✓ {name}")
        elif asset_type == "gif":
            loaded_assets[name] = (load_gif_frames_rgb565(full_path), "gif")
            print(f"✓ {name}")
    except Exception as e:
        print(f"✗ {name}: {e}")

print(f"\n{len(loaded_assets)} assets loaded!")

# Animate GIF frames
def animate_gif(frames):
    global stop_animation
    frame_index = 0
    while not stop_animation:
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, frames[frame_index])
        frame_index = (frame_index + 1) % len(frames)
        sleep(0.1)  # ~10 FPS

# Display current asset
def show_current_asset():
    global current_index, animation_running, stop_animation

    # Stop any running animation
    if animation_running:
        stop_animation = True
        sleep(0.2)  # Wait for animation thread to stop
        animation_running = False
        stop_animation = False

    name, path, asset_type = assets[current_index]

    if name in loaded_assets:
        data, dtype = loaded_assets[name]
        print(f"\nShowing: {name} ({current_index + 1}/{len(assets)})")

        if dtype == "image":
            board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, data)
        elif dtype == "gif":
            # Start animation thread
            animation_running = True
            anim_thread = threading.Thread(target=animate_gif, args=(data,), daemon=True)
            anim_thread.start()

# Button callback
def on_button_pressed():
    global current_index
    current_index = (current_index + 1) % len(assets)
    show_current_asset()

board.on_button_press(on_button_pressed)

# Show first asset
show_current_asset()

try:
    print("\nPress button to cycle through assets (Ctrl+C to exit)...")
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting...")
    stop_animation = True
finally:
    board.cleanup()