import os
import requests
import customtkinter as ctk
from dotenv import load_dotenv

# --- Chargement des variables d'environnement ---
# Cette ligne lit le fichier .env et charge son contenu en mémoire
load_dotenv()

# --- Configuration de l'API ---
BASE_URL = "https://kissapi.kissgroup.io/kisslink"

# On récupère la clé depuis l'environnement au lieu de l'écrire en dur
API_KEY = os.getenv("KISSGROUP_API_KEY")

# Sécurité supplémentaire : on bloque le script si le .env est manquant ou vide
if not API_KEY:
    raise ValueError("ERREUR CRITIQUE : La clé API 'KISSGROUP_API_KEY' est introuvable. Vérifiez votre fichier .env.")


class NoxiaDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.title("Noxia Security - Dashboard Kissgroup")
        self.geometry("850x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Titre global
        self.header = ctk.CTkLabel(self, text="Dashboard Noxia Security", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=15)

        # --- Création du système d'onglets ---
        self.tabview = ctk.CTkTabview(self, width=800, height=550)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        # Ajout des deux onglets
        self.tab_liste = self.tabview.add("Liste des Liens")
        self.tab_supervision = self.tabview.add("Supervision Monitoring")

        # Initialisation du contenu de chaque onglet
        self.setup_tab_liste()
        self.setup_tab_supervision()

    # ==========================================
    # ONGLET 1 : LISTE DES LIENS
    # ==========================================
    def setup_tab_liste(self):
        # Zone défilante pour la liste
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_liste, label_text="Inventaire des accès clients")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.btn_load_links = ctk.CTkButton(self.tab_liste, text="Charger la liste des liens", command=self.load_links)
        self.btn_load_links.pack(pady=10)

    def clear_frame(self):
        """Nettoie la liste avant un rafraîchissement"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def load_links(self):
        """Récupère et affiche la liste des liens depuis l'API /links"""
        self.clear_frame()
        headers = {"api_key": API_KEY}
        
        try:
            response = requests.get(f"{BASE_URL}/links", headers=headers)
            response.raise_for_status()
            links_data = response.json()

            if not links_data:
                self.show_message("Aucun lien trouvé.")
                return

            for i, link in enumerate(links_data):
                self.create_link_card(link)

        except Exception as e:
            self.show_message(f"Erreur : {str(e)}")

    def create_link_card(self, link):
        """Crée un petit bloc visuel pour chaque lien dans l'onglet 1"""
        card = ctk.CTkFrame(self.scroll_frame)
        card.pack(fill="x", padx=10, pady=5)

        # Colonne 1 : Client et Code
        name_label = ctk.CTkLabel(card, text=f"{link.get('client_name', 'N/A')}", font=ctk.CTkFont(size=14, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        code_label = ctk.CTkLabel(card, text=f"Code: {link.get('link_code', 'N/A')}", text_color="gray")
        code_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        # Colonne 2 : Technologie et Débit
        tech_info = f"{link.get('techno_name', 'N/A')} - {link.get('bandwidth_display', 'N/A')}"
        tech_label = ctk.CTkLabel(card, text=tech_info)
        tech_label.grid(row=0, column=1, padx=20, sticky="e")

        # Colonne 3 : Statut Administratif
        status = link.get('status_admin', 'Inconnu')
        status_color = "#2ecc71" if status == "Livré" else "#f1c40f"
        status_label = ctk.CTkLabel(card, text=status, text_color=status_color, font=ctk.CTkFont(size=12, weight="bold"))
        status_label.grid(row=0, column=2, padx=20, sticky="e")
        
        card.grid_columnconfigure(0, weight=1)

    def show_message(self, msg):
        lbl = ctk.CTkLabel(self.scroll_frame, text=msg)
        lbl.pack(pady=20)

    # ==========================================
    # ONGLET 2 : SUPERVISION (MONITORING)
    # ==========================================
    def setup_tab_supervision(self):
        # Éléments de texte (vides au démarrage) positionnés dans self.tab_supervision
        self.label_client = ctk.CTkLabel(self.tab_supervision, text="Appuyez sur 'Actualiser' pour charger les données de supervision.", font=ctk.CTkFont(size=14))
        self.label_client.pack(pady=(40, 10))

        self.label_address = ctk.CTkLabel(self.tab_supervision, text="", font=ctk.CTkFont(size=12))
        self.label_address.pack(pady=10)

        self.label_status = ctk.CTkLabel(self.tab_supervision, text="-", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_status.pack(pady=30)

        self.btn_refresh_monitoring = ctk.CTkButton(self.tab_supervision, text="Actualiser le Monitoring", command=self.fetch_monitoring_data, height=40)
        self.btn_refresh_monitoring.pack(pady=20)

    def fetch_monitoring_data(self):
        """Récupère et affiche les données depuis l'API /monitoring"""
        headers = {"api_key": API_KEY}
        
        try:
            response = requests.get(f"{BASE_URL}/monitoring", headers=headers)
            response.raise_for_status()
            data = response.json() 
            
            if isinstance(data, list) and len(data) > 0:
                lien = data[0] # On récupère le premier lien retourné par le monitoring
                
                # Mise à jour de l'interface
                self.label_client.configure(text=f"Lien : {lien.get('id_lien')} | Réf : {lien.get('reference_partenaire')}")
                self.label_address.configure(text=f"Adresse : {lien.get('address')}")
                
                status = lien.get('status_display', 'inconnu').lower()
                if status == 'ok':
                    self.label_status.configure(text="STATUT DU LIEN : OK", text_color="#2ecc71")
                else:
                    self.label_status.configure(text=f"STATUT DU LIEN : {status.upper()}", text_color="#e74c3c")
            else:
                self.label_status.configure(text="Aucune donnée de monitoring trouvée.", text_color="orange")
                
        except requests.exceptions.RequestException as e:
            self.label_status.configure(text="Erreur de connexion API", text_color="red")
            print(f"Détail de l'erreur : {e}")

# --- Lancement de l'application ---
if __name__ == "__main__":
    app = NoxiaDashboard()
    app.mainloop()