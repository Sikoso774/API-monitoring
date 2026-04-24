"""Module de configuration globale de l'application Noxia.

Gère le chargement des variables d'environnement, les chemins absolus,
le chargement des polices, et définit la charte graphique de l'UI.
"""

import sys
from pathlib import Path
import customtkinter as ctk
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_base_path() -> Path:
    """Détermine le chemin racine absolu du projet.

    Gère la différence entre l'exécution via script Python classique 
    et l'exécution via un binaire compilé (PyInstaller/Nuitka).

    Returns:
        Path: L'objet Path pointant vers le dossier racine.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


# --- CONFIGURATION DES CHEMINS ---
BASE_DIR: Path = get_base_path()
ASSETS_DIR: Path = BASE_DIR / "assets"
FONTS_DIR: Path = ASSETS_DIR / "fonts"
IMG_DIR: Path = ASSETS_DIR / "img"
ENV_PATH: Path = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Classe de gestion des variables d'environnement via Pydantic.

    Lit les valeurs depuis le fichier .env ou les variables système.

    Attributes:
        BASE_URL (str): URL de l'API Noxia.
        API_KEY (str): Clé d'API secrète de KissGroup.
    """
    BASE_URL: str = Field(validation_alias="BASE_URL")
    API_KEY: str = Field(validation_alias="KISSGROUP_API_KEY")

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
        # Priorise le fichier .env sur les variables système
        env_priority=1
    )


# Instanciation globale des paramètres métier
try:
    settings = Settings()
except Exception as e:
    print(f"ERREUR instanciation de Settings : {e}")


# --- CHARGEMENT DES POLICES EMBARQUÉES ---
try:
    # On charge les fichiers .ttf directement dans la mémoire de CustomTkinter
    ctk.FontManager.load_font(str(FONTS_DIR / "Montserrat-Regular.ttf"))
    ctk.FontManager.load_font(str(FONTS_DIR / "Montserrat-Bold.ttf"))
    print("✅ Polices Montserrat chargées avec succès.")
except Exception as e:
    print(f"⚠️ Impossible de charger les polices : {e}")


# --- CHARTE GRAPHIQUE NOXIA SECURITY (Version Pro) ---
COLORS = {
    "bg": "#0d1b2e",          # Bleu nuit profond
    "bg_darker": "#081220",   # Pour les zones très sombres
    "card": "#1a2a3f",        # Bleu acier
    "card_alt": "#1e3a5f",    # Variantes de cartes
    "primary": "#2a7fc1",     # Bleu bouton
    "primary_hover": "#1f538d",
    "secondary": "#27ae60",
    "secondary_hover": "#1e8449",
    "accent": "#1a9b6e",      # Émeraude Noxia
    "accent_hover": "#22c78a",
    "error": "#e74c3c",       # Rouge alerte
    "text": "#ffffff",        # Blanc pur
    "text_sub": "#a0aec0",    # Gris bleuté secondaire
    "border": "#2d4a6b",      # Bordures discrètes
    "scroll_button": "#2d4a6b",
    "scroll_hover": "#2a7fc1"
}

# Polices globales
FONTS = {
    "title": ("Montserrat", 18, "bold"),
    "subtitle": ("Montserrat", 14, "bold"),
    "body": ("Montserrat", 12),
    "button": ("Montserrat", 13),
    "small": ("Montserrat", 11),
    "status": ("Montserrat", 32, "bold")
}

# Paramètres du logo
LOGO_FILENAME: str = "img/logo-noxia.png"
LOGO_WIDTH: int = 400