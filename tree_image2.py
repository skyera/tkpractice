import random
import tkinter as tk
from tkinter import PanedWindow, ttk

from PIL import Image, ImageDraw, ImageTk


def create_dynamic_image(width=200, height=200):
    """Create a colorful dynamic image using random rectangles."""
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    for _ in range(20):
        x1, y1 = random.randint(0, width - 50), random.randint(0, height - 50)
        x2, y2 = x1 + random.randint(20, 80), y1 + random.randint(20, 80)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([x1, y1, x2, y2], fill=color, outline="black")
    return image


def on_tree_double_click(event):
    selected_item = tree.focus()
    if selected_item:
        img = create_dynamic_image()
        tk_img = ImageTk.PhotoImage(img)
        image_label.config(image=tk_img, text="")  # clear text
        image_label.image = tk_img  # keep reference
        info_label.config(text=f"Image size: {img.width} x {img.height}")


root = tk.Tk()
root.title("Resizable Panes with Tree and Image Viewer")
root.geometry("800x500")

# Create PanedWindow (horizontal split)
paned = PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill=tk.BOTH, expand=True)

# Left pane with Treeview
left_frame = tk.Frame(paned)
tree = ttk.Treeview(left_frame)
tree.pack(fill=tk.BOTH, expand=True)

# Add some tree items
for i in range(1, 6):
    parent = tree.insert("", "end", text=f"Category {i}")
    for j in range(1, 4):
        tree.insert(parent, "end", text=f"Item {i}.{j}")

tree.bind("<Double-1>", on_tree_double_click)

# Right pane with Image label + info label
right_frame = tk.Frame(paned)

image_label = tk.Label(
    right_frame, text="Double-click a tree item to show image", compound="center"
)
image_label.pack(fill=tk.BOTH, expand=True)

info_label = tk.Label(right_frame, text="Image size: N/A", anchor="center")
info_label.pack(fill=tk.X)

# Add frames to paned window
paned.add(left_frame, minsize=200)  # Minimum width for tree
paned.add(right_frame, minsize=300)  # Minimum width for image display

root.mainloop()
