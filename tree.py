import tkinter as tk
from tkinter import ttk, scrolledtext

root = tk.Tk()
root.title("Treeview with Text Pane")

# Create a horizontal PanedWindow
paned = ttk.Panedwindow(root, orient="horizontal")
paned.pack(fill="both", expand=True)

# Left pane: Treeview
tree_frame = ttk.Frame(paned)
tree = ttk.Treeview(tree_frame, columns=("size", "type"), show="tree headings")
tree.heading("#0", text="Name")
tree.heading("size", text="Size")
tree.heading("type", text="Type")
tree.column("#0", width=200)
tree.column("size", width=80, anchor="e")
tree.column("type", width=100)

# Add sample items
folder = tree.insert("", "end", text="Projects", values=("", "Folder"))
tree.insert(folder, "end", text="app.py", values=("4 KB", "Python"))
tree.insert(folder, "end", text="README.md", values=("1 KB", "Markdown"))

docs = tree.insert("", "end", text="Documents", values=("", "Folder"))
tree.insert(docs, "end", text="Notes.txt", values=("2 KB", "Text"))

# Scrollbar for tree
vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
tree_frame.rowconfigure(0, weight=1)
tree_frame.columnconfigure(0, weight=1)

paned.add(tree_frame, weight=1)

# Right pane: Text widget
text_frame = ttk.Frame(paned)
text_widget = scrolledtext.ScrolledText(text_frame, wrap="word")
text_widget.pack(fill="both", expand=True)
paned.add(text_frame, weight=3)

# Double-click callback
def on_double_click(event):
    selected = tree.selection()
    if selected:
        item = tree.item(selected[0])
        # Update text control with item info
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"Name: {item['text']}\n")
        if "values" in item:
            text_widget.insert(tk.END, f"Values: {item['values']}\n")

tree.bind("<Double-1>", on_double_click)

root.mainloop()

