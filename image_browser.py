import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from pathlib import Path
from datetime import datetime
import json

class ImageBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser")
        self.root.geometry("1100x800")
        
        self.image_files = []
        self.thumbnails = []
        self.thumbnail_labels = []
        self.current_index = 0
        self.photo_image = None
        self.current_pil_image = None  # Store original image for resizing
        self.loading = False
        
        # Config file for remembering last folder
        self.config_file = os.path.join(Path.home(), ".image_browser_config.json")
        self.last_folder = self.load_config()
        
        # Create top frame for folder selection
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.browse_btn = tk.Button(top_frame, text="Open Folder", command=self.open_folder)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_label = tk.Label(top_frame, text="No folder selected", fg="gray")
        self.folder_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Main content area with PanedWindow
        self.paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Gallery Frame (Left)
        self.gallery_container = tk.Frame(self.paned, width=200, bg="gray90")
        self.paned.add(self.gallery_container, width=200)
        
        self.gallery_canvas = tk.Canvas(self.gallery_container, bg="gray90", highlightthickness=0)
        self.gallery_scrollbar = tk.Scrollbar(self.gallery_container, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_scrollable_frame = tk.Frame(self.gallery_canvas, bg="gray90")
        
        self.gallery_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
        )
        
        self.canvas_window = self.gallery_canvas.create_window((0, 0), window=self.gallery_scrollable_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=self.gallery_scrollbar.set)
        
        # Add mouse wheel support
        self.gallery_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Ensure the inner frame matches the canvas width for centering/expansion
        self.gallery_canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        self.gallery_scrollbar.pack(side="right", fill="y")
        
        # Viewer Frame (Right)
        self.viewer_frame = tk.Frame(self.paned)
        self.paned.add(self.viewer_frame)
        
        # Create image display frame
        self.image_frame = tk.Frame(self.viewer_frame, bg="black")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(self.image_frame, bg="black")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize event to image frame
        self.image_frame.bind("<Configure>", self.on_viewer_resize)
        
        # Create metadata frame for datetime
        metadata_frame = tk.Frame(self.viewer_frame, bg="lightgray")
        metadata_frame.pack(fill=tk.X, padx=10)
        
        self.datetime_label = tk.Label(metadata_frame, text="Date/Time: ", bg="lightgray", font=("Arial", 10))
        self.datetime_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Create bottom frame for navigation
        bottom_frame = tk.Frame(self.viewer_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.prev_btn = tk.Button(bottom_frame, text="< Previous", command=self.prev_image, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.info_label = tk.Label(bottom_frame, text="No images loaded")
        self.info_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        self.next_btn = tk.Button(bottom_frame, text="Next >", command=self.next_image, state=tk.DISABLED)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        # Load last folder automatically
        if self.last_folder and os.path.isdir(self.last_folder):
            self.load_images(self.last_folder)
    
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder with images")
        if folder:
            self.save_config(folder)
            self.load_images(folder)
    
    def load_images(self, folder_path):
        """Load all image files and create thumbnails"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        self.image_files = [
            str(f) for f in Path(folder_path).iterdir()
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        self.image_files.sort()
        
        # Clear existing thumbnails
        for widget in self.gallery_scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []
        self.thumbnail_labels = []
        
        if self.image_files:
            self.current_index = 0
            self.folder_label.config(text=f"Folder: {folder_path}", fg="black")
            
            # Create thumbnails
            for i, img_path in enumerate(self.image_files):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((150, 150))
                    thumb = ImageTk.PhotoImage(img)
                    self.thumbnails.append(thumb)
                    
                    lbl = tk.Label(self.gallery_scrollable_frame, image=thumb, bg="gray90", cursor="hand2")
                    lbl.pack(pady=5, padx=10)
                    lbl.bind("<Button-1>", lambda e, index=i: self.select_image(index))
                    self.thumbnail_labels.append(lbl)
                except Exception as e:
                    print(f"Error creating thumbnail for {img_path}: {e}")
            
            self.display_image()
            self.update_buttons()
        else:
            self.folder_label.config(text="No images found in this folder", fg="red")
            self.current_pil_image = None
            if self.photo_image:
                del self.photo_image
            self.photo_image = None
            self.image_label.config(image='')
            self.info_label.config(text="No images found")
            self.datetime_label.config(text="Date/Time: ")
            self.update_buttons()
    
    def select_image(self, index):
        """Select image from gallery"""
        self.current_index = index
        self.display_image()
        self.update_buttons()
    
    def on_viewer_resize(self, event=None):
        """Handle viewer frame resize by re-rendering the image"""
        if not self.loading and self.current_pil_image:
            self.render_image()

    def display_image(self):
        """Load and prepare the current image for display"""
        if not self.image_files or self.loading:
            return
        
        self.loading = True
        image_path = self.image_files[self.current_index]
        
        # Highlight selected thumbnail and scroll to it
        for i, lbl in enumerate(self.thumbnail_labels):
            if i == self.current_index:
                lbl.config(bg="blue")
                # Ensure the selected thumbnail is visible
                self.root.update_idletasks()
                y1 = lbl.winfo_y()
                y2 = y1 + lbl.winfo_height()
                canvas_height = self.gallery_canvas.winfo_height()
                scroll_pos = self.gallery_canvas.yview()
                total_height = self.gallery_scrollable_frame.winfo_height()
                
                if total_height > 0:
                    view_top = scroll_pos[0] * total_height
                    view_bottom = scroll_pos[1] * total_height
                    if y1 < view_top:
                        self.gallery_canvas.yview_moveto(y1 / total_height)
                    elif y2 > view_bottom:
                        self.gallery_canvas.yview_moveto((y2 - canvas_height) / total_height)
            else:
                lbl.config(bg="gray90")
        
        try:
            # Load original image and apply orientation once
            img = Image.open(image_path)
            self.current_pil_image = self.apply_exif_orientation(img)
            
            # Render to current frame size
            self.render_image()
            
            filename = os.path.basename(image_path)
            self.info_label.config(
                text=f"{self.current_index + 1}/{len(self.image_files)} - {filename}"
            )
            
            datetime_str = self.get_image_datetime(image_path)
            self.datetime_label.config(text=f"Date/Time: {datetime_str}")
        except Exception as e:
            self.info_label.config(text=f"Error loading image: {str(e)}")
            self.datetime_label.config(text="Date/Time: Error reading metadata")
            self.current_pil_image = None
        finally:
            self.loading = False

    def render_image(self):
        """Scale and display the current PIL image in the viewer label"""
        if not self.current_pil_image:
            return
            
        try:
            # Get current size of image_frame
            max_width = self.image_frame.winfo_width() - 20
            max_height = self.image_frame.winfo_height() - 20
            
            if max_width < 50 or max_height < 50:
                # Use geometry or defaults if winfo is not yet accurate
                max_width, max_height = 850, 600
            
            # Create a copy for resizing to preserve the original pil image
            display_img = self.current_pil_image.copy()
            display_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            if self.photo_image:
                del self.photo_image
            
            self.photo_image = ImageTk.PhotoImage(display_img)
            self.image_label.config(image=self.photo_image)
        except Exception as e:
            print(f"Render error: {e}")
    
    def next_image(self):
        """Show next image"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_image()
            self.update_buttons()
    
    def prev_image(self):
        """Show previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()
            self.update_buttons()
    
    def update_buttons(self):
        """Enable/disable navigation buttons based on current position"""
        if not self.image_files:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.image_files) - 1 else tk.DISABLED)
    
    def apply_exif_orientation(self, image):
        """Apply EXIF orientation to rotate image correctly"""
        try:
            exif_data = image.getexif()
            if exif_data:
                orientation = exif_data.get(274)  # Tag 274 is Orientation
                
                if orientation == 2:
                    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 4:
                    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    image = image.rotate(90, expand=True)
                    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    image = image.rotate(-90, expand=True)
                elif orientation == 7:
                    image = image.rotate(-90, expand=True)
                    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except:
            pass
        
        return image
    
    def get_image_datetime(self, image_path):
        """Extract datetime from EXIF data or file modification time"""
        # Try to get EXIF DateTimeOriginal (when photo was taken)
        try:
            image = Image.open(image_path)
            exif_data = image.getexif()  # Public method, works with Pillow 8.2.0+
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    # DateTimeOriginal tag ID is 36867 (preferred)
                    if tag_id == 36867 or tag_name == "DateTimeOriginal":
                        return f"{value} (Taken)"
        except:
            pass
        
        # Try EXIF DateTime (when file was modified)
        try:
            image = Image.open(image_path)
            exif_data = image.getexif()
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    # DateTime tag ID is 306
                    if tag_id == 306:
                        return f"{value} (EXIF)"
        except:
            pass
        
        # Fallback to file modification time
        try:
            mod_time = os.path.getmtime(image_path)
            dt = datetime.fromtimestamp(mod_time)
            return dt.strftime("%Y:%m:%d %H:%M:%S (Modified)")
        except:
            return "Unknown"
    
    def save_config(self, folder_path):
        """Save the last opened folder to config file"""
        try:
            config = {"last_folder": folder_path}
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except:
            pass
    
    def load_config(self):
        """Load the last opened folder from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    return config.get("last_folder")
        except:
            pass
        return None

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the gallery"""
        self.gallery_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_canvas_configure(self, event):
        """Adjust the width of the scrollable frame to match the canvas"""
        self.gallery_canvas.itemconfig(self.canvas_window, width=event.width)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()
