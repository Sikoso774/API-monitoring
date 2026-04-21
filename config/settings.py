import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_URL: str = "https://kissapi.kissgroup.io/kisslink"
    
    # On précise à Pydantic le nom exact de la variable dans le fichier .env
    API_KEY: str = Field(validation_alias="KISSGROUP_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instanciation globale
settings = Settings()

# --- CHARTE GRAPHIQUE NOXIA SECURITY ---
COLORS = {
    "bg": "#121212",
    "card": "#2b2b2b",
    "primary": "#1f538d",
    "accent": "#2ecc71",
    "error": "#e74c3c",
    "text": "#ffffff",
    "border": "#3d3d3d"
}

# --- RÉGLAGES ASSETS ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
LOGO_FILENAME = "logo-noxia.png"
LOGO_WIDTH = 400