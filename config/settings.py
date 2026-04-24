import os
import sys
import customtkinter as ctk
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

BASE_DIR = get_base_path()
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
IMG_DIR = ASSETS_DIR / "img"  # <--- On définit le nouveau dossier ici

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

BASE_DIR = get_base_path()
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # On utilise Field pour être explicite et permettre des valeurs par défaut si besoin
    BASE_URL: str = Field(validation_alias="BASE_URL")
    API_KEY: str = Field(validation_alias="KISSGROUP_API_KEY")

    model_config = SettingsConfigDict(
            env_file=str(ENV_PATH),
            env_file_encoding='utf-8',
            extra='ignore',
            # On dit à Pydantic de prioriser le fichier .env sur les variables système
            env_priority=1 
        )


# Instanciation globale
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

# --- CHARTE GRAPHIQUE NOXIA SECURITY ---
COLORS = {
    "bg": "#121212",
    "card": "#1E1E1E",
    "primary": "#007ACC",
    "accent": "#00CC66",
    "error": "#FF4444",
    "text": "#FFFFFF",
    "border": "#3d3d3d"
}

FONTS = {
    "title": ("Montserrat", 16, "bold"),
    "body": ("Montserrat", 12),
    "small": ("Montserrat", 11),
    "small_bold": ("Montserrat", 11, "bold"),
    "status": ("Montserrat", 30, "bold")
}

# --- RÉGLAGES ASSETS ---
# ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
LOGO_FILENAME = IMG_DIR / "logo-noxia.png"
LOGO_WIDTH = 400