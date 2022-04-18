import tkinter as tk


DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday']
MODES = [tk.SINGLE, tk.BROWSE, tk.MULTIPLE, tk.EXTENDED]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.make_listbox()
        self.make_btn()
        self.layout_widgets()

    def make_listbox(self):
        self.listbox = tk.Listbox(self)
        self.listbox.insert(0, *DAYS)

    def make_btn(self):
        self.print_btn = tk.Button(self, text='Print',
                command=self.print_selection)
        self.btns = [self.create_btn(m) for m in MODES]

    def layout_widgets(self):
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.print_btn.pack(fill=tk.BOTH)
        for btn in self.btns:
            btn.pack(side=tk.LEFT)

    def create_btn(self, mode):
        cmd = lambda: self.listbox.config(selectmode=mode)
        return tk.Button(self, command=cmd, text=mode.capitalize())

    def print_selection(self):
        selection = self.listbox.curselection()
        print([self.listbox.get(i) for i in selection])


if __name__ == '__main__':
    app = App()
    app.mainloop()
