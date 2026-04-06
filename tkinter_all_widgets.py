"""
Tkinter All Widgets Practice
A comprehensive demonstration of all standard tkinter widgets
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, font

class TkinterWidgetsDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter All Widgets Practice")
        self.root.geometry("1200x900")
        
        # Create notebook for organizing widgets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for different widget categories
        self.create_basic_tab()
        self.create_buttons_tab()
        self.create_text_tab()
        self.create_selection_tab()
        self.create_container_tab()
        self.create_canvas_tab()
        self.create_dialogs_tab()
        self.create_advanced_tab()
        
    def create_basic_tab(self):
        """Basic widgets: Label, Entry, Message"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Basic Widgets')
        
        # Label variations
        ttk.Label(frame, text="Label Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        label_frame = ttk.LabelFrame(frame, text="Label Examples", padding=10)
        label_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(label_frame, text="Plain Label").pack(side='left', padx=5)
        tk.Label(label_frame, text="Colored Label", bg='yellow', fg='red').pack(side='left', padx=5)
        tk.Label(label_frame, text="Bordered Label", relief='solid', borderwidth=2).pack(side='left', padx=5)
        
        # Entry variations
        entry_frame = ttk.LabelFrame(frame, text="Entry Examples", padding=10)
        entry_frame.pack(fill='x', padx=10, pady=5)
        
        self.entry_var = tk.StringVar(value="Type here...")
        tk.Entry(entry_frame, textvariable=self.entry_var, width=30).pack(side='left', padx=5)
        
        self.entry_readonly = tk.Entry(entry_frame, state='readonly', width=20)
        self.entry_readonly.pack(side='left', padx=5)
        self.entry_readonly.insert(0, "Read-only")
        
        self.entry_password = tk.Entry(entry_frame, show='*', width=20)
        self.entry_password.pack(side='left', padx=5)
        self.entry_password.insert(0, "password")
        
        # Message widget
        message_frame = ttk.LabelFrame(frame, text="Message Widget (Auto-wraps text)", padding=10)
        message_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Message(message_frame, 
                   text="This is a Message widget. It automatically wraps text to fit the width and is useful for multi-line messages that need automatic formatting.",
                   width=400,
                   bg='lightblue',
                   relief='raised').pack(fill='x')
        
        # Scale widget
        scale_frame = ttk.LabelFrame(frame, text="Scale Widget", padding=10)
        scale_frame.pack(fill='x', padx=10, pady=5)
        
        self.scale_var = tk.DoubleVar(value=50)
        tk.Scale(scale_frame, from_=0, to=100, orient='horizontal', 
                variable=self.scale_var, length=300).pack()
        ttk.Label(scale_frame, textvariable=self.scale_var).pack()
        
    def create_buttons_tab(self):
        """Button widgets: Button, Checkbutton, Radiobutton"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Buttons')
        
        ttk.Label(frame, text="Button Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Regular buttons
        btn_frame = ttk.LabelFrame(frame, text="Button Examples", padding=10)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(btn_frame, text="Regular Button", command=lambda: self.show_message("Regular button clicked!")).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Active Background", activebackground='green').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Disabled", state='disabled').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Flat Relief", relief='flat', bg='lightblue').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Raised Relief", relief='raised', bg='lightyellow').pack(side='left', padx=5)
        
        # Checkbuttons
        check_frame = ttk.LabelFrame(frame, text="Checkbutton Examples", padding=10)
        check_frame.pack(fill='x', padx=10, pady=5)
        
        self.check1_var = tk.BooleanVar(value=True)
        self.check2_var = tk.BooleanVar(value=False)
        self.check3_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(check_frame, text="Option 1", variable=self.check1_var).pack(side='left', padx=10)
        tk.Checkbutton(check_frame, text="Option 2", variable=self.check2_var).pack(side='left', padx=10)
        tk.Checkbutton(check_frame, text="Option 3 (Disabled)", variable=self.check3_var, state='disabled').pack(side='left', padx=10)
        
        ttk.Button(check_frame, text="Show Selections", 
                  command=lambda: self.show_message(f"Check1: {self.check1_var.get()}, Check2: {self.check2_var.get()}, Check3: {self.check3_var.get()}")).pack(side='left', padx=20)
        
        # Radiobuttons
        radio_frame = ttk.LabelFrame(frame, text="Radiobutton Examples", padding=10)
        radio_frame.pack(fill='x', padx=10, pady=5)
        
        self.radio_var = tk.StringVar(value='option2')
        
        tk.Radiobutton(radio_frame, text="Option A", variable=self.radio_var, value='option1').pack(side='left', padx=10)
        tk.Radiobutton(radio_frame, text="Option B", variable=self.radio_var, value='option2').pack(side='left', padx=10)
        tk.Radiobutton(radio_frame, text="Option C", variable=self.radio_var, value='option3').pack(side='left', padx=10)
        
        ttk.Button(radio_frame, text="Show Selection", 
                  command=lambda: self.show_message(f"Selected: {self.radio_var.get()}")).pack(side='left', padx=20)
        
        # Menubutton (classic)
        menubtn_frame = ttk.LabelFrame(frame, text="Menubutton (Classic)", padding=10)
        menubtn_frame.pack(fill='x', padx=10, pady=5)
        
        self.menu_var = tk.StringVar(value="Select...")
        menubutton = tk.Menubutton(menubtn_frame, textvariable=self.menu_var, relief='raised')
        menubutton.pack()
        
        menu = tk.Menu(menubutton, tearoff=0)
        menu.add_command(label="Item 1", command=lambda: self.menu_var.set("Item 1"))
        menu.add_command(label="Item 2", command=lambda: self.menu_var.set("Item 2"))
        menu.add_command(label="Item 3", command=lambda: self.menu_var.set("Item 3"))
        menubutton['menu'] = menu
        
    def create_text_tab(self):
        """Text input widgets: Text, ScrolledText, Spinbox"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Text Input')
        
        ttk.Label(frame, text="Text Input Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Text widget
        text_frame = ttk.LabelFrame(frame, text="Text Widget (Multi-line)", padding=10)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.text_widget = tk.Text(text_frame, height=8, width=60, wrap='word')
        self.text_widget.pack(side='left', fill='both', expand=True)
        self.text_widget.insert('1.0', "This is a Text widget.\n\nIt supports:\n- Multi-line text\n- Different fonts and colors\n- Selection and editing\n- Scrollbars")
        
        text_scroll = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        text_scroll.pack(side='right', fill='y')
        self.text_widget['yscrollcommand'] = text_scroll.set
        
        btn_frame = ttk.Frame(text_frame)
        btn_frame.pack(side='right', fill='y', padx=5)
        ttk.Button(btn_frame, text="Get Text", command=self.get_text_content).pack(pady=2)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.text_widget.delete('1.0', 'end')).pack(pady=2)
        ttk.Button(btn_frame, text="Insert", command=lambda: self.text_widget.insert('end', "\n[New Line]")).pack(pady=2)
        
        # Spinbox
        spin_frame = ttk.LabelFrame(frame, text="Spinbox Widget", padding=10)
        spin_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Spinbox(spin_frame, from_=0, to=100, width=10).pack(side='left', padx=5)
        tk.Spinbox(spin_frame, values=('Red', 'Green', 'Blue', 'Yellow'), width=10).pack(side='left', padx=5)
        tk.Spinbox(spin_frame, values=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), width=12).pack(side='left', padx=5)
        
    def create_selection_tab(self):
        """Selection widgets: Listbox, Combobox, OptionMenu"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Selection')
        
        ttk.Label(frame, text="Selection Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Listbox
        list_frame = ttk.LabelFrame(frame, text="Listbox Widget", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        list_container = ttk.Frame(list_frame)
        list_container.pack(side='left', fill='both', expand=True)
        
        self.listbox = tk.Listbox(list_container, selectmode='extended', exportselection=0)
        self.listbox.pack(side='left', fill='both', expand=True)
        
        for item in ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape', 'Honeydew']:
            self.listbox.insert('end', item)
        
        list_scroll = tk.Scrollbar(list_container, command=self.listbox.yview)
        list_scroll.pack(side='right', fill='y')
        self.listbox['yscrollcommand'] = list_scroll.set
        
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.pack(side='right', fill='y', padx=5)
        ttk.Button(list_btn_frame, text="Get Selected", command=self.get_listbox_selection).pack(pady=2)
        ttk.Button(list_btn_frame, text="Clear Selection", command=lambda: self.listbox.selection_clear(0, 'end')).pack(pady=2)
        ttk.Button(list_btn_frame, text="Delete Item", command=self.delete_listbox_item).pack(pady=2)
        
        # Combobox
        combo_frame = ttk.LabelFrame(frame, text="Combobox Widget", padding=10)
        combo_frame.pack(fill='x', padx=10, pady=5)
        
        self.combo_var = tk.StringVar()
        self.combobox = ttk.Combobox(combo_frame, textvariable=self.combo_var, values=['Python', 'Java', 'C++', 'JavaScript', 'Go', 'Rust'])
        self.combobox.pack(side='left', padx=5)
        self.combobox.set('Select a language...')
        
        ttk.Button(combo_frame, text="Get Value", command=lambda: self.show_message(f"Selected: {self.combo_var.get()}")).pack(side='left', padx=5)
        
        # OptionMenu
        option_frame = ttk.LabelFrame(frame, text="OptionMenu Widget", padding=10)
        option_frame.pack(fill='x', padx=10, pady=5)
        
        self.option_var = tk.StringVar(value='Select...')
        option_menu = tk.OptionMenu(option_frame, self.option_var, 'Small', 'Medium', 'Large', 'Extra Large')
        option_menu.pack(side='left', padx=5)
        
        ttk.Button(option_frame, text="Get Value", command=lambda: self.show_message(f"Selected: {self.option_var.get()}")).pack(side='left', padx=5)
        
    def create_container_tab(self):
        """Container widgets: Frame, LabelFrame, PanedWindow, Notebook"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Containers')
        
        ttk.Label(frame, text="Container Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Frame examples
        container_frame = ttk.Frame(frame)
        container_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Regular Frame
        tk_frame = tk.Frame(container_frame, bg='lightblue', borderwidth=2, relief='solid')
        tk_frame.pack(side='left', fill='both', expand=True, padx=5)
        tk.Label(tk_frame, text="tk.Frame\n(bg='lightblue')", bg='lightblue').pack(pady=20)
        
        # LabelFrame
        lbl_frame = ttk.LabelFrame(container_frame, text="LabelFrame")
        lbl_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(lbl_frame, text="Grouped widgets here").pack(pady=20)
        
        # PanedWindow
        paned_frame = ttk.LabelFrame(frame, text="PanedWindow (Resizable panes)", padding=10)
        paned_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        paned = tk.PanedWindow(paned_frame, orient='horizontal', sashrelief='raised', sashwidth=5)
        paned.pack(fill='both', expand=True)
        
        left_pane = tk.Frame(paned, bg='lightgreen', width=200)
        tk.Label(left_pane, text="Left Pane\n(Drag sash to resize)", bg='lightgreen').pack(expand=True)
        paned.add(left_pane)
        
        right_pane = tk.Frame(paned, bg='lightcoral', width=200)
        tk.Label(right_pane, text="Right Pane", bg='lightcoral').pack(expand=True)
        paned.add(right_pane)
        
    def create_canvas_tab(self):
        """Canvas widget demonstrations"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Canvas')
        
        ttk.Label(frame, text="Canvas Widget", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Canvas with shapes
        self.canvas = tk.Canvas(frame, width=800, height=500, bg='white', scrollregion=(0, 0, 1000, 800))
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbars for canvas
        v_scroll = tk.Scrollbar(frame, orient='vertical', command=self.canvas.yview)
        v_scroll.pack(side='right', fill='y')
        h_scroll = tk.Scrollbar(frame, orient='horizontal', command=self.canvas.xview)
        h_scroll.pack(side='bottom', fill='x')
        
        self.canvas['yscrollcommand'] = v_scroll.set
        self.canvas['xscrollcommand'] = h_scroll.set
        
        # Draw shapes
        self.canvas.create_text(400, 30, text="Canvas Drawing Examples", font=('Helvetica', 16, 'bold'))
        
        # Rectangle
        self.canvas.create_rectangle(50, 60, 200, 160, fill='red', outline='black', width=2)
        self.canvas.create_text(125, 170, text="Rectangle")
        
        # Oval
        self.canvas.create_oval(250, 60, 400, 160, fill='blue', outline='black', width=2)
        self.canvas.create_text(325, 170, text="Oval")
        
        # Polygon
        self.canvas.create_polygon([450, 160, 500, 60, 550, 160], fill='green', outline='black', width=2)
        self.canvas.create_text(500, 170, text="Polygon")
        
        # Line
        self.canvas.create_line(600, 60, 750, 160, fill='purple', width=3)
        self.canvas.create_line(600, 160, 750, 60, fill='orange', width=3)
        self.canvas.create_text(675, 170, text="Lines")
        
        # Arc
        self.canvas.create_arc(50, 200, 200, 350, start=0, extent=90, fill='yellow', outline='black')
        self.canvas.create_text(125, 370, text="Arc (90°)")
        
        # Text on canvas
        self.canvas.create_text(325, 250, text="Canvas Text", font=('Arial', 14), fill='navy')
        
        # Image placeholder (drawn rectangle with text)
        self.canvas.create_rectangle(450, 200, 600, 350, fill='lightgray', outline='black')
        self.canvas.create_text(525, 275, text="Image\nPlaceholder")
        
        # Interactive drawing area
        self.canvas.create_text(675, 220, text="Click & Drag to draw", font=('Arial', 10))
        self.canvas.bind('<B1-Motion>', self.canvas_draw)
        
    def create_dialogs_tab(self):
        """Dialog widgets: MessageBox, FileDialog, ColorChooser"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Dialogs')
        
        ttk.Label(frame, text="Dialog Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Messagebox
        msg_frame = ttk.LabelFrame(frame, text="Messagebox Dialogs", padding=10)
        msg_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(msg_frame, text="Show Info", command=lambda: messagebox.showinfo("Info", "This is an information message!")).pack(side='left', padx=5)
        ttk.Button(msg_frame, text="Show Warning", command=lambda: messagebox.showwarning("Warning", "This is a warning!")).pack(side='left', padx=5)
        ttk.Button(msg_frame, text="Show Error", command=lambda: messagebox.showerror("Error", "This is an error!")).pack(side='left', padx=5)
        ttk.Button(msg_frame, text="Ask Yes/No", command=lambda: self.show_message(f"Result: {messagebox.askyesno('Question', 'Do you agree?')}")).pack(side='left', padx=5)
        ttk.Button(msg_frame, text="Ask OK/Cancel", command=lambda: self.show_message(f"Result: {messagebox.askokcancel('Confirm', 'Proceed?')}")).pack(side='left', padx=5)
        
        # File dialogs
        file_frame = ttk.LabelFrame(frame, text="File Dialogs", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(file_frame, text="Open File", command=self.open_file_dialog).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Save File", command=self.save_file_dialog).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Choose Directory", command=self.choose_directory).pack(side='left', padx=5)
        
        # Color chooser
        color_frame = ttk.LabelFrame(frame, text="Color Chooser", padding=10)
        color_frame.pack(fill='x', padx=10, pady=5)
        
        self.color_preview = tk.Canvas(color_frame, width=100, height=50, bg='white', relief='solid')
        self.color_preview.pack(side='left', padx=5)
        
        ttk.Button(color_frame, text="Choose Color", command=self.choose_color).pack(side='left', padx=5)
        
    def create_advanced_tab(self):
        """Advanced widgets: Treeview, Progressbar, Separator, Sizegrip"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Advanced')
        
        ttk.Label(frame, text="Advanced Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Treeview
        tree_frame = ttk.LabelFrame(frame, text="Treeview Widget", padding=10)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=('Size', 'Modified'), show='tree headings', height=8)
        self.tree.pack(side='left', fill='both', expand=True)
        
        self.tree.heading('#0', text='Name')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Modified')
        
        self.tree.column('#0', width=200)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=150)
        
        # Add items
        root1 = self.tree.insert('', 'end', text='Documents', values=('-', '2024-01-15'))
        self.tree.insert(root1, 'end', text='report.pdf', values=('2.5 MB', '2024-01-10'))
        self.tree.insert(root1, 'end', text='data.xlsx', values=('1.2 MB', '2024-01-12'))
        
        root2 = self.tree.insert('', 'end', text='Images', values=('-', '2024-01-14'))
        self.tree.insert(root2, 'end', text='photo1.jpg', values=('3.1 MB', '2024-01-08'))
        self.tree.insert(root2, 'end', text='photo2.jpg', values=('2.8 MB', '2024-01-09'))
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree['yscrollcommand'] = tree_scroll.set
        
        # Progressbar
        progress_frame = ttk.LabelFrame(frame, text="Progressbar Widget", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(side='left', padx=5)
        self.progress['value'] = 50
        
        ttk.Button(progress_frame, text="25%", command=lambda: self.progress.configure(value=25)).pack(side='left', padx=2)
        ttk.Button(progress_frame, text="50%", command=lambda: self.progress.configure(value=50)).pack(side='left', padx=2)
        ttk.Button(progress_frame, text="75%", command=lambda: self.progress.configure(value=75)).pack(side='left', padx=2)
        ttk.Button(progress_frame, text="100%", command=lambda: self.progress.configure(value=100)).pack(side='left', padx=2)
        
        # Indeterminate progressbar
        self.progress_ind = ttk.Progressbar(progress_frame, length=200, mode='indeterminate')
        self.progress_ind.pack(side='left', padx=20)
        ttk.Button(progress_frame, text="Start", command=self.progress_ind.start).pack(side='left')
        ttk.Button(progress_frame, text="Stop", command=self.progress_ind.stop).pack(side='left', padx=2)
        
        # Separator and Sizegrip
        sep_frame = ttk.LabelFrame(frame, text="Separator & Sizegrip", padding=10)
        sep_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(sep_frame, text="Above separator").pack()
        ttk.Separator(sep_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(sep_frame, text="Below separator").pack()
        
        ttk.Separator(sep_frame, orient='vertical').pack(side='left', fill='y', padx=20, pady=10)
        
        ttk.Label(sep_frame, text="Sizegrip (resize window from corner)", font=('Arial', 9, 'italic')).pack(side='left', padx=10)
        
    # Helper methods
    def show_message(self, message):
        """Display message in a label or print"""
        messagebox.showinfo("Message", message)
        
    def get_text_content(self):
        content = self.text_widget.get('1.0', 'end-1c')
        self.show_message(f"Text content:\n{content[:100]}...")
        
    def get_listbox_selection(self):
        selection = self.listbox.curselection()
        if selection:
            items = [self.listbox.get(i) for i in selection]
            self.show_message(f"Selected: {', '.join(items)}")
        else:
            self.show_message("No selection")
            
    def delete_listbox_item(self):
        selection = self.listbox.curselection()
        if selection:
            for index in reversed(selection):
                self.listbox.delete(index)
                
    def canvas_draw(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='black')
        
    def open_file_dialog(self):
        filename = filedialog.askopenfilename(title="Select a file")
        if filename:
            self.show_message(f"Selected: {filename}")
            
    def save_file_dialog(self):
        filename = filedialog.asksaveasfilename(title="Save file", defaultextension=".txt")
        if filename:
            self.show_message(f"Save to: {filename}")
            
    def choose_directory(self):
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            self.show_message(f"Directory: {directory}")
            
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose a color")
        if color[1]:
            self.color_preview.config(bg=color[1])
            self.show_message(f"Selected color: {color[1]}")


def main():
    root = tk.Tk()
    app = TkinterWidgetsDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
