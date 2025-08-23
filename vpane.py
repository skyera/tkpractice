import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import *


class VPaneFrame(ttk.Frame):
    def __init__(self, master, name="verticalicalpane"):
        super().__init__(master, name=name)
        self.make_widgets()

    def make_widgets(self):
        pw = ttk.PanedWindow(self, orient=tk.VERTICAL)
        pw.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH, padx="2m", pady=2)
        self.make_listbox_with_vscroll(pw)
        self.make_text(pw)
        pw.add(self.top_frame)
        pw.add(self.text)

    def make_listbox_with_vscroll(self, parent):
        self.top_frame = ttk.Frame(parent)
        self.make_var()
        self.make_listbox()
        self.make_vscrollbar()
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(fill=tk.BOTH, expand=tk.Y)

    def make_var(self):
        wnames = (
            "List of Tk Widgets",
            "button",
            "canvas",
            "checkbutton",
            "entry",
            "frame",
            "label",
            "labelframe",
            "listbox",
            "menu",
            "menubutton",
            "message",
            "panedwindow",
            "radiobutton",
            "scale",
            "scrollbar",
            "spinbox",
            "text",
            "toplevel",
        )
        self.panelist_var = tk.StringVar()
        self.panelist_var.set(wnames)

    def make_listbox(self):
        self.listbox = tk.Listbox(self.top_frame, listvariable=self.panelist_var)
        self.listbox.itemconfigure(
            0, background=self.listbox.cget("fg"), fg=self.listbox.cget("bg")
        )

    def make_vscrollbar(self):
        self.vscroll = ttk.Scrollbar(
            self.top_frame, orient=tk.VERTICAL, command=self.listbox.yview
        )
        self.listbox["yscrollcommand"] = self.vscroll.set

    def make_text(self, parent):
        self.text = ScrolledText(parent, height=8, width=30, wrap=None)
        self.text.insert(tk.END, "This is a test")
        self.text.pack(expand=tk.Y, fill=tk.BOTH)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        frame = VPaneFrame(self)
        frame.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
