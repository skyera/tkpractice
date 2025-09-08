import tkinter as tk

root = tk.Tk()
root.title("Spinbox + Drag Box Example")

canvas_width = 300
canvas_height = 200

# Create Canvas
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack(pady=20)

# Initial position
x0 = 0
y0 = 50
box_width = 50
box_height = 50

# Draw rectangle
box = canvas.create_rectangle(x0, y0, x0 + box_width, y0 + box_height, fill="blue")


# Move box based on Spinbox
def move_box():
    x = int(spin.get())
    canvas.coords(box, x, y0, x + box_width, y0 + box_height)


# Validation: only digits
def validate(P):
    return P.isdigit() or P == ""


vcmd = (root.register(validate), "%P")

# Spinbox with initial value 0
spin_var = tk.StringVar(value=str(x0))
spin = tk.Spinbox(
    root,
    from_=0,
    to=canvas_width - box_width,
    width=5,
    command=move_box,
    validate="key",
    validatecommand=vcmd,
    textvariable=spin_var,
)
spin.pack()


# Update box when typing manually
def on_spin_change(*args):
    if spin_var.get().isdigit():
        move_box()


spin_var.trace_add("write", on_spin_change)

# --- Mouse Dragging ---
drag_data = {"x": 0}


def on_box_press(event):
    # Save the initial mouse position
    drag_data["x"] = event.x


def on_box_drag(event):
    dx = event.x - drag_data["x"]
    drag_data["x"] = event.x

    # Move rectangle horizontally
    coords = canvas.coords(box)
    new_x1 = max(0, min(canvas_width - box_width, coords[0] + dx))
    new_x2 = new_x1 + box_width
    canvas.coords(box, new_x1, y0, new_x2, y0 + box_height)

    # Update Spinbox
    spin_var.set(str(int(new_x1)))


# Bind mouse events
canvas.tag_bind(box, "<ButtonPress-1>", on_box_press)
canvas.tag_bind(box, "<B1-Motion>", on_box_drag)

root.mainloop()
