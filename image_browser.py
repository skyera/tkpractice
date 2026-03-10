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
        self.root.geometry("900x700")
        
        self.image_files = []
        self.current_index = 0
        self.photo_image = None
        self.loading = False  # Prevent race conditions
        
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
        
        # Create image display frame
        self.image_frame = tk.Frame(root, bg="black")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(self.image_frame, bg="black")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Create metadata frame for datetime
        metadata_frame = tk.Frame(root, bg="lightgray")
        metadata_frame.pack(fill=tk.X, padx=10)
        
        self.datetime_label = tk.Label(metadata_frame, text="Date/Time: ", bg="lightgray", font=("Arial", 10))
        self.datetime_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Create bottom frame for navigation
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.prev_btn = tk.Button(bottom_frame, text="< Previous", command=self.prev_image, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.info_label = tk.Label(bottom_frame, text="No images loaded")
        self.info_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        self.next_btn = tk.Button(bottom_frame, text="Next >", command=self.next_image, state=tk.DISABLED)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        # Load last folder automatically (after UI is fully initialized)
        if self.last_folder and os.path.isdir(self.last_folder):
            self.load_images(self.last_folder)
    
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder with images")
        if folder:
            self.save_config(folder)
            self.load_images(folder)
    
    def load_images(self, folder_path):
        """Load all image files from the selected folder"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        self.image_files = [
            str(f) for f in Path(folder_path).iterdir()
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        self.image_files.sort()
        
        if self.image_files:
            self.current_index = 0
            self.folder_label.config(text=f"Folder: {folder_path}", fg="black")
            self.display_image()
            self.update_buttons()
        else:
            self.folder_label.config(text="No images found in this folder", fg="red")
            if self.photo_image:
                del self.photo_image
            self.photo_image = None
            self.image_label.config(image='')
            self.info_label.config(text="No images found")
            self.datetime_label.config(text="Date/Time: ")
            self.update_buttons()
    
    def display_image(self):
        """Display the current image"""
        if not self.image_files or self.loading:
            return
        
        self.loading = True
        image_path = self.image_files[self.current_index]
        
        try:
            image = Image.open(image_path)
            
            # Apply EXIF orientation if available
            image = self.apply_exif_orientation(image)
            
            # Resize image to fit in frame while maintaining aspect ratio
            max_width, max_height = 850, 600
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Clean up old image reference to prevent memory leak
            if self.photo_image:
                del self.photo_image
            
            self.photo_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo_image)
            
            # Update info label
            filename = os.path.basename(image_path)
            self.info_label.config(
                text=f"{self.current_index + 1}/{len(self.image_files)} - {filename}"
            )
            
            # Extract and display datetime
            datetime_str = self.get_image_datetime(image_path)
            self.datetime_label.config(text=f"Date/Time: {datetime_str}")
        except Exception as e:
            self.info_label.config(text=f"Error loading image: {str(e)}")
            self.datetime_label.config(text="Date/Time: Error reading metadata")
        finally:
            self.loading = False
    
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()
