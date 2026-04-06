"""
Tkinter All Widgets Practice
A comprehensive demonstration of all standard tkinter widgets
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, font
from PIL import Image, ImageTk

class TkinterWidgetsDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter All Widgets Practice")
        self.root.geometry("1200x900")

        # Load icons for Treeview
        self.load_icons()

        # Create menubar
        self.create_menubar()

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
        self.create_menu_tab()

    def create_menubar(self):
        """Create application menubar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.menu_new, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.menu_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.menu_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.menu_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.show_message("Cut"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.show_message("Copy"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.show_message("Paste"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=self.menu_preferences)

        # View Menu (with checkbuttons)
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        self.show_status = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Show Status Bar", variable=self.show_status, command=self.toggle_status_bar)
        view_menu.add_checkbutton(label="Show Toolbar", variable=tk.BooleanVar(value=False))
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=lambda: self.show_message("Zoom In"))
        view_menu.add_command(label="Zoom Out", command=lambda: self.show_message("Zoom Out"))

        # Tools Menu (with radio buttons)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        self.tool_mode = tk.StringVar(value="select")
        tools_menu.add_radiobutton(label="Selection Mode", variable=self.tool_mode, value="select", command=self.tool_changed)
        tools_menu.add_radiobutton(label="Drawing Mode", variable=self.tool_mode, value="draw", command=self.tool_changed)
        tools_menu.add_radiobutton(label="Edit Mode", variable=self.tool_mode, value="edit", command=self.tool_changed)
        tools_menu.add_separator()

        # Submenu in Tools
        sub_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Advanced", menu=sub_menu)
        sub_menu.add_command(label="Option 1", command=lambda: self.show_message("Advanced Option 1"))
        sub_menu.add_command(label="Option 2", command=lambda: self.show_message("Advanced Option 2"))

        # Widgets Menu
        widgets_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Widgets", menu=widgets_menu)
        widgets_menu.add_command(label="Go to Basic", command=lambda: self.notebook.select(0))
        widgets_menu.add_command(label="Go to Buttons", command=lambda: self.notebook.select(1))
        widgets_menu.add_command(label="Go to Canvas", command=lambda: self.notebook.select(5))
        widgets_menu.add_separator()
        widgets_menu.add_command(label="Refresh All", command=self.refresh_all)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=lambda: self.show_message("Documentation"))
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

        # Context menu (right-click)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.show_message("Context: Cut"))
        self.context_menu.add_command(label="Copy", command=lambda: self.show_message("Context: Copy"))
        self.context_menu.add_command(label="Paste", command=lambda: self.show_message("Context: Paste"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Properties", command=lambda: self.show_message("Properties"))

        # Bind right-click to show context menu
        self.root.bind("<Button-3>", self.show_context_menu)  # Windows
        self.root.bind("<Button-2>", self.show_context_menu)    # macOS

    def menu_new(self):
        """Handle New menu action"""
        messagebox.showinfo("New", "Creating new file...")

    def menu_open(self):
        """Handle Open menu action"""
        filename = filedialog.askopenfilename(title="Open File")
        if filename:
            self.show_message(f"Opening: {filename}")

    def menu_save(self):
        """Handle Save menu action"""
        self.show_message("File saved!")

    def menu_save_as(self):
        """Handle Save As menu action"""
        filename = filedialog.asksaveasfilename(title="Save As")
        if filename:
            self.show_message(f"Saved to: {filename}")

    def menu_preferences(self):
        """Open preferences dialog"""
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("300x200")
        ttk.Label(pref_window, text="Preferences Window", font=('Helvetica', 14)).pack(pady=20)
        ttk.Label(pref_window, text="Settings would go here...").pack(pady=10)
        ttk.Button(pref_window, text="Close", command=pref_window.destroy).pack(pady=20)

    def toggle_status_bar(self):
        """Toggle status bar visibility"""
        if self.show_status.get():
            self.show_message("Status bar shown")
        else:
            self.show_message("Status bar hidden")

    def tool_changed(self):
        """Handle tool mode change"""
        self.show_message(f"Tool mode changed to: {self.tool_mode.get()}")

    def show_shortcuts(self):
        """Display keyboard shortcuts"""
        shortcuts = """Keyboard Shortcuts:

File:
  Ctrl+N - New
  Ctrl+O - Open
  Ctrl+S - Save

Edit:
  Ctrl+X - Cut
  Ctrl+C - Copy
  Ctrl+V - Paste

View:
  Ctrl++ - Zoom In
  Ctrl+- - Zoom Out
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def show_about(self):
        """Display About dialog"""
        about_text = """Tkinter All Widgets Practice
Version 1.0

A comprehensive demonstration of tkinter widgets.

Created for learning and practicing GUI development.
"""
        messagebox.showinfo("About", about_text)

    def show_context_menu(self, event):
        """Show context menu at mouse position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def refresh_all(self):
        """Refresh all widgets"""
        self.show_message("Refreshing all widgets...")
        
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
        
    def load_icons(self):
        """Load and resize icons for Treeview"""
        try:
            # Using castle.gif for folders and dive.gif for files (resized to 16x16)
            folder_pil = Image.open("images/castle.gif").resize((16, 16), Image.Resampling.LANCZOS)
            file_pil = Image.open("images/dive.gif").resize((16, 16), Image.Resampling.LANCZOS)
            
            self.folder_icon = ImageTk.PhotoImage(folder_pil)
            self.file_icon = ImageTk.PhotoImage(file_pil)
            
            # Map item names to preview images
            self.preview_images = {}
            preview_files = {
                'photo1.jpg': 'images/s6.jpg',
                'photo2.jpg': 'images/s7.jpg',
                'report.pdf': 'images/beach.jpg',
                'data.xlsx': 'images/boat.jpg'
            }
            
            for name, path in preview_files.items():
                try:
                    pil_img = Image.open(path).resize((250, 180), Image.Resampling.LANCZOS)
                    self.preview_images[name] = ImageTk.PhotoImage(pil_img)
                except:
                    pass
                    
            # Default preview
            default_pil = Image.open("images/kimura.jpg").resize((250, 180), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(default_pil)
        except Exception as e:
            print(f"Error loading icons: {e}")
            self.folder_icon = None
            self.file_icon = None
            self.preview_photo = None
            self.preview_images = {}

    def on_tree_select(self, event):
        """Handle tree selection to update preview"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item_text = self.tree.item(selected_item[0], 'text')
        
        if item_text in self.preview_images:
            self.tree_image_label.config(image=self.preview_images[item_text], text=f"Preview: {item_text}")
        else:
            # For folders or items without specific image
            if self.tree.get_children(selected_item[0]):
                self.tree_image_label.config(image=self.preview_photo, text="Category Preview")
            else:
                self.tree_image_label.config(image='', text=f"No preview available\nfor {item_text}")

    def create_advanced_tab(self):
        """Advanced widgets: Treeview, Progressbar, Separator, Sizegrip"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Advanced')
        
        ttk.Label(frame, text="Advanced Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Treeview with images
        tree_preview_frame = ttk.Frame(frame)
        tree_preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tree_frame = ttk.LabelFrame(tree_preview_frame, text="Treeview (with Icons and Images)", padding=10)
        tree_frame.pack(side='left', fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=('Size', 'Modified'), show='tree headings', height=8)
        self.tree.pack(side='left', fill='both', expand=True)
        
        self.tree.heading('#0', text='Name')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Modified')
        
        self.tree.column('#0', width=200)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=150)
        
        # Add items with icons
        root1 = self.tree.insert('', 'end', text='Documents', values=('-', '2024-01-15'), image=self.folder_icon)
        self.tree.insert(root1, 'end', text='report.pdf', values=('2.5 MB', '2024-01-10'), image=self.file_icon)
        self.tree.insert(root1, 'end', text='data.xlsx', values=('1.2 MB', '2024-01-12'), image=self.file_icon)
        
        root2 = self.tree.insert('', 'end', text='Images', values=('-', '2024-01-14'), image=self.folder_icon)
        self.tree.insert(root2, 'end', text='photo1.jpg', values=('3.1 MB', '2024-01-08'), image=self.file_icon)
        self.tree.insert(root2, 'end', text='photo2.jpg', values=('2.8 MB', '2024-01-09'), image=self.file_icon)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side='right', fill='y')
        self.tree['yscrollcommand'] = tree_scroll.set

        # Preview area for Treeview selection
        preview_frame = ttk.LabelFrame(tree_preview_frame, text="Selection Preview", padding=10)
        preview_frame.pack(side='right', fill='both', expand=False, padx=(10, 0))
        
        self.tree_image_label = ttk.Label(preview_frame, text="Select an image\nto see preview", anchor='center', justify='center')
        self.tree_image_label.pack(pady=10)
        
        if self.preview_photo:
            self.tree_image_label.config(image=self.preview_photo, compound='top')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
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

    def create_menu_tab(self):
        """Menu widget demonstrations"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Menus')

        ttk.Label(frame, text="Menu Widgets", font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Description
        desc = """Menus are created using the Menu widget.

Types of menu items:
• command - Normal menu item
• checkbutton - Toggle on/off
• radiobutton - Select one from group
• cascade - Submenu
• separator - Visual divider

This app demonstrates a complete menubar:
File, Edit, View, Tools, Widgets, and Help menus.

Right-click anywhere for a context menu!
"""
        tk.Message(frame, text=desc, width=800, font=('Arial', 11), bg='lightyellow', relief='groove').pack(fill='x', padx=20, pady=10)

        # Menu demo frame
        demo_frame = ttk.LabelFrame(frame, text="Menu Demo", padding=20)
        demo_frame.pack(fill='both', expand=True, padx=20, pady=10)

        ttk.Label(demo_frame, text="Try the menubar above!", font=('Helvetica', 12)).pack(pady=10)
        ttk.Label(demo_frame, text="Check out: File → New, Edit → Cut/Copy/Paste, View → Show Status Bar", font=('Arial', 10)).pack(pady=5)
        ttk.Label(demo_frame, text="Tools has radio buttons and a submenu", font=('Arial', 10)).pack(pady=5)
        ttk.Label(demo_frame, text="Widgets menu lets you jump to tabs", font=('Arial', 10)).pack(pady=5)
        ttk.Label(demo_frame, text="Help → About shows app info", font=('Arial', 10)).pack(pady=5)

        # Menu bar structure visualization
        struct_frame = ttk.LabelFrame(frame, text="Menu Structure", padding=10)
        struct_frame.pack(fill='x', padx=20, pady=10)

        tree = ttk.Treeview(struct_frame, columns=('Type',), show='tree headings', height=10)
        tree.pack(fill='x')
        tree.heading('#0', text='Menu Item')
        tree.heading('Type', text='Type')
        tree.column('#0', width=250)
        tree.column('Type', width=150)

        # Menu structure
        file = tree.insert('', 'end', text='File', values=('cascade',))
        tree.insert(file, 'end', text='New', values=('command',))
        tree.insert(file, 'end', text='Open...', values=('command',))
        tree.insert(file, 'end', text='Save', values=('command',))
        tree.insert(file, 'end', text='---', values=('separator',))
        tree.insert(file, 'end', text='Exit', values=('command',))

        edit = tree.insert('', 'end', text='Edit', values=('cascade',))
        tree.insert(edit, 'end', text='Cut', values=('command',))
        tree.insert(edit, 'end', text='Copy', values=('command',))
        tree.insert(edit, 'end', text='Paste', values=('command',))

        view = tree.insert('', 'end', text='View', values=('cascade',))
        tree.insert(view, 'end', text='Show Status Bar', values=('checkbutton',))
        tree.insert(view, 'end', text='Show Toolbar', values=('checkbutton',))

        tools = tree.insert('', 'end', text='Tools', values=('cascade',))
        tree.insert(tools, 'end', text='Selection Mode', values=('radiobutton',))
        tree.insert(tools, 'end', text='Drawing Mode', values=('radiobutton',))
        tree.insert(tools, 'end', text='Advanced', values=('cascade',))

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
