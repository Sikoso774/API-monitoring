"""Module de configuration globale de l'application Noxia.

Gère le chargement des variables d'environnement, les chemins absolus,
le chargement des polices, et définit la charte graphique de l'UI.
"""

import sys
from typing import Any, Dict
from pathlib import Path
import keyring
import customtkinter as ctk
from pydantic import Field, field_validator
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
    Intègre également la récupération sécurisée depuis le trousseau Windows.

    Attributes:
        BASE_URL (str): URL de l'API Noxia (forcée en HTTPS).
        API_KEY (str): Clé d'API secrète de KissGroup.
    """
    
    BASE_URL: str = Field(validation_alias="BASE_URL")
    API_KEY: str = Field(default="", validation_alias="KISSGROUP_API_KEY")

    @field_validator('API_KEY', mode='before')
    @classmethod
    def get_from_keyring(cls, v: Any) -> str:
        """Récupère la clé API depuis le keyring système si disponible.
        
        Args:
            v: Valeur initiale (provenant de l'env ou du .env).
        
        Returns:
            str: La clé API trouvée dans le keyring ou la valeur initiale.
        """
        # On priorité le coffre-fort système (Windows Credential Manager)
        secret = keyring.get_password("NoxiaDashboard", "API_KEY")
        if secret:
            return secret
        # Sinon on utilise la valeur du .env ou de la variable d'environnement
        return str(v) if v else ""
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
        # Priorise le fichier .env sur les variables système
        env_priority=1
    )

    @field_validator('BASE_URL')
    @classmethod
    def enforce_https(cls, v: str) -> str:
        """Assure que l'URL de base utilise le protocole HTTPS.
        
        Args:
            v: L'URL fournie dans la configuration.
            
        Returns:
            str: L'URL validée et éventuellement corrigée.
            
        Raises:
            ValueError: Si l'URL n'est pas sécurisée et ne peut être corrigée.
        """
        # 1. Si l'URL commence par http://, on la corrige silencieusement
        if v.startswith('http://'):
            print("🛡️ Auto-correction de l'URL HTTP vers HTTPS.")
            v = v.replace('http://', 'https://')
            
        # 2. Si après correction ce n'est pas sécurisé
        if not v.startswith('https://'):
            raise ValueError("🛡️ SÉCURITÉ CRITIQUE : La BASE_URL doit obligatoirement utiliser HTTPS.")
            
        return v


# Instanciation globale des paramètres métier
try:
    settings = Settings()
except Exception as err:
    print(f"ERREUR instanciation de Settings : {err}")


# --- CHARGEMENT DES POLICES EMBARQUÉES ---
try:
    # On charge les fichiers .ttf directement dans la mémoire de CustomTkinter
    ctk.FontManager.load_font(str(FONTS_DIR / "Montserrat-Regular.ttf"))
    ctk.FontManager.load_font(str(FONTS_DIR / "Montserrat-Bold.ttf"))
    print("✅ Polices Montserrat chargées avec succès.")
except Exception as err:
    print(f"⚠️ Impossible de charger les polices : {err}")


# --- CHARTE GRAPHIQUE NOXIA SECURITY (Version Pro) ---
COLORS: Dict[str, str] = {
    "bg": "#000726",          # Fond le plus sombre (Graphiste)
    "card": "#002359",        # Bleu intermédiaire (Graphiste)
    "card_alt": "#01346b",    # Intermédiaire pour le survol
    
    # Couleurs principales unifiées pour les boutons
    "primary": "#0251a1",     # Bleu clair (Graphiste)
    "primary_hover": "#014282",
    "accent": "#2e7d32",      # Vert succès/validation moins clinquant
    "accent_hover": "#1b5e20",
    
    "error": "#d32f2f",       # Rouge alerte atténué
    "text": "#ffffff",        # Blanc pur
    "text_sub": "#b1b9c0",    # Gris clair (Graphiste)
    "border": "#0251a1",      # Bordures complémentaires (Graphiste)
    "scroll_button": "#002359",
    "scroll_hover": "#0251a1"
}

# Polices globales
FONTS: Dict[str, Any] = {
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