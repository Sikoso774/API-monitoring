import os
import csv
import customtkinter as ctk
import tkintermapview
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

# Import de nos propres modules
import config
from api_client import API_Client

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Noxia Security - Dashboard")
        # self.geometry("1100x850")
        # On remplace la taille fixe par un calcul dynamique
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # On calcule 85% de la taille de l'écran
        app_width = int(screen_width * 0.85)
        app_height = int(screen_height * 0.85)
        self.geometry(f"{app_width}x{app_height}")
        
        # On définit une taille minimale pour éviter que tout s'écrase
        self.minsize(900, 600)
        
        # Astuce Windows : Lancer la fenêtre directement agrandie
        try:
            self.state('zoomed')
        except:
            pass
        self.configure(fg_color=config.COLORS["bg"])

        self.api = API_Client(config.BASE_URL, config.API_KEY)
        self.all_links = [] 

        self.setup_header()
        
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=config.COLORS["primary"])
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_liste = self.tabview.add("Liste des Liens")
        self.tab_supervision = self.tabview.add("Supervision")

        self.setup_tab_liste()
        self.setup_tab_supervision()
        self.auto_refresh_monitoring()
    
    def load_icon_with_ratio(self, filename, width_wanted=35):
        """Charge une image PNG et la redimensionne en gardant les proportions"""
        basedir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(basedir, filename)
        
        pil_img = Image.open(path)
        
        # Ton fameux calcul de ratio
        ratio = pil_img.height / pil_img.width
        height_calculated = int(width_wanted * ratio)
        
        # Redimensionnement de haute qualité (LANCZOS empêche que ça pixelise)
        img_resized = pil_img.resize((width_wanted, height_calculated), Image.Resampling.LANCZOS)
        
        return ImageTk.PhotoImage(img_resized)

    def setup_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")
        try:
            basedir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(basedir, config.LOGO_FILENAME) 
            pil_img = Image.open(logo_path)
            ratio = pil_img.height / pil_img.width
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(config.LOGO_WIDTH, int(config.LOGO_WIDTH * ratio)))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 20))
        except Exception as e:
            print(f"Erreur logo : {e}")

    # ==========================================
    # ONGLET 1 : LISTE DES LIENS (Inchangé)
    # ==========================================
    def setup_tab_liste(self):
        self.ctrl_frame = ctk.CTkFrame(self.tab_liste, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(self.ctrl_frame, placeholder_text="Rechercher...", width=350, height=35)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_links)

        self.btn_load = ctk.CTkButton(self.ctrl_frame, text="CHARGER API", fg_color=config.COLORS["primary"], command=self.load_links)
        self.btn_load.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(self.ctrl_frame, text="EXPORTER CSV", fg_color="#27ae60", hover_color="#1e8449", command=self.export_to_csv)
        self.btn_export.pack(side="left", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_liste, fg_color="transparent")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def load_links(self):
        try:
            self.all_links = self.api.get_links()
            self.display_links(self.all_links)
        except Exception as e:
            self.show_message(f"Erreur : {e}")

    def display_links(self, links_to_show):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        for link in links_to_show:
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLORS["card"], border_width=1, border_color=config.COLORS["border"])
            card.pack(fill="x", padx=10, pady=5)

            info = f"{link.get('client_name')}\n{link.get('link_code')} | {link.get('techno_name')}"
            ctk.CTkLabel(card, text=info, font=("Arial", 13, "bold"), justify="left").pack(side="left", padx=15, pady=10)

            status = link.get('status_admin')
            color = config.COLORS["accent"] if status == "Livré" else "#f1c40f"
            ctk.CTkLabel(card, text=f"● {status}", text_color=color).pack(side="left", padx=20)

            ctk.CTkButton(card, text="SUPERVISER", width=100, fg_color=config.COLORS["primary"],
                          command=lambda l=link: self.go_to_monitoring(l)).pack(side="right", padx=15)

    def filter_links(self, event=None):
        query = self.search_entry.get().lower()
        filtered = [l for l in self.all_links if query in str(l).lower()]
        self.display_links(filtered)

    def export_to_csv(self):
        if not self.all_links:
            messagebox.showwarning("Export", "Veuillez d'abord charger la liste.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["Client", "Code Lien", "Adresse", "Techno", "Débit", "Statut Admin", "Référence Partenaire"])
                for link in self.all_links:
                    writer.writerow([link.get('client_name'), link.get('link_code'), link.get('address'), link.get('techno_name'), link.get('bandwidth_display'), link.get('status_admin'), link.get('reference_partner')])

    # ==========================================
    # ONGLET 2 : SUPERVISION & CARTE
    # ==========================================
    def setup_tab_supervision(self):
        try:
            self.img_pin_ok = self.load_icon_with_ratio("green_pin.png", width_wanted=35)
            self.img_pin_error = self.load_icon_with_ratio("red_pin.png", width_wanted=35)
        except Exception as e:
            print(f"Alerte : Icônes non trouvées ({e}). La carte utilisera les marqueurs par défaut.")
            self.img_pin_ok = None
            self.img_pin_error = None

        # Panneau de gauche (Infos)
        self.info_panel = ctk.CTkFrame(self.tab_supervision, width=300, fg_color="transparent")
        self.info_panel.pack(side="left", fill="y", padx=20, pady=20)

        self.label_client = ctk.CTkLabel(self.info_panel, text="Sélectionnez un lien", font=("Arial", 16, "bold"), wraplength=250)
        self.label_client.pack(pady=20)
        self.label_address = ctk.CTkLabel(self.info_panel, text="", font=("Arial", 12), wraplength=250)
        self.label_address.pack(pady=10)
        self.label_status = ctk.CTkLabel(self.info_panel, text="-", font=("Arial", 30, "bold"))
        self.label_status.pack(pady=30)
        self.btn_mon = ctk.CTkButton(self.info_panel, text="Rafraîchir Statut", fg_color=config.COLORS["primary"], command=self.fetch_monitoring_data)
        self.btn_mon.pack(pady=20)

        # Panneau de droite (Carte)
        self.map_widget = tkintermapview.TkinterMapView(self.tab_supervision, corner_radius=10)
        self.map_widget.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Application du Thème Sombre (CartoDB Dark Matter)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png")
        self.map_widget.set_position(48.8566, 2.3522) # Paris par défaut

    def go_to_monitoring(self, link):
        self.tabview.set("Supervision")
        self.label_client.configure(text=f"Client : {link.get('client_name')}")
        self.label_address.configure(text=f"Adresse : {link.get('address')}")
        self.label_status.configure(text="Chargement...", text_color=config.COLORS["text"])
        self.fetch_monitoring_data()

    def fetch_monitoring_data(self):
        try:
            lien = self.api.get_monitoring_data()
            
            if lien.get('address'):
                self.label_address.configure(text=f"Adresse : {lien.get('address')}")
            
            # Analyse du statut
            status = str(lien.get('status_display', 'inconnu')).lower()
            is_ok = (status == 'ok')
            color = config.COLORS["accent"] if is_ok else config.COLORS["error"]
            
            self.label_status.configure(text=f"STATUT : {status.upper()}", text_color=color)
            
            # --- CORRECTION : Récupération des coordonnées ---
            lat = lien.get('lat')
            lng = lien.get('lng')
            
            if lat and lng:
                # 1. On efface les anciens marqueurs
                self.map_widget.delete_all_marker()
                
                # 2. On centre la carte
                self.map_widget.set_position(lat, lng)
                
                # 3. On place le marqueur
                icone = self.img_pin_ok if is_ok else self.img_pin_error
                
                # Sécurité : si l'image n'a pas chargé, on remet le marqueur par défaut
                # 3. On place le marqueur avec le texte en blanc
                if icone:
                    self.map_widget.set_marker(
                        lat, lng, 
                        text=f"État : {status.upper()}", 
                        icon=icone,
                        text_color=config.COLORS["text"] # <-- Ajout ici (Force le blanc)
                    )
                else:
                    self.map_widget.set_marker(
                        lat, lng, 
                        text=f"État : {status.upper()}", 
                        marker_color_circle=color, 
                        marker_color_outside=color,
                        text_color=config.COLORS["text"] # <-- Et ici aussi
                    )
                self.map_widget.set_zoom(13)
                
        except Exception as e:
            self.label_status.configure(text="Erreur Supervision", text_color="red")
            print(f"Erreur API Monitoring : {e}")

    def auto_refresh_monitoring(self):
        if self.label_address.cget("text") != "":
            self.fetch_monitoring_data()
        self.after(60000, self.auto_refresh_monitoring)

    def show_message(self, msg):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.scroll_frame, text=msg).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()