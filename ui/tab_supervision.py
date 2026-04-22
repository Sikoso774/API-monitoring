import threading
from ui.supervision.info_sidebar import InfoSidebar
from ui.supervision.map_view import MapView
from services.monitoring import MonitoringService

class TabSupervision:
    def __init__(self, parent_frame, api_client):
        self.parent = parent_frame
        self.api = api_client
        self.mon_service = MonitoringService(api_client)
        self.current_link_code = ""

        # Instanciation des composants
        self.sidebar = InfoSidebar(parent_frame, self.refresh_data, self.start_diagnostic_thread)
        self.sidebar.pack(side="left", fill="y", padx=20, pady=20)
        
        self.map_view = MapView(parent_frame)
        self.map_view.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.auto_refresh_monitoring()

    def load_client(self, link):
        self.current_link_code = link.get('link_code', '')
        self.sidebar.label_client.configure(text=f"Client : {link.get('client_name')}")
        self.sidebar.set_diag_text("")
        self.refresh_data()

    def refresh_data(self):
        if not self.current_link_code: return
        threading.Thread(target=self._threaded_load, daemon=True).start()

    def _threaded_load(self):
        try:
            data = self.mon_service.fetch_comprehensive_data(self.current_link_code)
            self.parent.after(0, self._update_ui_safe, data)
        except: pass

    def _update_ui_safe(self, data):
        self.sidebar.update_display(data)
        self.map_view.update_marker(data['lat'], data['lng'], data['status'])

    def start_diagnostic_thread(self):
        if not self.current_link_code: return
        self.sidebar.set_diag_text("🔍 Diagnostic en cours...")
        threading.Thread(target=self._threaded_diag, daemon=True).start()

    def _threaded_diag(self):
        result = self.api.run_diagnostic(self.current_link_code)
        self.parent.after(0, self.sidebar.set_diag_text, result.get("message"))

    def auto_refresh_monitoring(self):
        if self.current_link_code: self.refresh_data()
        self.parent.after(60000, self.auto_refresh_monitoring)