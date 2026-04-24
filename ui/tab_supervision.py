"""Module gérant l'onglet 'Supervision'.

Cet onglet permet de visualiser les détails d'un lien sélectionné,
d'afficher sa position sur une carte et de lancer des diagnostics réseau
en tâche de fond.
"""

import threading
import logging
from typing import Dict, Any
import customtkinter as ctk

from ui.supervision.info_sidebar import InfoSidebar
from ui.supervision.map_view import MapView
from services.monitoring import MonitoringService
from services.diagnostic import DiagnosticService
from services.api_client import API_Client

logger = logging.getLogger(__name__)


class TabSupervision:
    """Classe représentant l'onglet de Supervision d'un lien spécifique.

    Gère le rafraîchissement asynchrone des données et l'exécution
    des diagnostics sans bloquer l'interface graphique.

    Attributes:
        parent (ctk.CTkFrame): Le widget parent contenant cet onglet.
        api (API_Client): Le client API injecté pour les requêtes.
        diag (DiagnosticService): Service pour l'exécution des tests.
        mon_service (MonitoringService): Service pour récupérer les métriques.
        current_link_code (str): Code du lien actuellement supervisé.
        sidebar (InfoSidebar): Panneau latéral affichant les informations.
        map_view (MapView): Composant affichant la carte géographique.
    """

    def __init__(self, parent_frame: ctk.CTkFrame, api_client: API_Client) -> None:
        """Initialise l'onglet de supervision et ses sous-composants.

        Args:
            parent_frame (ctk.CTkFrame): Conteneur parent de l'onglet.
            api_client (API_Client): Client API pour requêter les données.
        """
        self.parent: ctk.CTkFrame = parent_frame
        self.api: API_Client = api_client
        self.diag: DiagnosticService = DiagnosticService(self.api)
        self.mon_service: MonitoringService = MonitoringService(api_client)
        self.current_link_code: str = ""

        # Instanciation des composants UI
        self.sidebar: InfoSidebar = InfoSidebar(
            parent_frame, self.refresh_data, self.start_diagnostic_thread
        )
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)

        self.map_view: MapView = MapView(parent_frame)
        self.map_view.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Lancement de la boucle d'auto-rafraîchissement
        self.auto_refresh_monitoring()

    def load_client(self, link: Dict[str, Any]) -> None:
        """Charge un nouveau client dans l'onglet de supervision.

        Args:
            link (Dict[str, Any]): Dictionnaire contenant les informations du lien (dont 'link_code').
        """
        self.current_link_code = link.get("link_code", "")
        client_name = link.get("client_name", "Inconnu")
        
        self.sidebar.label_client.configure(text=f"Client : {client_name}")
        self.sidebar.set_diag_text("")
        self.refresh_data()

    def refresh_data(self) -> None:
        """Déclenche la mise à jour des données dans un thread séparé.
        
        Si aucun lien n'est chargé, la méthode ne fait rien.
        """
        if not self.current_link_code:
            return
        
        # Lancement asynchrone pour ne pas geler l'UI
        threading.Thread(target=self._threaded_load, daemon=True).start()

    def _threaded_load(self) -> None:
        """Fonction exécutée dans un thread séparé pour récupérer les données.
        
        Rapatrie les données de monitoring puis demande la mise à jour
        de l'interface graphique sur le thread principal (UI thread).
        """
        try:
            data: Dict[str, Any] = self.mon_service.fetch_comprehensive_data(self.current_link_code)
            # Retour sur le thread principal pour modifier l'UI
            self.parent.after(0, self._update_ui_safe, data)
        except Exception as e:
            logger.error(f"Erreur chargement supervision : {e}")
            self.parent.after(0, self.sidebar.set_status_error, "Erreur de chargement")

    def _update_ui_safe(self, data: Dict[str, Any]) -> None:
        """Met à jour l'interface utilisateur de manière sécurisée (thread principal).

        Args:
            data (Dict[str, Any]): Données agrégées retournées par l'API.
        """
        self.sidebar.update_display(data)
        self.map_view.update_marker(data.get("lat"), data.get("lng"), data.get("status"))

    def start_diagnostic_thread(self) -> None:
        """Démarre le processus de diagnostic complet de la ligne.
        
        Active l'animation de chargement et délègue le calcul à un thread.
        """
        if not self.current_link_code:
            return
            
        self.sidebar.set_diag_text("🔍 Diagnostic en cours...")
        self.sidebar.start_loading()  # Animation de chargement
        
        threading.Thread(target=self._threaded_diag, daemon=True).start()

    def _threaded_diag(self) -> None:
        """Exécute les routines de test réseau (Ping, MTR, SNMP) de manière asynchrone."""
        result: Dict[str, Any] = self.diag.run_full_diagnostic(self.current_link_code)
        
        # Renvoi du message formatté au thread principal
        message = result.get("message", "Aucun résultat.")
        self.parent.after(0, self._finish_diagnostic_ui, message)

    def _finish_diagnostic_ui(self, message: str) -> None:
        """Clôture la vue diagnostic sur le thread principal.

        Args:
            message (str): Rapport complet généré par le service de diagnostic.
        """
        self.sidebar.stop_loading()  # Arrêt de l'animation
        self.sidebar.set_diag_text(message)  # Affichage du rapport

    def auto_refresh_monitoring(self) -> None:
        """Boucle de rafraîchissement automatique des métriques.
        
        S'auto-invoque via Tkinter 'after' toutes les 60 secondes (60000 ms).
        """
        if self.current_link_code:
            self.refresh_data()
            
        self.parent.after(60000, self.auto_refresh_monitoring)