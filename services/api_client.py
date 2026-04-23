import requests
import time
from config.settings import settings
from config.logger import setup_logger # Import de notre nouveau système

# On initialise le logger pour ce module spécifique
logger = setup_logger("API_Client")

class API_Client:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.headers = {"api_key": settings.API_KEY}
        logger.info("API_Client initialisé avec succès")

    def get_links(self):
        try:
            logger.debug("Tentative de récupération de la liste des liens...")
            response = requests.get(f"{self.base_url}/links", headers=self.headers)
            response.raise_for_status()
            links = response.json()
            logger.info(f"{len(links)} liens récupérés avec succès")
            return links
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des liens : {e}")
            raise

    def get_monitoring_data(self):
        try:
            logger.debug("Appel API : /monitoring")
            response = requests.get(f"{self.base_url}/monitoring", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            logger.info("Données de monitoring reçues")
            return data
        except Exception as e:
            logger.error(f"Erreur monitoring : {e}")
            return []

    def get_link_details(self, link_code):
        try:
            logger.debug(f"Récupération des détails pour le lien : {link_code}")
            response = requests.get(f"{self.base_url}/links/{link_code}", headers=self.headers)
            response.raise_for_status()
            logger.info(f"Détails récupérés pour {link_code}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Lien {link_code} introuvable (404) ou erreur API")
            return {}
        except Exception as e:
            logger.error(f"Erreur réseau sur {link_code} : {e}")
            return {}

    def run_diagnostic(self, link_code):
        # On garde notre simulateur mais on logge l'action
        logger.info(f"Démarrage du diagnostic simulé pour {link_code}")
        time.sleep(2)
        logger.debug("Simulation de l'analyse des paquets terminée")
        return {"message": "✅ Diagnostic (Simulé) : Tout est OK."}