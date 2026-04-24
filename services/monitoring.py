"""Module en charge de l'agrégation des données de supervision.

Combine les flux de monitoring global et les détails spécifiques
d'un lien pour produire une vision consolidée et sécurisée.
"""

from typing import Any, Dict, List, Union

from services.api_client import API_Client
from config.logger import setup_logger

# Correction : orthographe de 'MonitoringSrervice'
logger = setup_logger("MonitoringService")


class MonitoringService:
    """Service de traitement des métriques de supervision.

    Attributes:
        api (API_Client): Le client API pour récupérer les données brutes.
    """

    def __init__(self, api_client: API_Client) -> None:
        """Initialise le service de monitoring.

        Args:
            api_client (API_Client): Instance du client API Noxia.
        """
        self.api: API_Client = api_client

    def fetch_comprehensive_data(self, link_code: str) -> Dict[str, Any]:
        """Fusionne monitoring global et détails techniques sans aucun crash.

        Assure une extraction sécurisée des données avec des valeurs par défaut
        pour alimenter la vue Supervision de l'application.

        Args:
            link_code (str): Code unique du lien à inspecter.

        Returns:
            Dict[str, Any]: Un dictionnaire consolidé de toutes les métriques réseau.
        """
        # 1. Infos globales (Statut, GPS)
        try:
            mon_list: Union[List[Dict[str, Any]], Dict[str, Any]] = self.api.get_monitoring_data()
            if not isinstance(mon_list, list):
                mon_list = [mon_list]
                
            mon_data: Dict[str, Any] = next(
                (item for item in mon_list if item.get("id_lien") == link_code), {}
            )
        except Exception as e:
            logger.warning(f"Impossible de récupérer le monitoring global pour {link_code} : {e}")
            mon_data = {}

        # 2. Détails techniques (PPPoE, Equipement, etc.)
        try:
            details: Dict[str, Any] = self.api.get_link_details(link_code) or {}
        except Exception as e:
            # CORRECTION : On vide 'details' et non 'mon_data'
            logger.warning(f"Impossible de récupérer les détails de lien pour {link_code} : {e}")
            details = {}

        # 3. Sécurisation extrême des listes (Évite l'erreur IndexError)
        ppp_logins = details.get("ppp_logins") or []
        first_ppp: Dict[str, Any] = ppp_logins[0] if len(ppp_logins) > 0 else {}

        devices = details.get("devices") or []
        first_device: Dict[str, Any] = devices[0] if len(devices) > 0 else {}

        # 4. Construction et renvoi d'un dictionnaire propre et harmonisé
        return {
            "status": str(mon_data.get("status_display", "inconnu")).upper(),
            "address": mon_data.get("address", ""),
            "lat": mon_data.get("lat"),
            "lng": mon_data.get("lng"),
            
            "ip_publique": first_ppp.get("ip_address", "Non définie"),
            "session_ppp": first_ppp.get("ppp_login", "Aucune"),
            "provider": details.get("provider_name", "Inconnu"),
            "ip_device": first_device.get("ip_device", "Non administrable"),
            "status_tech": first_ppp.get("status_tech", "N/A"),
            "brand": first_device.get("brand", "N/A"),
            "password_device": first_device.get("password_device", "********"),
            
            # Donnée d'atténuation (souvent dans un champ technique de l'API)
            "attenuation": details.get("optical_attenuation", -18.5),
            "last_change_connection_date": mon_data.get(
                "last_change_connection_date", "Inconnue"
            )
        }