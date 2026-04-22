from services.api_client import API_Client

class MonitoringService:
    def __init__(self, api_client: API_Client):
        self.api = api_client

    def fetch_comprehensive_data(self, link_code):
        """Fusionne monitoring + détails sans AUCUN crash possible"""
        # 1. Infos globales (Statut, GPS)
        try:
            mon_list = self.api.get_monitoring_data()
            if not isinstance(mon_list, list): mon_list = [mon_list]
            mon_data = next((item for item in mon_list if item.get("id_lien") == link_code), {})
        except Exception:
            mon_data = {}
            
        # 2. Détails techniques (PPPoE, etc.)
        try:
            details = self.api.get_link_details(link_code) or {}
        except Exception:
            details = {}
        
        # 3. Sécurisation extrême des listes (Évite l'erreur de l'index 0)
        ppp_logins = details.get("ppp_logins") or []
        first_ppp = ppp_logins[0] if len(ppp_logins) > 0 else {}
        
        devices = details.get("devices") or []
        first_device = devices[0] if len(devices) > 0 else {}
        
        # 4. On renvoie un dictionnaire propre
        return {
            "status": str(mon_data.get("status_display", "inconnu")).upper(),
            "address": mon_data.get("address", ""),
            "lat": mon_data.get("lat"),
            "lng": mon_data.get("lng"),
                        
            "ip_publique": first_ppp.get("ip_address", "Non définie"),
            "session_ppp": first_ppp.get("ppp_login", "Aucune"),
            "provider": details.get("provider_name", "Inconnu"),
            "ip_device": first_device.get("ip_device", "Non administrable"),
            "status_tech": first_ppp.get("status_tech", "N/A"), #
            "brand": first_device.get("brand", "N/A"), #
            "password_device": first_device.get("password_device", "********"), #
            
            # Donnée d'atténuation (souvent dans un champ technique de l'API)
            "attenuation": details.get("optical_attenuation", -18.5), # Valeur de test
            "last_change_connection_date": mon_data.get("last_change_connection_date", "Inconnue")
        }