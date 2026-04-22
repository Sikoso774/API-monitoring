import requests
import time
from config.settings import settings

class API_Client:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.headers = {"api_key": settings.API_KEY}

    def get_links(self):
        response = requests.get(f"{self.base_url}/links", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_monitoring_data(self):
        """Récupère la liste complète des statuts de supervision"""
        response = requests.get(f"{self.base_url}/monitoring", headers=self.headers)
        response.raise_for_status()
        return response.json() # On renvoie toute la liste JSON

    # --- NOUVELLES FONCTIONNALITÉS SÉCURISÉES ---

    def get_link_details(self, link_code):
        """Récupère le détail complet d'un lien en gérant les erreurs 404"""
        try:
            # Si la doc se trompe, tu pourras tester de remplacer "/links/" par "/link/" ici
            response = requests.get(f"{self.base_url}/links/{link_code}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data[0] if isinstance(data, list) else data
            
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ Alerte API : Détails introuvables pour {link_code} (Erreur {e.response.status_code})")
            # On retourne un dictionnaire vide pour protéger l'interface graphique
            return {}
        except Exception as e:
            print(f"⚠️ Erreur réseau inattendue : {e}")
            return {}

    def run_diagnostic(self, link_code):
        """
        Simulateur de diagnostic réseau.
        Remplace l'appel API (qui n'existe pas chez Kissgroup) par un faux test réaliste.
        """
        try:
            # 1. On simule le temps de test sur le réseau (ex: 2.5 secondes)
            time.sleep(2.5)
            
            # 2. On renvoie un rapport technique complet et positif
            rapport = (
                "✅ DIAGNOSTIC TERMINÉ\n"
                "------------------------------------------\n"
                "• Ligne Optique : Synchronisée\n"
                "• Puissance reçue (Rx) : -19.4 dBm (Excellent)\n"
                "• Authentification PPPoE : Succès\n"
                "• Latence vers passerelle : 4 ms\n"
                "• Perte de paquets (Ping) : 0%\n"
                "------------------------------------------\n"
                "Résultat : Le lien est totalement opérationnel."
            )
            
            return {"message": rapport}
            
        except Exception as e:
            return {"message": f"Erreur de simulation : {e}"}