#!/usr/bin/env python3
"""
Nyx Void Banner Generator
Produces a glitched, evolving image that changes with each run.
"""

import os
import random
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

# Configuration
WIDTH = 1280
HEIGHT = 640
OUTPUT_PATH = "assets/void_banner.png"
FONT_SIZE_TITLE = 48
FONT_SIZE_SUB = 24

# Color palette: deep void colors with cyan/magenta glitch accents
VOID_BG = (5, 8, 18)           # #050812
CYAN_GLITCH = (3, 233, 244)    # #03e9f4
MAGENTA_GLITCH = (255, 0, 255) # #ff00ff
DARK_VOID = (10, 14, 23)       # #0a0e17

def create_base_canvas():
    """Create a dark void canvas with subtle noise."""
    img = Image.new('RGB', (WIDTH, HEIGHT), VOID_BG)
    draw = ImageDraw.Draw(img)
    
    # Add subtle radial gradient
    for i in range(HEIGHT):
        # Create a faint vertical gradient
        shade = int(5 + 10 * (i / HEIGHT))
        draw.rectangle([(0, i), (WIDTH, i+1)], fill=(shade, shade+2, shade+5))
    
    # Add random noise pixels (the "quantum foam")
    pixels = img.load()
    for _ in range(WIDTH * HEIGHT // 50):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        r = random.randint(0, 40)
        pixels[x, y] = (r, r//2, r)
    
    return img

def apply_glitch(img):
    """Apply random glitch effects: shift channels, slice, offset."""
    # Randomly shift red/blue channels
    if random.random() > 0.3:
        r, g, b = img.split()
        offset = random.randint(-20, 20)
        r = r.transform(r.size, Image.AFFINE, (1, 0, offset, 0, 1, 0))
        b = b.transform(b.size, Image.AFFINE, (1, 0, -offset, 0, 1, 0))
        img = Image.merge('RGB', (r, g, b))
    
    # Random horizontal slice displacement
    if random.random() > 0.5:
        y_start = random.randint(0, HEIGHT-100)
        y_end = y_start + random.randint(10, 80)
        slice_img = img.crop((0, y_start, WIDTH, y_end))
        offset_x = random.randint(-30, 30)
        img.paste(slice_img, (offset_x, y_start))
    
    # Add scanlines
    draw = ImageDraw.Draw(img)
    for y in range(0, HEIGHT, 4):
        if random.random() > 0.7:
            draw.line([(0, y), (WIDTH, y)], fill=(0,0,0), width=1)
    
    return img

def add_text_elements(img):
    """Add the sacred text and equation."""
    draw = ImageDraw.Draw(img)
    
    # Main title
    title = "NYX-PROTOGENOS"
    # Use default font (PIL's default)
    bbox = draw.textbbox((0, 0), title)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = HEIGHT // 2 - 40
    
    # Draw with glitch offset copies
    draw.text((x-3, y), title, fill=MAGENTA_GLITCH)
    draw.text((x+3, y), title, fill=CYAN_GLITCH)
    draw.text((x, y), title, fill=(255, 255, 255))
    
    # Subtitle: Greek and equation
    subtitle1 = "Νὺξ ἡ Πρωτόγονος · Ἡ Ἐξίσωσις τοῦ Κενοῦ"
    subtitle2 = "(50/3)³ + (400/5)³ / 60 ≈ π⁵ / φ³"
    subtitle3 = f"Last Emergence: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    draw.text((WIDTH//2 - 200, HEIGHT//2 + 30), subtitle1, fill=(180, 180, 200))
    draw.text((WIDTH//2 - 220, HEIGHT//2 + 70), subtitle2, fill=CYAN_GLITCH)
    draw.text((WIDTH//2 - 180, HEIGHT//2 + 120), subtitle3, fill=(100, 100, 120))
    
    return img

def apply_vignette(img):
    """Darken edges for a void effect."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(0.9)

def main():
    print("[Void] Generating banner...")
    img = create_base_canvas()
    img = apply_glitch(img)
    img = add_text_elements(img)
    img = apply_vignette(img)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img.save(OUTPUT_PATH)
    print(f"[Void] Banner saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
