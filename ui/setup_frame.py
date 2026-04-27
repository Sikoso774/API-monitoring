import os
from typing import Any
from PIL import Image
import customtkinter as ctk
import keyring
from config.settings import COLORS, FONTS, ASSETS_DIR, LOGO_FILENAME, LOGO_WIDTH

class SetupFrame(ctk.CTkFrame):
    """Vue de configuration initiale sécurisée avec un design premium.
    
    Cette classe gère l'affichage du formulaire de saisie de la clé API,
    son enregistrement sécurisé via keyring, et notifie le parent en cas de succès.
    
    Attributes:
        on_success (callable): Fonction de rappel après enregistrement réussi.
    """
    
    def __init__(self, master: Any, on_success: callable, **kwargs: Any) -> None:
        """Initialise le cadre de configuration.
        
        Args:
            master: Le widget parent (généralement App).
            on_success: Callback appelé avec la clé API une fois sauvegardée.
            **kwargs: Arguments supplémentaires pour CTkFrame.
        """
        super().__init__(master, fg_color=COLORS["bg"], **kwargs)
        self.on_success = on_success
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construit l'interface graphique avec le logo et la carte de saisie."""
        # Conteneur principal centré pour tout le contenu (Logo + Carte)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")

        # 1. Logo
        self._load_logo(self.main_container)

        # 2. Conteneur Central (Style Carte)
        self.card = ctk.CTkFrame(self.main_container, fg_color=COLORS["card"], corner_radius=15)
        self.card.pack(pady=20, padx=20)

        # Titre avec icône
        ctk.CTkLabel(
            self.card, 
            text="🔐 CONFIGURATION SÉCURISÉE", 
            font=FONTS["title"],
            text_color=COLORS["primary"]
        ).pack(pady=(30, 10), padx=60)
        
        ctk.CTkLabel(
            self.card, 
            text="Veuillez saisir votre clé API KissGroup :", 
            font=FONTS["body"],
            text_color=COLORS["text_sub"]
        ).pack(pady=(0, 25))
        
        # Champ de saisie stylisé
        self.api_key_entry = ctk.CTkEntry(
            self.card, 
            width=350, 
            height=45,
            placeholder_text="Clé API...", 
            show="*",
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            font=FONTS["body"]
        )
        self.api_key_entry.pack(pady=10, padx=40)
        
        # Liaison de la touche Entrée
        self.api_key_entry.bind("<Return>", lambda e: self._on_enter_press())

        # Bouton d'enregistrement avec bordure (Style Dashboard)
        self.save_btn = ctk.CTkButton(
            self.card, 
            text="ENREGISTRER DANS LE SYSTÈME", 
            font=FONTS["button"],
            width=250,
            height=45,
            command=self._save_key,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            border_width=1,
            border_color=COLORS["primary"]
        )
        self.save_btn.pack(pady=(20, 30))

        # Zone d'information (Feedback)
        self.info_label = ctk.CTkLabel(self.card, text="", font=FONTS["small"])
        self.info_label.pack(pady=(0, 20))

    def _load_logo(self, parent: ctk.CTkFrame) -> None:
        """Charge le logo Noxia avec le bon ratio.
        
        Args:
            parent: Le widget parent où placer le logo.
        """
        try:
            path = os.path.join(ASSETS_DIR, LOGO_FILENAME)
            pil_img = Image.open(path)
            ratio = pil_img.height / pil_img.width
            logo_img = ctk.CTkImage(
                light_image=pil_img, 
                dark_image=pil_img, 
                size=(LOGO_WIDTH, int(LOGO_WIDTH * ratio))
            )
            logo_label = ctk.CTkLabel(parent, image=logo_img, text="")
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Logo error: {e}")

    def _on_enter_press(self) -> None:
        """Gère l'événement d'appui sur la touche Entrée."""
        # Effet visuel de "clignotement" sur le bouton
        original_color = self.save_btn.cget("fg_color")
        self.save_btn.configure(fg_color=COLORS["primary_hover"])
        self.after(100, lambda: self.save_btn.configure(fg_color=original_color))
        
        # Lancement de la sauvegarde
        self._save_key()

    def _save_key(self) -> None:
        """Valide la saisie et enregistre la clé dans le coffre-fort système."""
        key = self.api_key_entry.get().strip()
        if not key:
            self.info_label.configure(text="❌ Veuillez saisir une clé", text_color=COLORS["error"])
            return

        try:
            keyring.set_password("NoxiaDashboard", "API_KEY", key)
            self.info_label.configure(text="✅ Clé sécurisée avec succès", text_color=COLORS["accent"])
            self.after(800, lambda: self.on_success(key))
        except Exception as e:
            self.info_label.configure(text=f"❌ Erreur : {e}", text_color=COLORS["error"])