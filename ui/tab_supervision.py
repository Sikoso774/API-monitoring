import os
import threading
import customtkinter as ctk
import tkintermapview
from PIL import Image, ImageTk

from services.monitoring import MonitoringService
from config.settings import COLORS, ASSETS_DIR

class TabSupervision:
    def __init__(self, parent_frame, api_client):
        self.parent = parent_frame
        self.api = api_client
        self.current_address = ""
        self.current_link_code = "" # On sauvegarde le code du lien pour le diagnostic
        self.mon_service = MonitoringService(api_client)
        
        self.setup_ui()
        self.auto_refresh_monitoring()

    def load_icon_with_ratio(self, filename, width_wanted=35):
        path = os.path.join(ASSETS_DIR, filename)
        pil_img = Image.open(path)
        ratio = pil_img.height / pil_img.width
        height_calculated = int(width_wanted * ratio)
        img_resized = pil_img.resize((width_wanted, height_calculated), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img_resized)

    def setup_ui(self):
        # --- CHARGEMENT DES ICÔNES ---
        try:
            self.img_pin_ok = self.load_icon_with_ratio("green_pin.png", width_wanted=35)
            self.img_pin_error = self.load_icon_with_ratio("red_pin.png", width_wanted=35)
        except Exception:
            self.img_pin_ok = None
            self.img_pin_error = None

        # --- PANNEAU DE GAUCHE (Transformé en ScrollableFrame pour les petits écrans) ---
        self.info_panel = ctk.CTkScrollableFrame(self.parent, width=320, fg_color="transparent")
        self.info_panel.pack(side="left", fill="y", padx=20, pady=20)

        # En-tête Client
        self.label_client = ctk.CTkLabel(self.info_panel, text="Sélectionnez un lien", font=("Arial", 16, "bold"), wraplength=280)
        self.label_client.pack(pady=(10, 5))
        self.label_address = ctk.CTkLabel(self.info_panel, text="", font=("Arial", 12), wraplength=280)
        self.label_address.pack(pady=5)

        # Carte d'informations techniques (PPPoE, IP, Device)
        self.tech_frame = ctk.CTkFrame(self.info_panel, fg_color=COLORS["card"], corner_radius=8)
        self.tech_frame.pack(fill="x", pady=15, padx=5)
        
        self.label_provider = ctk.CTkLabel(self.tech_frame, text="Fournisseur : -", font=("Arial", 11), anchor="w")
        self.label_provider.pack(fill="x", padx=10, pady=(10, 2))
        
        self.label_ip = ctk.CTkLabel(self.tech_frame, text="IP Publique : -", font=("Arial", 11), anchor="w")
        self.label_ip.pack(fill="x", padx=10, pady=2)
        
        self.label_pppoe = ctk.CTkLabel(self.tech_frame, text="Session PPP : -", font=("Arial", 11), anchor="w")
        self.label_pppoe.pack(fill="x", padx=10, pady=2)
        
        self.label_device = ctk.CTkLabel(self.tech_frame, text="IP Équipement : -", font=("Arial", 11), anchor="w")
        self.label_device.pack(fill="x", padx=10, pady=(2, 10))
        
        self.label_last_conn = ctk.CTkLabel(self.tech_frame, text="Dernière connexion : -", font=("Arial", 11, "bold"), text_color=COLORS["accent"], anchor="w")
        self.label_last_conn.pack(fill="x", padx=10, pady=(10, 2))

        # Statut Temps Réel
        self.label_status = ctk.CTkLabel(self.info_panel, text="-", font=("Arial", 30, "bold"))
        self.label_status.pack(pady=15)
        
        self.btn_mon = ctk.CTkButton(self.info_panel, text="Rafraîchir Statut", fg_color=COLORS["primary"], command=self.refresh_data)
        self.btn_mon.pack(pady=10)

        # Outil de Diagnostic
        self.btn_diag = ctk.CTkButton(self.info_panel, text="LANCER DIAGNOSTIC", fg_color="#8e44ad", hover_color="#732d91", command=self.run_diagnostic)
        self.btn_diag.pack(pady=(15, 5))
        
        # CORRECTION ICI : fill="x" (sans les antislashs)
        self.diag_result = ctk.CTkTextbox(self.info_panel, height=80, fg_color=COLORS["card"], text_color=COLORS["text"], state="disabled", wrap="word")
        self.diag_result.pack(fill="x", pady=5, padx=5)

        # --- PANNEAU DE DROITE (Carte) ---
        self.map_widget = tkintermapview.TkinterMapView(self.parent, corner_radius=10)
        self.map_widget.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png")
        self.map_widget.set_position(48.8566, 2.3522)


    def fetch_link_details(self):
        """Récupère et affiche les informations techniques (PPPoE, Provider, Device)"""
        if not self.current_link_code: return
        try:
            details = self.api.get_link_details(self.current_link_code)
            
            # 1. Fournisseur
            provider = details.get("provider_name", "Inconnu")
            self.label_provider.configure(text=f"Fournisseur : {provider}")
            
            # 2. Session PPPoE & IP
            ppp_logins = details.get("ppp_logins", [])
            if ppp_logins and len(ppp_logins) > 0:
                first_ppp = ppp_logins[0]
                self.label_pppoe.configure(text=f"Session PPP : {first_ppp.get('ppp_login', 'Non définie')}")
                self.label_ip.configure(text=f"IP Publique : {first_ppp.get('ip_address', 'Non définie')}")
            else:
                self.label_pppoe.configure(text="Session PPP : Aucune")
                self.label_ip.configure(text="IP Publique : Aucune")
                
            # 3. Equipement (KISSBOX, ONT...)
            devices = details.get("devices", [])
            if devices and len(devices) > 0:
                device_ip = devices[0].get("ip_device", "Non administrable")
                self.label_device.configure(text=f"IP Équipement : {device_ip}")
            else:
                self.label_device.configure(text="IP Équipement : Aucun")
                
        except Exception as e:
            print(f"Erreur détails techniques : {e}")
            self.label_provider.configure(text="Fournisseur : Erreur réseau")
            
            
    def load_client(self, link):
        """Action lancée au clic sur SUPERVISER"""
        self.current_link_code = link.get('link_code', '')
        self.label_client.configure(text=f"Client : {link.get('client_name')}")
        self.label_status.configure(text="Chargement des données...", text_color="white")
        self.current_address = link.get('address', '')
        
        # On vide la boîte de diag par défaut
        self.set_diag_text("") 
        
        # On lance le chargement
        self.refresh_data()

    def refresh_data(self):
        """Lance le thread de fond pour ne pas figer l'interface"""
        if not self.current_link_code: return
        thread = threading.Thread(target=self._threaded_load, args=(self.current_link_code,))
        thread.daemon = True
        thread.start()

    def _threaded_load(self, link_code):
        """Logique réseau exécutée en arrière-plan"""
        try:
            full_data = self.mon_service.fetch_comprehensive_data(link_code)
            # Une fois les données prêtes, on dit à l'interface de s'actualiser
            self.parent.after(0, self._update_ui_safe, full_data)
        except Exception as e:
            print(f"Erreur fatale dans le thread : {e}")
            self.parent.after(0, lambda: self.label_status.configure(text="ERREUR RÉSEAU", text_color="red"))

    def _update_ui_safe(self, data):
            """Met à jour les textes de l'interface graphique en toute sécurité"""
            
            # On nettoie le texte (enlève les espaces invisibles) et on vérifie
            is_ok = data['status'].strip().upper() == "OK"
            
            # Statut et Adresse
            self.label_status.configure(text=f"STATUT : {data['status']}", 
                                        text_color=COLORS["accent"] if is_ok else COLORS["error"])
            if data['address']:
                self.label_address.configure(text=f"Adresse : {data['address']}")
                
            # NOUVEAU : Mise à jour des 4 champs techniques que j'avais oubliés
            self.label_ip.configure(text=f"IP Publique : {data['ip_publique']}")
            self.label_pppoe.configure(text=f"Session PPP : {data['session_ppp']}")
            self.label_provider.configure(text=f"Fournisseur : {data['provider']}")
            self.label_device.configure(text=f"IP Équipement : {data['ip_device']}")
            
            # Mise à jour de la carte
            lat, lng = data['lat'], data['lng']
            if lat and lng:
                self.map_widget.delete_all_marker()
                self.map_widget.set_position(lat, lng)
                icone = self.img_pin_ok if data['status'] == "OK" else self.img_pin_error
                
                if icone:
                    self.map_widget.set_marker(lat, lng, text=f"État : {data['status']}", icon=icone, text_color=COLORS["text"])
                else:
                    self.map_widget.set_marker(lat, lng, text=f"État : {data['status']}", text_color=COLORS["text"])
                
                self.map_widget.set_zoom(13)

    def auto_refresh_monitoring(self):
            """Rafraîchissement automatique toutes les 60 secondes"""
            if self.current_link_code:
                self.refresh_data()
            self.parent.after(60000, self.auto_refresh_monitoring)

    def run_diagnostic(self):
        """Lance l'appel API du diagnostic et affiche le résultat"""
        if not self.current_link_code:
            self.set_diag_text("Veuillez sélectionner un lien d'abord.")
            return
            
        self.set_diag_text("Lancement du diagnostic en cours...")
        self.parent.update() # Force l'interface à se mettre à jour immédiatement
        
        try:
            result = self.api.run_diagnostic(self.current_link_code)
            # On cherche le champ "message" ou on affiche le JSON brut
            message = result.get("message", str(result))
            self.set_diag_text(message)
        except Exception as e:
            self.set_diag_text(f"Échec du diagnostic :\n{e}")

    def set_diag_text(self, text):
        """Méthode utilitaire pour écrire dans la TextBox en lecture seule"""
        self.diag_result.configure(state="normal")
        self.diag_result.delete("1.0", "end")
        self.diag_result.insert("1.0", text)
        self.diag_result.configure(state="disabled")

    def fetch_monitoring_data(self):
        try:
            # 1. On récupère la liste de tous les liens supervisés
            monitoring_list = self.api.get_monitoring_data()
            
            # 2. On cherche le lien qui correspond à notre current_link_code
            lien_data = next((item for item in monitoring_list if item.get("id_lien") == self.current_link_code), None)
            
            if lien_data:
                # Extraction de la date de dernière connexion
                last_conn = lien_data.get("last_change_connection_date", "Inconnue")
                
                # Formatage rapide de la date (ex: 2026-04-10T02:49:04+02:00 -> 10/04/2026 02:49)
                if last_conn != "Inconnue":
                    date_part = last_conn.split("T")[0]
                    time_part = last_conn.split("T")[1][:5]
                    formatted_date = f"{date_part} à {time_part}"
                else:
                    formatted_date = "Jamais"

                # Mise à jour d'un nouveau label (à ajouter dans setup_ui)
                self.label_last_conn.configure(text=f"Dernière connexion : {formatted_date}")
            
            
            lat, lng = lien.get('lat'), lien.get('lng')
            if lat and lng:
                self.map_widget.delete_all_marker()
                self.map_widget.set_position(lat, lng)
                
                icone = self.img_pin_ok if is_ok else self.img_pin_error
                
                if icone:
                    self.map_widget.set_marker(lat, lng, text=f"État : {status.upper()}", icon=icone, text_color=COLORS["text"])
                else:
                    self.map_widget.set_marker(lat, lng, text=f"État : {status.upper()}", marker_color_circle=color, marker_color_outside=color, text_color=COLORS["text"])
                
                self.map_widget.set_zoom(13)
        except Exception:
            self.label_status.configure(text="Erreur Supervision", text_color="red")