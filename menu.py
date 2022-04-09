import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.make_menu()

    def make_menu(self):
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.make_file_menu()
        self.menu.add_command(label='About', command=self.about)
        self.menu.add_command(label='Quit', command=self.destroy)

    def make_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label='New file')
        file_menu.add_command(label='Open')
        file_menu.add_separator()
        file_menu.add_command(label='Save')
        file_menu.add_command(label='Save as...')
        self.menu.add_cascade(label='File', menu=file_menu)

    def about(self):
        print('about')


if __name__ == '__main__':
    app = App()
    app.mainloop()
