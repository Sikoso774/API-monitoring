import os
import customtkinter as ctk
from PIL import Image

from config.settings import settings, COLORS, ASSETS_DIR, LOGO_FILENAME, LOGO_WIDTH
from ui.tab_list import TabListe
from ui.tab_supervision import TabSupervision
from services.api_client import API_Client

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Noxia Security - Dashboard")
        self.configure(fg_color=COLORS["bg"])
        
        # Fenêtre responsive
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.85)}x{int(screen_height * 0.85)}")
        self.minsize(900, 600)
        try:
            self.state('zoomed')
        except: pass

        # Services
        self.api = API_Client()

        # UI
        self.setup_header()
        
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=COLORS["primary"])
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_liste_frame = self.tabview.add("Liste des Liens")
        self.tab_supervision_frame = self.tabview.add("Supervision")

        # Initialisation des onglets séparés
        self.tab_supervision = TabSupervision(self.tab_supervision_frame, self.api)
        self.tab_liste = TabListe(self.tab_liste_frame, self.api, self.go_to_monitoring)

    def setup_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")
        try:
            logo_path = os.path.join(ASSETS_DIR, LOGO_FILENAME) 
            pil_img = Image.open(logo_path)
            ratio = pil_img.height / pil_img.width
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(LOGO_WIDTH, int(LOGO_WIDTH * ratio)))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 20))
        except Exception as e:
            print(f"Erreur logo : {e}")

    def go_to_monitoring(self, link):
        """Fonction callback appelée depuis l'onglet Liste"""
        self.tabview.set("Supervision")
        self.tab_supervision.load_client(link)