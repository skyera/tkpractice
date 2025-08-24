import mimetypes
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

# ---------- Helpers ----------
TEXT_EXTS = {
    ".txt",
    ".py",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".csv",
    ".tsv",
    ".log",
    ".xml",
    ".html",
    ".htm",
    ".css",
    ".js",
}

IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"}


def is_text_file(path: str) -> bool:
    ext = os.path.splitext(path.lower())[1]
    if ext in TEXT_EXTS:
        return True
    # Fallback to mimetype guess
    mt, _ = mimetypes.guess_type(path)
    return (mt or "").startswith("text")


def is_image_file(path: str) -> bool:
    ext = os.path.splitext(path.lower())[1]
    if ext in IMG_EXTS:
        return True
    mt, _ = mimetypes.guess_type(path)
    return (mt or "").startswith("image")


# ---------- Main App ----------
class FileViewerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Directory Tree & Viewer")
        self.geometry("1100x700")

        # Keep references
        self._photo = None
        self._pil_image = None
        self._current_file = None

        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x")
        choose_btn = ttk.Button(
            toolbar, text="Choose Directory…", command=self.choose_directory
        )
        choose_btn.pack(side="left", padx=6, pady=6)

        # Panes
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left: Tree
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        self.tree = ttk.Treeview(left, columns=("fullpath", "type"), displaycolumns=())
        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set, show="tree")
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Tree bindings
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Right: Viewer
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Right contains: image frame and text frame (we show/hide as needed)
        self.viewer = ttk.Frame(right)
        self.viewer.pack(fill="both", expand=True)

        # Image frame
        self.image_frame = ttk.Frame(self.viewer)
        self.image_label = ttk.Label(self.image_frame, anchor="center")
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        info = ttk.Frame(self.image_frame)
        info.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(info, text="Image format:").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        self.img_format_var = tk.StringVar(value="—")
        self.img_format_val = ttk.Entry(
            info, textvariable=self.img_format_var, width=20, state="readonly"
        )
        self.img_format_val.grid(row=0, column=1, sticky="w")

        ttk.Label(info, text="Image size (w×h):").grid(
            row=0, column=2, sticky="w", padx=(18, 6)
        )
        self.img_size_var = tk.StringVar(value="—")
        self.img_size_val = ttk.Entry(
            info, textvariable=self.img_size_var, width=20, state="readonly"
        )
        self.img_size_val.grid(row=0, column=3, sticky="w")

        # Text frame
        self.text_frame = ttk.Frame(self.viewer)
        self.text_box = ScrolledText(self.text_frame, wrap="word")
        self.text_box.pack(fill="both", expand=True, padx=10, pady=10)

        # Resize handling for image scaling
        self.image_frame.bind("<Configure>", self._maybe_rescale_image)

        # Start with placeholders
        self._show_placeholder()

    # ---------- Directory handling ----------
    def choose_directory(self):
        path = filedialog.askdirectory(title="Choose a directory")
        if not path:
            return
        self.populate_tree(path)

    def populate_tree(self, root_path: str):
        self.tree.delete(*self.tree.get_children())
        abspath = os.path.abspath(root_path)
        root_node = self.tree.insert(
            "", "end", text=abspath, values=(abspath, "dir"), open=True
        )
        self._insert_dummy(root_node)
        # Expand root immediately
        self.on_open_node_for_id(root_node)

    def _insert_dummy(self, node_id):
        # Add a dummy child so the expand arrow shows up
        if not self.tree.get_children(node_id):
            self.tree.insert(node_id, "end", text="(loading…)", values=("", "dummy"))

    def on_open_node(self, event):
        node_id = self.tree.focus()
        self.on_open_node_for_id(node_id)

    def on_open_node_for_id(self, node_id):
        path, typ = self.tree.item(node_id, "values") or ("", "")
        if typ != "dir" or not path:
            return
        # Clear old children
        for child in self.tree.get_children(node_id):
            self.tree.delete(child)

        # Insert real directory listing
        try:
            entries = sorted(os.listdir(path), key=str.lower)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot access:\n{path}\n\n{e}")
            return

        for name in entries:
            full = os.path.join(path, name)
            if os.path.isdir(full):
                nid = self.tree.insert(node_id, "end", text=name, values=(full, "dir"))
                self._insert_dummy(nid)
            else:
                self.tree.insert(node_id, "end", text=name, values=(full, "file"))

    # ---------- Interaction ----------
    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        path, typ = self.tree.item(item, "values") or ("", "")
        if not path:
            return

        if typ == "dir":
            # toggle open/close
            is_open = self.tree.item(item, "open")
            self.tree.item(item, open=not is_open)
            if not is_open:
                self.on_open_node_for_id(item)
            return

        # File: choose how to display
        self._current_file = path
        if is_image_file(path):
            self._show_image(path)
        elif is_text_file(path):
            self._show_text(path)
        else:
            # Try to decide by content: if image open fails, fallback to text with bytes preview
            try:
                self._show_image(path)
            except Exception:
                self._show_text(path)

    # ---------- Viewers ----------
    def _show_placeholder(self):
        for w in (self.image_frame, self.text_frame):
            w.pack_forget()
        placeholder = ttk.Label(
            self.viewer,
            text="Choose a directory, then double-click a file in the tree.",
            anchor="center",
        )
        placeholder.pack_forget()  # just to ensure no duplicates
        self._placeholder = placeholder
        self._placeholder.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear_placeholder(self):
        if hasattr(self, "_placeholder") and self._placeholder.winfo_exists():
            self._placeholder.pack_forget()

    def _show_text(self, path):
        self._clear_placeholder()
        self.image_frame.pack_forget()
        self.text_frame.pack(fill="both", expand=True)

        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
        except Exception as e:
            data = f"Unable to open file:\n{path}\n\n{e}"
        self.text_box.insert("1.0", data)
        self.text_box.config(state="disabled")

    def _show_image(self, path):
        self._clear_placeholder()
        self.text_frame.pack_forget()
        self.image_frame.pack(fill="both", expand=True)

        # Load image with PIL
        try:
            pil = Image.open(path)
            pil.load()
        except Exception as e:
            messagebox.showerror("Image error", f"Failed to open image:\n{path}\n\n{e}")
            return

        self._pil_image = pil  # keep original for rescaling
        self.img_format_var.set(pil.format or "Unknown")
        self.img_size_var.set(f"{pil.width} × {pil.height}")
        self._update_image_label()

    def _maybe_rescale_image(self, event=None):
        # Rescale image preview on frame resize
        if self._pil_image is None or not self.image_frame.winfo_ismapped():
            return
        self._update_image_label()

    def _update_image_label(self):
        if self._pil_image is None:
            return
        # Figure available area for image_label
        lw = max(self.image_label.winfo_width(), 50)
        lh = max(self.image_label.winfo_height(), 50)
        if lw < 10 or lh < 10:
            # widget not yet laid out—retry later
            self.after(50, self._update_image_label)
            return
        # Scale to fit while preserving aspect
        scale = min(lw / self._pil_image.width, lh / self._pil_image.height, 1.0)
        new_w = max(1, int(self._pil_image.width * scale))
        new_h = max(1, int(self._pil_image.height * scale))
        disp = (
            self._pil_image
            if (new_w, new_h) == self._pil_image.size
            else self._pil_image.resize((new_w, new_h), Image.LANCZOS)
        )
        self._photo = ImageTk.PhotoImage(disp)
        self.image_label.configure(image=self._photo)


# ---------- Run ----------
if __name__ == "__main__":
    # Better file type guesses on Windows
    if sys.platform.startswith("win"):
        mimetypes.init()

    app = FileViewerApp()
    app.mainloop()
