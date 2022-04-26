import tkinter as tk


class ScrolledFrame(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.make_widgets()
        self.layout_widgets()
        self.fill_listbox()
        self.bind_events()

    def make_widgets(self):
        self.sbar = tk.Scrollbar(self)
        self.listbox = tk.Listbox(self, relief=tk.SUNKEN)
        self.sbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.sbar.set)

    def layout_widgets(self):
        self.sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    def fill_listbox(self):
        for index in range(20):
            self.listbox.insert(index, 'Jack %d' % index)

    def bind_events(self):
        self.listbox.bind('<Double-1>', self.handlelist)

    def handlelist(self, event):
        index = self.listbox.curselection()
        label = self.listbox.get(index)
        print('You selected', label)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.frame = ScrolledFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()

        

