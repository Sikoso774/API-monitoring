import os
import customtkinter as ctk
import tkintermapview
from PIL import Image, ImageTk
from config.settings import COLORS, ASSETS_DIR

class TabSupervision:
    def __init__(self, parent_frame, api_client):
        self.parent = parent_frame
        self.api = api_client
        self.current_address = "" # Pour savoir si on doit rafraîchir
        
        self.setup_ui()
        self.auto_refresh_monitoring()

    def load_icon_with_ratio(self, filename, width_wanted=35):
        path = os.path.join(ASSETS_DIR, filename)
        pil_img = Image.open(path)
        ratio = pil_img.height / pil_img.width
        height_calculated = int(width_wanted * ratio)
        img_resized = pil_img.resize((width_wanted, height_calculated), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img_resized)

    def setup_ui(self):
        try:
            self.img_pin_ok = self.load_icon_with_ratio("green_pin.png", width_wanted=35)
            self.img_pin_error = self.load_icon_with_ratio("red_pin.png", width_wanted=35)
        except Exception:
            self.img_pin_ok = None
            self.img_pin_error = None

        self.info_panel = ctk.CTkFrame(self.parent, width=300, fg_color="transparent")
        self.info_panel.pack(side="left", fill="y", padx=20, pady=20)

        self.label_client = ctk.CTkLabel(self.info_panel, text="Sélectionnez un lien", font=("Arial", 16, "bold"), wraplength=250)
        self.label_client.pack(pady=20)
        self.label_address = ctk.CTkLabel(self.info_panel, text="", font=("Arial", 12), wraplength=250)
        self.label_address.pack(pady=10)
        self.label_status = ctk.CTkLabel(self.info_panel, text="-", font=("Arial", 30, "bold"))
        self.label_status.pack(pady=30)
        self.btn_mon = ctk.CTkButton(self.info_panel, text="Rafraîchir Statut", fg_color=COLORS["primary"], command=self.fetch_monitoring_data)
        self.btn_mon.pack(pady=20)

        self.map_widget = tkintermapview.TkinterMapView(self.parent, corner_radius=10)
        self.map_widget.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png")
        self.map_widget.set_position(48.8566, 2.3522)

    def load_client(self, link):
        """Appelée par app.py quand on clique sur SUPERVISER"""
        self.label_client.configure(text=f"Client : {link.get('client_name')}")
        self.label_address.configure(text=f"Adresse : {link.get('address')}")
        self.label_status.configure(text="Chargement...", text_color=COLORS["text"])
        self.current_address = link.get('address', '')
        self.fetch_monitoring_data()

    def fetch_monitoring_data(self):
        try:
            lien = self.api.get_monitoring_data()
            
            if lien.get('address'):
                self.label_address.configure(text=f"Adresse : {lien.get('address')}")
                self.current_address = lien.get('address')
            
            status = str(lien.get('status_display', 'inconnu')).lower()
            is_ok = (status == 'ok')
            color = COLORS["accent"] if is_ok else COLORS["error"]
            self.label_status.configure(text=f"STATUT : {status.upper()}", text_color=color)
            
            lat, lng = lien.get('lat'), lien.get('lng')
            if lat and lng:
                self.map_widget.delete_all_marker()
                self.map_widget.set_position(lat, lng)
                
                icone = self.img_pin_ok if is_ok else self.img_pin_error
                
                if icone:
                    self.map_widget.set_marker(lat, lng, text=f"État : {status.upper()}", icon=icone, text_color=COLORS["text"])
                else:
                    self.map_widget.set_marker(lat, lng, text=f"État : {status.upper()}", marker_color_circle=color, marker_color_outside=color, text_color=COLORS["text"])
                
                self.map_widget.set_zoom(13)
        except Exception:
            self.label_status.configure(text="Erreur Supervision", text_color="red")

    def auto_refresh_monitoring(self):
        if self.current_address != "":
            self.fetch_monitoring_data()
        # On utilise master.after car self n'est pas un widget TK ici
        self.parent.after(60000, self.auto_refresh_monitoring)