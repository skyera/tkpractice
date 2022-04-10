import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    colors = ('', 'gray90', 'red4', 'DarkGreen',
                  'NavyBlue', 'gray75', 'Red', 'Green', 
                  'Blue', 'gray50', 'Yellow', 'Cyan',
                  'Magenta', 'White', 'Brown', 'DarkSeaGreen')
    def __init__(self):
        super().__init__()
        self.make_widgets()

    def make_widgets(self):
        self.make_color_menu()
        self.make_color_images()
    
    def make_color_menu(self):
        self.color_var = tk.StringVar()
        self.color_menu = tk.OptionMenu(self, self.color_var,
                *self.colors, #direction='flush',
                command=self.change_color)
        self.color_var.set('gray90')
        self.color_menu.pack(padx=25, pady=25)

    def make_color_images(self):
        self._imgs = []
        for i in range(len(self.colors)):
            self._make_color_image(i)
    
    def _make_color_image(self, i):
        c = self.color_menu['menu'].entryconfig(i, 'label')[-1]
        img = tk.PhotoImage(name='image_'.join(c), width=16, height=16)
        img.put(c, to=(1,1,15,15))
        self._imgs.append(img)
        self.color_menu['menu'].entryconfigure(i, image=img, hidemargin=True)

        if not i%4:
            self.color_menu['menu'].entryconfigure(i, columnbreak=True)

    def change_color(self, choice):
        print(choice)
        self.color_menu.config(background=choice)


if __name__ == '__main__':
    app = App()
    app.mainloop()
