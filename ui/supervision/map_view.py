import os
import tkintermapview
import customtkinter as ctk
from PIL import Image, ImageTk
from config.settings import COLORS, IMG_DIR

class MapView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Chargement des icônes
        self.img_ok = self._load_pin("green_pin.png")
        self.img_err = self._load_pin("red_pin.png")
        
        # Widget Carte
        self.map_widget = tkintermapview.TkinterMapView(self, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png")
        self.map_widget.set_position(48.8566, 2.3522) # Paris par défaut

    def _load_pin(self, filename):
        try:
            path = os.path.join(IMG_DIR, filename)
            pil_img = Image.open(path)
            # On force une taille de pin standard
            img_resized = pil_img.resize((35, 45), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_resized)
        except: return None

    def update_marker(self, lat, lng, status):
        if not lat or not lng: return
        
        self.map_widget.delete_all_marker()
        self.map_widget.set_position(lat, lng)
        
        is_ok = (status.strip().upper() == "OK")
        icon = self.img_ok if is_ok else self.img_err
        
        self.map_widget.set_marker(lat, lng, text=f"État : {status}", icon=icon, text_color=COLORS["text"])
        self.map_widget.set_zoom(14)