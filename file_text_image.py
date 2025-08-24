import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from PIL import Image, ImageTk


class FileBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Browser with Preview")

        # Toolbar
        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        open_btn = tk.Button(
            toolbar, text="Open Directory", command=self.open_directory
        )
        open_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Paned window for resizable panes
        paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left pane (tree with scrollbar)
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)

        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(
            left_frame, orient="vertical", command=self.tree.yview
        )
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Right pane (content)
        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame, weight=3)

        self.text_area = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(self.right_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Bind double click
        self.tree.bind("<Double-1>", self.on_double_click)

        # Supported file types
        self.text_ext = {".txt", ".py", ".md", ".log", ".csv"}
        self.image_ext = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}

    def open_directory(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        # Clear old tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Populate tree once
        self.insert_files("", directory)

    def insert_files(self, parent, path):
        for entry in os.scandir(path):
            if entry.is_dir():
                node = self.tree.insert(
                    parent, "end", text=entry.name, open=False, values=[entry.path]
                )
                self.insert_files(node, entry.path)
            else:
                ext = os.path.splitext(entry.name)[1].lower()
                if ext in self.text_ext or ext in self.image_ext:
                    self.tree.insert(
                        parent, "end", text=entry.name, values=[entry.path]
                    )

    def on_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        filepath = self.tree.item(item_id, "values")[0]
        if not os.path.isfile(filepath):
            return

        ext = os.path.splitext(filepath)[1].lower()
        self.text_area.pack_forget()
        self.image_label.pack_forget()

        if ext in self.text_ext:
            size = os.path.getsize(filepath)
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, f"File: {filepath}\nSize: {size} bytes\n\n")
            self.text_area.insert(tk.END, content)
            self.text_area.pack(fill=tk.BOTH, expand=True)
        elif ext in self.image_ext:
            try:
                img = Image.open(filepath)
                w, h = img.size
                fmt = img.format
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(
                    tk.END, f"Image: {filepath}\nFormat: {fmt}\nSize: {w}x{h}\n"
                )
                self.text_area.pack(fill=tk.X)

                img.thumbnail((400, 400))  # resize preview
                self.tk_img = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.tk_img)
                self.image_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, f"Error loading image: {e}")
                self.text_area.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileBrowserApp(root)
    root.mainloop()
