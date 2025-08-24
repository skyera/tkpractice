import colorsys
import hashlib
import math
import random
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


# ---------------------------
# Image generator (colorful)
# ---------------------------
def make_colorful_image(seed_text: str, w=420, h=420):
    """
    Create a colorful image deterministically from seed_text.
    Uses HSV rainbows + radial/spiral modulation.
    """
    # Use a stable seed derived from the item text
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16) & (
        (1 << 32) - 1
    )
    rng = random.Random(seed)
    hue_offset = rng.random()
    swirl = 0.9 + rng.random() * 1.6
    ring_freq = 6 + rng.randrange(12)  # 6..17
    value_drop = 0.12 + rng.random() * 0.25

    img = Image.new("RGB", (w, h))
    px = img.load()
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = min(w, h) / 2.0

    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            r = math.hypot(dx, dy) / radius  # 0 at center -> ~1 at edge
            a = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)  # 0..1
            # Spiral hue with offset (rainbow)
            hue = (a * swirl + hue_offset) % 1.0
            # Radial rings for texture
            ring = 0.5 + 0.5 * math.sin(r * ring_freq * 2 * math.pi)
            sat = 0.8 + 0.2 * ring
            val = 1.0 - value_drop * (r**1.2) * (0.6 + 0.4 * ring)
            val = max(0.0, min(1.0, val))
            r_, g_, b_ = colorsys.hsv_to_rgb(hue, sat, val)
            px[x, y] = (int(r_ * 255), int(g_ * 255), int(b_ * 255))
    return img


# ---------------------------
# GUI
# ---------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tree → Dynamic Colorful Image")
        self.geometry("900x560")

        # Paned layout
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left: Tree + scrollbar
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        self.tree = ttk.Treeview(left, show="tree")
        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Right: Image display
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        self.image_label = ttk.Label(right, anchor="center")
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Keep a reference to PhotoImage to avoid GC
        self._photo = None

        # Populate tree
        self._populate_tree()

        # Bind double-click
        self.tree.bind("<Double-1>", self.on_open_item)
        # Also allow Enter key to trigger
        self.tree.bind("<Return>", self.on_open_item)

    def _populate_tree(self):
        cats = {
            "Planets": [
                "Mercury",
                "Venus",
                "Earth",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
            ],
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
        # If a parent category was double-clicked, just show its name too
        if not text:
            return

        # Generate colorful image from the text seed
        pil_img = make_colorful_image(text, w=600, h=600)

        # Fit to current right pane size (keep aspect)
        # Get label size (fallback if not realized yet)
        lw = max(self.image_label.winfo_width(), 300)
        lh = max(self.image_label.winfo_height(), 300)
        scale = min(lw / pil_img.width, lh / pil_img.height)
        new_size = (
            max(1, int(pil_img.width * scale)),
            max(1, int(pil_img.height * scale)),
        )
        pil_img = pil_img.resize(new_size, Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(pil_img)
        self.image_label.configure(image=self._photo, text="")


if __name__ == "__main__":
    App().mainloop()
