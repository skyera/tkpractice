import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk


def collect_dirs_with_files(root_dir):
    result = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Collect only .txt or image files
        files = [
            f
            for f in filenames
            if f.lower().endswith((".txt", ".png", ".jpg", ".jpeg", ".gif"))
        ]

        # Check if current dir has valid files or child dirs with files
        if files or any(os.path.join(dirpath, d) in result for d in dirnames):
            result[dirpath] = files
    return result


class FileBrowserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Browser with Viewer")
        self.geometry("900x600")

        # Paned window (Tree on left, viewer on right)
        self.paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left frame (Tree)
        self.tree_frame = ttk.Frame(self.paned)
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(
            self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.paned.add(self.tree_frame, weight=1)

        # Right frame (viewer)
        self.viewer_frame = ttk.Frame(self.paned)
        self.paned.add(self.viewer_frame, weight=3)

        # Toolbar button to select directory
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill=tk.X)
        self.select_btn = ttk.Button(
            self.toolbar, text="Select Directory", command=self.load_directory
        )
        self.select_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Bind tree events
        self.tree.bind("<Double-1>", self.on_item_double_click)

        self.file_data = {}
        self.image_cache = None  # Keep reference to avoid garbage collection

    def load_directory(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.tree.delete(*self.tree.get_children())
        self.file_data = collect_dirs_with_files(folder)

        # Build tree
        self.insert_nodes("", folder)

    def insert_nodes(self, parent, path):
        node = self.tree.insert(
            parent,
            "end",
            text=os.path.basename(path) or path,
            open=False,
            values=[path],
        )

        # Add children dirs
        for subdir in sorted([d for d in self.file_data if os.path.dirname(d) == path]):
            self.insert_nodes(node, subdir)

        # Add files
        for f in self.file_data.get(path, []):
            self.tree.insert(node, "end", text=f, values=[os.path.join(path, f)])

    def on_item_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        path = self.tree.item(selected[0], "values")[0]
        if os.path.isdir(path):
            return

        # Clear previous viewer content
        for widget in self.viewer_frame.winfo_children():
            widget.destroy()

        # Show text file
        if path.lower().endswith(".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            text_box = ScrolledText(self.viewer_frame, wrap=tk.WORD)
            text_box.insert(tk.END, text)
            text_box.config(state=tk.DISABLED)
            text_box.pack(fill=tk.BOTH, expand=True)

        # Show image file
        elif path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            img = Image.open(path)
            img.thumbnail((600, 600))  # Resize to fit
            self.image_cache = ImageTk.PhotoImage(img)

            lbl = ttk.Label(self.viewer_frame, image=self.image_cache)
            lbl.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = FileBrowserApp()
    app.mainloop()
