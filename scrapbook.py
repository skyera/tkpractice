import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Scrapbook")
        self.geometry("450x650")
        self.resizable(False, False)
        
        self.info_displayed = False
        self.image_fnames = []
        self.current_image = None
        self.tk_image = None
        
        self.prepare_assets()
        self.make_widgets()
        
        # Load first image if available
        if self.image_fnames:
            self.display_image(0)
        else:
            self.show_empty_placeholder()

    def prepare_assets(self):
        """Defensively check for images folder and filter valid image files"""
        if not os.path.exists('images'):
            os.makedirs('images')
            
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        self.image_fnames = [
            f for f in os.listdir('images')
            if f.lower().endswith(valid_extensions)
        ]

    def make_widgets(self):
        # Main container frame
        self.frame = tk.Frame(self, bg='gray50', relief=tk.RAISED, bd=4)
        self.frame.pack(expand=True, fill=tk.BOTH)
        
        # Image Display Label
        self.image_label = tk.Label(self.frame, bg='gray40')
        self.image_label.place(relx=0.5, rely=0.45, width=400, height=400, anchor=tk.CENTER)
        
        # Bottom Navigation Button Frame
        self.nav_frame = tk.Frame(self.frame, bg='gray50')
        self.nav_frame.place(relx=0.5, rely=0.88, relwidth=0.9, anchor=tk.CENTER)
        
        self.make_image_buttons()
        self.make_done_button()
        self.make_info_button()

    def make_image_buttons(self):
        """Creates image selector buttons side-by-side in a scrollable or packed frame"""
        # A container sub-frame for pagination buttons
        self.btn_subframe = tk.Frame(self.nav_frame, bg='gray50')
        self.btn_subframe.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        for i in range(len(self.image_fnames)):
            btn = tk.Button(
                self.btn_subframe,
                text=f"{i + 1}",
                bg='gray10',
                fg='white',
                activebackground='gray30',
                activeforeground='white',
                width=3,
                command=lambda idx=i: self.display_image(idx)
            )
            btn.pack(side=tk.LEFT, padx=2)

    def make_done_button(self):
        done_btn = tk.Button(
            self.frame,
            text='Done',
            command=self.destroy,
            bg='red',
            fg='yellow',
            activebackground='darkred',
            activeforeground='yellow',
            font=('Arial', 10, 'bold')
        )
        done_btn.place(relx=0.97, rely=0.97, anchor=tk.SE)

    def make_info_button(self):
        """Creates the info toggle button"""
        self.btn_info = tk.Button(
            self.frame,
            text="Info",
            command=self.toggle_image_info,
            bg='blue',
            fg='yellow',
            activebackground='navy',
            activeforeground='yellow',
            font=('Arial', 10, 'bold')
        )
        self.btn_info.place(relx=0.97, rely=0.80, anchor=tk.SE)

    def show_empty_placeholder(self):
        """Displays a clean placeholder if no images are present"""
        self.image_label.config(
            text="No images found in 'images/' folder.\n\nPlease copy image files here to start!",
            fg="white",
            font=("Arial", 11, "bold"),
            compound='center'
        )

    def display_image(self, index):
        """Loads and scales the selected image"""
        try:
            image_path = os.path.join('images', self.image_fnames[index])
            self.image = Image.open(image_path)
            
            # Keep copy for property details
            self.current_image = self.image.copy()
            
            self.image.thumbnail((400, 400))
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.image_label.config(image=self.tk_image, text="")
            
            # Refresh info panel only if toggled open
            if self.info_displayed:
                self.show_image_info()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def toggle_image_info(self):
        """Safely toggles the visibility state of the image properties panel"""
        self.info_displayed = not self.info_displayed
        if self.info_displayed:
            if self.image_fnames:
                self.show_image_info()
                self.btn_info.config(relief=tk.SUNKEN, bg='navy')
        else:
            self.btn_info.config(relief=tk.RAISED, bg='blue')
            if hasattr(self, 'info_frame'):
                self.info_frame.destroy()

    def show_image_info(self):
        """Re-draws the info panel"""
        if hasattr(self, 'info_frame'):
            self.info_frame.destroy()

        if not self.current_image:
            return

        self.make_image_info_frame()
        self.make_image_info_labels()

    def make_image_info_frame(self):
        # Anchor the info frame precisely within the image display frame
        self.info_frame = tk.Frame(self.frame, bg='gray10', bd=1, relief=tk.SOLID)
        self.info_frame.place(
            in_=self.image_label,
            relx=0.5,
            relwidth=1.0,
            height=60,
            anchor=tk.S,
            rely=1.0,
            y=0,
            bordermode='outside'
        )

    def make_image_info_labels(self):
        """Creates vertical list of details using tk.pack instead of manual relative place coordinates"""
        for attr_name in ['Format', 'Size', 'Mode']:
            attr_val = getattr(self.current_image, attr_name.lower())
            label_text = f"{attr_name}: {attr_val}"
            
            attr_label = tk.Label(
                self.info_frame,
                text=label_text,
                bg='gray10',
                fg='white',
                font=('Verdana', 8)
            )
            attr_label.pack(anchor=tk.W, padx=15, pady=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()
