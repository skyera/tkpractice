import colorsys
import hashlib
import math
import random
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw


# ---------------------------
# Image generators
# ---------------------------

def draw_stars(draw, w, h, count=100):
    """Draw a simple starfield background."""
    for _ in range(count):
        x, y = random.randint(0, w), random.randint(0, h)
        size = random.randint(1, 2)
        draw.ellipse([x, y, x + size, y + size], fill="white")

def make_colorful_image(seed_text: str, w=420, h=420):
    """Fallback procedural generator."""
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16) & ((1 << 32) - 1)
    rng = random.Random(seed)
    hue_offset = rng.random()
    swirl = 0.9 + rng.random() * 1.6
    ring_freq = 6 + rng.randrange(12)
    value_drop = 0.12 + rng.random() * 0.25

    img = Image.new("RGB", (w, h))
    px = img.load()
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = min(w, h) / 2.0

    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            r = math.hypot(dx, dy) / radius
            a = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            hue = (a * swirl + hue_offset) % 1.0
            ring = 0.5 + 0.5 * math.sin(r * ring_freq * 2 * math.pi)
            sat = 0.8 + 0.2 * ring
            val = 1.0 - value_drop * (r**1.2) * (0.6 + 0.4 * ring)
            val = max(0.0, min(1.0, val))
            r_, g_, b_ = colorsys.hsv_to_rgb(hue, sat, val)
            px[x, y] = (int(r_ * 255), int(g_ * 255), int(b_ * 255))
    return img

def make_themed_image(text: str, category: str, w=600, h=600):
    """Create a drawing that visually represents the item name."""
    img = Image.new("RGB", (w, h), (20, 20, 25))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    r_base = min(w, h) // 3

    # Use text to seed local randomness for consistent details
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) & ((1 << 32) - 1)
    rng = random.Random(seed)

    if category == "Planets":
        draw_stars(draw, w, h, count=150)
        p_colors = {
            "Mercury": "#A5A5A5", "Venus": "#E3BB76", "Earth": "#2271B3",
            "Mars": "#E27B58", "Jupiter": "#D39C7E", "Saturn": "#EAD6B8",
            "Uranus": "#D1E7E7", "Neptune": "#5B5DFF",
        }
        base_color = p_colors.get(text, "#FFFFFF")
        
        # Draw Planet Body
        draw.ellipse([cx - r_base, cy - r_base, cx + r_base, cy + r_base], fill=base_color)

        if text == "Earth":
            # Draw a stylized USA map on the blue planet
            s = r_base / 150.0
            usa_pts = [
                (cx - 120 * s, cy - 60 * s),  # NW (Washington)
                (cx + 20 * s, cy - 65 * s),   # N (Great Lakes area)
                (cx + 120 * s, cy - 75 * s),  # NE (Maine)
                (cx + 105 * s, cy + 10 * s),  # East Coast
                (cx + 95 * s, cy + 80 * s),   # Florida
                (cx + 60 * s, cy + 40 * s),   # Gulf
                (cx + 20 * s, cy + 90 * s),   # Texas
                (cx - 40 * s, cy + 50 * s),   # SW South
                (cx - 135 * s, cy + 40 * s),  # SW (California)
                (cx - 125 * s, cy - 10 * s),  # West Coast
            ]
            draw.polygon(usa_pts, fill="#228B22", outline="#1a6b1a")
            
            # Add a few small islands nearby (Caribbean/Hawaii style)
            draw.ellipse([cx + 110 * s, cy + 90 * s, cx + 115 * s, cy + 95 * s], fill="#228B22")
            draw.ellipse([cx - 160 * s, cy + 60 * s, cx - 155 * s, cy + 65 * s], fill="#228B22")

            # White cloud wisps
            for _ in range(5):
                wx = cx + rng.randint(-r_base, r_base)
                wy = cy + rng.randint(-r_base, r_base)
                if math.hypot(wx - cx, wy - cy) < r_base:
                    draw.ellipse([wx - 40, wy - 10, wx + 40, wy + 10], fill=(255, 255, 255, 120))
        
        elif text == "Saturn":
            # Rings
            draw.ellipse([cx - r_base * 1.8, cy - r_base * 0.4, cx + r_base * 1.8, cy + r_base * 0.4], outline="#C5AB6E", width=12)
            # Redraw planet half to simulate ring behind
            draw.chord([cx - r_base, cy - r_base, cx + r_base, cy + r_base], 180, 360, fill=base_color)

        elif text == "Jupiter":
            # Atmospheric bands
            for i in range(-r_base, r_base, 25):
                if rng.random() > 0.3:
                    draw.chord([cx - r_base, cy - r_base, cx + r_base, cy + r_base], 0, 180, fill="#A57E3E")

    elif category == "Animals":
        img = Image.new("RGB", (w, h), (34, 139, 34)) # Grass background
        draw = ImageDraw.Draw(img)
        
        if text == "Panda":
            # Body
            draw.ellipse([cx - 100, cy, cx + 100, cy + 150], fill="white", outline="black")
            # Head
            draw.ellipse([cx - 70, cy - 110, cx + 70, cy + 20], fill="white", outline="black")
            # Ears
            draw.ellipse([cx - 80, cy - 120, cx - 30, cy - 70], fill="black")
            draw.ellipse([cx + 30, cy - 120, cx + 80, cy - 70], fill="black")
            # Eye patches
            draw.ellipse([cx - 45, cy - 60, cx - 15, cy - 30], fill="black")
            draw.ellipse([cx + 15, cy - 60, cx + 45, cy - 30], fill="black")
            # Nose
            draw.ellipse([cx - 10, cy - 20, cx + 10, cy - 5], fill="black")

        elif text == "Tiger":
            # Body
            draw.ellipse([cx - 120, cy - 40, cx + 120, cy + 100], fill="#FF8C00")
            # Head
            draw.ellipse([cx - 70, cy - 110, cx + 70, cy - 10], fill="#FF8C00")
            # Stripes
            for i in range(-100, 100, 20):
                draw.line([cx + i, cy - 80, cx + i, cy - 40], fill="black", width=4)
            # Eyes
            draw.ellipse([cx - 30, cy - 70, cx - 15, cy - 55], fill="yellow")
            draw.ellipse([cx + 15, cy - 70, cx + 30, cy - 55], fill="yellow")

        else:
            # Generic animal shape
            draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill="#8B4513")
            draw.text((cx - 20, cy - 10), text, fill="white")

    elif category == "Shapes":
        color = "#FFD700"
        if text == "Circle":
            draw.ellipse([cx - r_base, cy - r_base, cx + r_base, cy + r_base], fill=color)
        elif text == "Square":
            draw.rectangle([cx - r_base, cy - r_base, cx + r_base, cy + r_base], fill=color)
        elif text == "Triangle":
            draw.polygon([(cx, cy - r_base), (cx - r_base, cy + r_base), (cx + r_base, cy + r_base)], fill=color)
        elif text == "Pentagon":
            pts = [(cx + r_base * math.cos(math.radians(i * 72 - 90)), 
                    cy + r_base * math.sin(math.radians(i * 72 - 90))) for i in range(5)]
            draw.polygon(pts, fill=color)
        elif text == "Hexagon":
            pts = [(cx + r_base * math.cos(math.radians(i * 60 - 90)), 
                    cy + r_base * math.sin(math.radians(i * 60 - 90))) for i in range(6)]
            draw.polygon(pts, fill=color)

    elif category == "Colors":
        color_map = {
            "Crimson": (220, 20, 60), "Azure": (0, 127, 255), "Amber": (255, 191, 0),
            "Indigo": (75, 0, 130), "Lime": (0, 255, 0), "Fuchsia": (255, 0, 255)
        }
        rgb = color_map.get(text, (255, 255, 255))
        draw.rectangle([0, 0, w, h], fill=rgb)
        # Texture
        for _ in range(100):
            rx, ry = rng.randint(0, w), rng.randint(0, h)
            rs = rng.randint(10, 40)
            draw.ellipse([rx, ry, rx + rs, ry + rs], fill=tuple(min(255, v + 20) for v in rgb))

    return img


