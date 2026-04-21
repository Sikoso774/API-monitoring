import os
from dotenv import load_dotenv

# Chargement du fichier .env
load_dotenv()

# --- CONFIGURATION API ---
BASE_URL = "https://kissapi.kissgroup.io/kisslink"
API_KEY = os.getenv("KISSGROUP_API_KEY")

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

# --- RÉGLAGES LOGO ---
LOGO_FILENAME = "logo-noxia.png"
LOGO_WIDTH = 400