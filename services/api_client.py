"""Module responsable des communications HTTP avec l'API métier Noxia.

Ce module encapsule la bibliothèque 'requests' pour fournir des méthodes
de haut niveau permettant de récupérer les liens, le monitoring et les détails.
"""

import time
from typing import Any, Dict, List, Union
import requests

from config.settings import settings
from config.logger import setup_logger

# Initialisation du logger pour ce module spécifique
logger = setup_logger("API_Client")


class API_Client:
    """Client HTTP dédié aux échanges avec l'API Noxia.

    Gère l'authentification via clé d'API et la construction des requêtes GET.

    Attributes:
        base_url (str): URL racine de l'API (issue des configurations).
        headers (Dict[str, str]): En-têtes HTTP incluant la clé d'API.
    """

    def __init__(self):
        # 1. Utilisation d'une Session pour la performance et la sécurité
        self.base_url: str = settings.BASE_URL
        self.session = requests.Session()
        
        # 2. Masquage de l'empreinte (User-Agent)
        # Par défaut, le serveur voit "python-requests/2.31". Un hacker sait donc que c'est un script Python.
        # On va déguiser l'application pour qu'elle ait l'air légitime :
        self.session.headers.update({
            "User-Agent": "NoxiaSecurityDashboard/1.0",
            "Accept": "application/json",
            "api_key": settings.API_KEY
        })
        
        # 3. Timeouts stricts (Anti-DDoS / Anti-Blocage)
        self.timeout = 10  # Si le serveur ne répond pas sous 10s, on coupe tout.
        logger.info("API_Client sécurisé initialisé avec succès")

    def get_links(self) -> List[Dict[str, Any]]:
        """Récupère la liste complète des liens réseau.

        Returns:
            List[Dict[str, Any]]: Une liste de dictionnaires représentant chaque lien.

        Raises:
            requests.exceptions.RequestException: En cas d'erreur de requête HTTP.
        """
        try:
            logger.debug("Tentative de récupération de la liste des liens...")
            response = self.session.get(f"{self.base_url}/links")
            response.raise_for_status()
            links: List[Dict[str, Any]] = response.json()
            logger.info(f"{len(links)} liens récupérés avec succès")
            return links
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des liens : {e}")
            raise

    def get_monitoring_data(self) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Récupère les données de supervision (monitoring) pour l'ensemble des liens.

        Returns:
            Union[List[Dict[str, Any]], Dict[str, Any]]: Les données de supervision reçues, 
            généralement une liste, ou une liste vide en cas d'erreur.
        """
        try:
            logger.debug("Appel API : /monitoring")
            response = self.session.get(
                f"{self.base_url}/monitoring", 
                timeout=self.timeout, 
                verify=True)
            response.raise_for_status()
            data = response.json()
            logger.info("Données de monitoring reçues")
            return data
        except Exception as e:
            logger.error(f"Erreur monitoring : {e}")
            return []

    def get_link_details(self, link_code: str) -> Dict[str, Any]:
        """Récupère les informations techniques détaillées pour un lien spécifique.

        Args:
            link_code (str): Identifiant unique du lien réseau.

        Returns:
            Dict[str, Any]: Un dictionnaire contenant les détails techniques.
            Retourne un dictionnaire vide si le lien est introuvable (404) ou en cas d'erreur.
        """
        try:
            logger.debug(f"Récupération des détails pour le lien : {link_code}")
            response = self.session.get(f"{self.base_url}/links/{link_code}")
            response.raise_for_status()
            logger.info(f"Détails récupérés pour {link_code}")
            return response.json()
        except requests.exceptions.HTTPError:
            logger.warning(f"Lien {link_code} introuvable (404) ou erreur API")
            return {}
        except Exception as e:
            logger.error(f"Erreur réseau sur {link_code} : {e}")
            return {}