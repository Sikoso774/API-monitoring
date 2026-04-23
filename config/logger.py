import logging
import os
from logging.handlers import RotatingFileHandler

# On détermine le chemin du dossier logs à la racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Création automatique du dossier logs s'il n'existe pas
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "noxia_dashboard.log")

def setup_logger(name):
    """Configure et retourne un logger personnalisé"""
    logger = logging.getLogger(name)
    
    # On évite d'ajouter plusieurs fois les mêmes handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Format professionnel : Date - Nom du module - Niveau - Message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 1. Handler pour le FICHIER (Rotation : 2 Mo max, garde les 5 derniers fichiers)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=5, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO) # On ne log que l'important dans le fichier

        # 2. Handler pour la CONSOLE
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG) # On log tout dans la console pour le debug

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Désactiver la propagation vers le logger racine pour éviter les doublons
        logger.propagate = False

    return logger