# ---------------------------
# GUI
# ---------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tree → Themed Drawings")
        self.geometry("1000x700")

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        self.tree = ttk.Treeview(left, show="tree")
        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        self.image_label = ttk.Label(right, anchor="center")
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        self._photo = None
        self._populate_tree()

        self.tree.bind("<Double-1>", self.on_open_item)
        self.tree.bind("<Return>", self.on_open_item)

    def _populate_tree(self):
        cats = {
            "Planets": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
            "Shapes": ["Circle", "Triangle", "Square", "Pentagon", "Hexagon"],
            "Animals": ["Panda", "Dolphin", "Alpaca", "Eagle", "Tiger", "Koala"],
            "Colors": ["Crimson", "Azure", "Amber", "Indigo", "Lime", "Fuchsia"],
        }
        for cat, items in cats.items():
            node = self.tree.insert("", "end", text=cat, open=True)
            for it in items:
                self.tree.insert(node, "end", text=it)

    def on_open_item(self, event=None):
        item_id = self.tree.focus()
        if not item_id:
            return
        
        text = self.tree.item(item_id, "text")
        parent_id = self.tree.parent(item_id)
        
        if not parent_id:
            # It's a category
            pil_img = make_colorful_image(text, w=600, h=600)
        else:
            category = self.tree.item(parent_id, "text")
            pil_img = make_themed_image(text, category, w=600, h=600)

        # Scale to fit
        lw = max(self.image_label.winfo_width(), 300)
        lh = max(self.image_label.winfo_height(), 300)
        scale = min(lw / pil_img.width, lh / pil_img.height)
        new_size = (max(1, int(pil_img.width * scale)), max(1, int(pil_img.height * scale)))
        pil_img = pil_img.resize(new_size, Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(pil_img)
        self.image_label.configure(image=self._photo)


if __name__ == "__main__":
    App().mainloop()
