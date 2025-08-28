import tkinter as tk
from tkinter import ttk


class FancyRadioApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fancy Tkinter Radio Buttons")
        self.geometry("500x300")
        self.configure(bg="#f0f0f5")

        # Variable to hold the selected option
        self.choice = tk.StringVar(value="Blue")

        # Left frame for radio buttons
        left_frame = ttk.LabelFrame(self, text="Choose a Theme", padding=10)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right frame for preview
        self.right_frame = tk.Frame(
            self, bg="white", width=300, height=250, relief="sunken", bd=2
        )
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.preview_label = tk.Label(
            self.right_frame, text="Preview", font=("Helvetica", 16), bg="white"
        )
        self.preview_label.pack(expand=True)

        # Define options with colors
        themes = {
            "Blue": "#4a90e2",
            "Green": "#4caf50",
            "Orange": "#ff9800",
            "Purple": "#9c27b0",
        }

        # Add radio buttons
        for text, color in themes.items():
            rb = ttk.Radiobutton(
                left_frame,
                text=text,
                value=text,
                variable=self.choice,
                command=lambda c=color, t=text: self.update_preview(c, t),
            )
            rb.pack(anchor="w", pady=5)

        # Initialize preview
        self.update_preview(themes["Blue"], "Blue")

    def update_preview(self, color, text):
        self.right_frame.config(bg=color)
        self.preview_label.config(bg=color, text=f"{text} Theme", fg="white")


if __name__ == "__main__":
    app = FancyRadioApp()
    app.mainloop()
