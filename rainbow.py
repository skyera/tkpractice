import colorsys
import math
import tkinter as tk
from tkinter import scrolledtext

from PIL import Image, ImageTk

# ----------------------
# 1. Create a 64x64 rainbow image
# ----------------------
w, h = 64, 64
cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

img = Image.new("RGB", (w, h), "black")
px = img.load()

for y in range(h):
    for x in range(w):
        hue = (math.atan2(y - cy, x - cx) + math.pi) / (2 * math.pi)
        d = min(math.hypot(x - cx, y - cy) / (min(w, h) / 2), 1.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0 - 0.2 * d)
        px[x, y] = (int(r * 255), int(g * 255), int(b * 255))

# ----------------------
# 2. Create Tkinter window with ScrolledText
# ----------------------
root = tk.Tk()
root.title("ScrolledText with Images")
st = scrolledtext.ScrolledText(root, width=40, height=15)
st.pack(padx=10, pady=10, fill="both", expand=True)

# Convert PIL image to PhotoImage for Tkinter
photo = ImageTk.PhotoImage(img)

# Keep references to images to prevent garbage collection
images = []

# ----------------------
# 3. Insert the image 3 times
# ----------------------
for i in range(3):
    st.insert(tk.END, f"Image {i+1}:\n")
    st.image_create(tk.END, image=photo)
    st.insert(tk.END, "\n\n")
    images.append(photo)

root.mainloop()
