"""Module responsable de l'affichage géographique des liens réseau.

Intègre la bibliothèque tkintermapview pour rendre une carte interactive,
positionner des pins de statut et gérer le zoom.
"""

import os
import logging
from typing import Any, Optional

import tkintermapview
import customtkinter as ctk
from PIL import Image, ImageTk

from config.settings import COLORS, IMG_DIR, FONTS

logger = logging.getLogger(__name__)


class MapView(ctk.CTkFrame):
    """Composant encapsulant une carte géographique interactive.

    Attributes:
        img_ok (Optional[ImageTk.PhotoImage]): Icône chargée pour un état normal.
        img_err (Optional[ImageTk.PhotoImage]): Icône chargée pour un état d'erreur.
        map_widget (tkintermapview.TkinterMapView): Le composant carte sous-jacent.
    """

    def __init__(self, master: Any, **kwargs: Any) -> None:
        """Initialise la vue carte et charge les ressources d'icônes.

        Args:
            master (Any): Widget parent.
            **kwargs (Any): Arguments supplémentaires passés au CTkFrame.
        """
        super().__init__(master, fg_color="transparent", **kwargs)

        # Chargement des icônes de localisation
        self.img_ok: Optional[ImageTk.PhotoImage] = self._load_pin("green_pin.png")
        self.img_err: Optional[ImageTk.PhotoImage] = self._load_pin("red_pin.png")

        # Configuration du widget Carte
        self.map_widget = tkintermapview.TkinterMapView(self, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        
        # Thème de carte sombre (CartoCDN Dark Matter)
        self.map_widget.set_tile_server(
            "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
        )
        # Positionnement par défaut sur Paris
        self.map_widget.set_position(48.8566, 2.3522)

    def _load_pin(self, filename: str) -> Optional[ImageTk.PhotoImage]:
        """Charge et redimensionne une icône de marqueur depuis le dossier des ressources.

        Args:
            filename (str): Nom du fichier image (ex: 'green_pin.png').

        Returns:
            Optional[ImageTk.PhotoImage]: L'image compatible Tkinter, ou None si échec.
        """
        try:
            path: str = os.path.join(IMG_DIR, filename)
            pil_img = Image.open(path)
            # Redimensionnement forcé pour l'homogénéité des icônes
            img_resized = pil_img.resize((35, 45), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img_resized)
        except Exception as e:
            logger.warning(f"Impossible de charger l'icône {filename} : {e}")
            return None

    def update_marker(
        self, lat: Optional[float], lng: Optional[float], status: str
    ) -> None:
        """Met à jour le marqueur actif sur la carte en fonction des coordonnées.

        Args:
            lat (Optional[float]): Latitude du point d'installation.
            lng (Optional[float]): Longitude du point d'installation.
            status (str): État du lien (ex: 'OK', 'KO', 'DOWN').
        """
        # Si les coordonnées sont invalides ou manquantes, on abandonne
        if not lat or not lng:
            return

        # Nettoyage des anciens points
        self.map_widget.delete_all_marker()
        
        # Centrage de la caméra
        self.map_widget.set_position(lat, lng)

        # Choix de l'icône selon l'état de la connexion
        is_ok: bool = (status.strip().upper() == "OK")
        icon: Optional[ImageTk.PhotoImage] = self.img_ok if is_ok else self.img_err

        # Placement du nouveau marqueur
        self.map_widget.set_marker(
            lat,
            lng,
            text=f"État : {status}",
            icon=icon,
            text_color=COLORS["text"],
            font=FONTS["small"]
        )
        self.map_widget.set_zoom(14)