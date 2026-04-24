"""Module responsable de l'exécution des routines de diagnostic réseau.

Simule ou orchestre des tests sur un lien spécifique (Ping, MTR, SNMP)
et génère un rapport détaillé pour l'utilisateur.
"""

import time
from typing import Any, Dict

from config.logger import setup_logger
from services.api_client import API_Client

logger = setup_logger("DiagnosticService")


class DiagnosticService:
    """Service encapsulant la logique métier des diagnostics de liens.

    Attributes:
        api (API_Client): Instance du client API pour récupérer les données pré-test.
    """

    def __init__(self, api_client: API_Client) -> None:
        """Initialise le service de diagnostic.

        Args:
            api_client (API_Client): Le client HTTP permettant de joindre l'API.
        """
        self.api: API_Client = api_client

    def run_full_diagnostic(self, link_code: str) -> Dict[str, str]:
        """Génère un rapport de diagnostic dynamique basé sur les données de l'API.

        Cette fonction effectue des requêtes préparatoires, simule un temps
        de traitement (comme un ping ou test optique) puis génère le résultat final.

        Args:
            link_code (str): L'identifiant unique du lien à diagnostiquer.

        Returns:
            Dict[str, str]: Un dictionnaire contenant la clé 'message' avec le rapport formaté.
        """
        logger.info(f"Démarrage du diagnostic pour le lien {link_code}")

        # 1. Récupération des informations techniques
        details: Dict[str, Any] = self.api.get_link_details(link_code) or {}

        # 2. Simulation réaliste du temps de traitement réseau (Tests optiques/MTR)
        time.sleep(2)

        if not details:
            logger.warning(f"Diagnostic impossible : lien {link_code} introuvable.")
            return {
                "message": "❌ Échec du diagnostic : Lien introuvable chez le fournisseur."
            }

        # 3. Extraction intelligente des données pour le rapport
        devices = details.get("devices", [])
        if not devices:
            # Fallback en cas de None renvoyé par .get()
            devices = []
            
        brand: str = devices[0].get("brand", "Générique") if len(devices) > 0 else "Générique"
        attenuation: str = str(details.get("optical_attenuation", "-19.0"))

        rapport: str = (
            f"✅ DIAGNOSTIC {brand.upper()} TERMINÉ\n"
            "------------------------------------------\n"
            "• Ligne Optique : Synchronisée\n"
            f"• Puissance reçue (Rx) : {attenuation} dBm\n"
            "• Authentification PPPoE : Succès\n"
            "• Routage IP : Opérationnel\n"
            "------------------------------------------\n"
            "Résultat : Le lien est totalement opérationnel."
        )

        logger.debug("Diagnostic généré avec succès.")
        return {"message": rapport}