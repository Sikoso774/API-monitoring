"""Module principal de l'application Noxia Security Dashboard.

Ce module contient la classe principale de l'interface graphique (App),
qui hérite de customtkinter.CTk et gère la navigation entre les différents
onglets (Liste des Liens, Supervision).
"""

import os
from typing import Dict, Any
import customtkinter as ctk
from PIL import Image

# Imports explicites pour respecter la PEP8 (au lieu de import *)
from config.settings import COLORS, FONTS, ASSETS_DIR, LOGO_FILENAME, LOGO_WIDTH
from ui.tab_list import TabListe
from ui.tab_supervision import TabSupervision
from services.api_client import API_Client


class App(ctk.CTk):
    """Classe principale de l'application Noxia Security Dashboard.

    Gère l'initialisation de la fenêtre principale, la création des onglets,
    et l'injection des dépendances (API Client).

    Attributes:
        api (API_Client): Instance du client API pour les requêtes réseau.
        tabview (ctk.CTkTabview): Gestionnaire des onglets de l'application.
        tab_liste (TabListe): Onglet affichant la liste des liens.
        tab_supervision (TabSupervision): Onglet affichant la supervision d'un lien.
    """

    def __init__(self) -> None:
        """Initialise la fenêtre principale et configure les composants de l'interface."""
        super().__init__()

        self.title("NOXIA Security - DASHBOARD")
        self.configure(fg_color=COLORS["bg"])

        # Configuration de la fenêtre responsive
        screen_width: int = self.winfo_screenwidth()
        screen_height: int = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.85)}x{int(screen_height * 0.85)}")
        self.minsize(900, 600)
        
        # Tentative d'ouverture de la fenêtre en mode plein écran (maximisé)
        try:
            self.state("zoomed")
        except Exception:
            # Sous certains OS (ex: Linux sans support zoom), on ignore l'erreur
            pass

        # Initialisation des services métier
        self.api = API_Client()

        # Construction de l'interface utilisateur
        self.setup_header()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Configuration du système d'onglets
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg"],
            segmented_button_fg_color=COLORS["card"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_hover_color=COLORS["card_alt"],
        )

        # Rendre la tabview responsive pour occuper tout l'espace disponible
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuration des polices pour la barre de navigation des onglets
        self.tabview._segmented_button.configure(font=FONTS["subtitle"])

        self.tab_liste_frame = self.tabview.add("Liste des Liens")
        self.tab_supervision_frame = self.tabview.add("Supervision")

        # Initialisation et rattachement des onglets séparés
        self.tab_supervision = TabSupervision(self.tab_supervision_frame, self.api)
        self.tab_liste = TabListe(self.tab_liste_frame, self.api, self.go_to_monitoring)

    def setup_header(self) -> None:
        """Configure et affiche l'en-tête de l'application avec le logo."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")
        
        try:
            logo_path: str = os.path.join(ASSETS_DIR, LOGO_FILENAME)
            pil_img = Image.open(logo_path)
            ratio: float = pil_img.height / pil_img.width
            logo_img = ctk.CTkImage(
                light_image=pil_img, 
                dark_image=pil_img, 
                size=(LOGO_WIDTH, int(LOGO_WIDTH * ratio))
            )
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 20))
        except Exception as e:
            # Fallback en cas de logo manquant pour ne pas crasher l'UI
            print(f"Erreur lors du chargement du logo : {e}")

    def go_to_monitoring(self, link: Dict[str, Any]) -> None:
        """Bascule vers l'onglet Supervision et charge les données du lien sélectionné.

        Args:
            link (Dict[str, Any]): Dictionnaire contenant les informations du lien à superviser.
        """
        self.tabview.set("Supervision")
        self.tab_supervision.load_client(link)