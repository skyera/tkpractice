import tkinter as tk
from tkinter import scrolledtext


def on_item_double_click(event):
    # Get selected item
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        item = listbox.get(index)

        # Update right pane with item details
        text_area.delete("1.0", tk.END)
        text_area.insert(
            tk.END, f"You selected: {item}\n\nDetails about {item} go here..."
        )


root = tk.Tk()
root.title("Listbox & ScrolledText Example")
root.geometry("600x400")

# Create panes
left_frame = tk.Frame(root, width=200)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Listbox on left
listbox = tk.Listbox(left_frame, font=("Arial", 12))
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Sample items
items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
for item in items:
    listbox.insert(tk.END, item)

# Bind double click
listbox.bind("<Double-Button-1>", on_item_double_click)

# ScrolledText on right
text_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Arial", 12))
text_area.pack(fill=tk.BOTH, expand=True)

root.mainloop()
