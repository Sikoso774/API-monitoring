import customtkinter as ctk
from config.settings import COLORS, FONTS

class InfoSidebar(ctk.CTkScrollableFrame):
    def __init__(self, master, on_refresh, on_diagnostic, **kwargs):
        super().__init__(master, width=320, fg_color="transparent", **kwargs)
        
        # En-tête Client
        self.label_client = ctk.CTkLabel(self, text="Sélectionnez un lien", font=FONTS["title"], wraplength=280)
        self.label_client.pack(pady=(10, 5))
        
        self.label_address = ctk.CTkLabel(self, text="", font=FONTS["body"], wraplength=280)
        self.label_address.pack(pady=5)

        # Carte d'informations techniques
        self.tech_frame = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=8)
        self.tech_frame.pack(fill="x", pady=15, padx=5)
        
        self.label_last_conn = self._create_label("Dernière connexion : -", bold=True, color=COLORS["accent"])
        self.label_provider = self._create_label("Fournisseur : -")
        self.label_ip = self._create_label("IP Publique : -")
        self.label_pppoe = self._create_label("Session PPP : -")
        self.label_brand = self._create_label("Marque : -")
        self.label_attenuation = self._create_label("Atténuation : -", bold=True)
        self.label_pass = self._create_label("Pass Admin : -", padding=(2, 10))

        # Statut Temps Réel
        self.label_status = ctk.CTkLabel(self, text="-", font=FONTS["status"])
        self.label_status.pack(pady=15)
        
        # Boutons d'action
        ctk.CTkButton(self, text="Rafraîchir Statut", fg_color=COLORS["primary"], command=on_refresh).pack(pady=10)
        
        # MODIFICATION 1 : On sauvegarde le bouton pour pouvoir le désactiver plus tard
        self.btn_diag = ctk.CTkButton(self, text="LANCER DIAGNOSTIC", fg_color="#8e44ad", hover_color="#732d91", command=on_diagnostic)
        self.btn_diag.pack(pady=(15, 5))
        
        # MODIFICATION 2 : Création de la barre de progression (sans faire de .pack() pour qu'elle reste cachée)
        self.progress_bar = ctk.CTkProgressBar(
            self, 
            orientation="horizontal", 
            mode="indeterminate",
            progress_color=COLORS["accent"], # Le vert néon de ta charte
            fg_color=COLORS["card"]          # Le gris de tes cartes
        )
        self.progress_bar.set(0)

        # Zone de résultat Diagnostic
        self.diag_result = ctk.CTkTextbox(self, height=100, fg_color=COLORS["card"], state="disabled", wrap="word")
        self.diag_result.pack(fill="x", pady=5, padx=5)

    # --- Reste de tes fonctions _create_label, update_display, etc... ---
        
    def _create_label(self, text, bold=False, color=None, padding=(2, 2)):
        # On utilise le dictionnaire de polices ici aussi !
        font = FONTS["small_bold"] if bold else FONTS["small"]
        lbl = ctk.CTkLabel(self.tech_frame, text=text, font=font, text_color=color, anchor="w")
        lbl.pack(fill="x", padx=10, pady=padding)
        return lbl

    def update_display(self, data):
        """Met à jour l'ensemble des labels avec les données fournies"""
        status_text = data.get("status", "INCONNU").strip().upper()
        is_ok = (status_text == "OK")
        
        self.label_status.configure(text=f"STATUT : {status_text}", 
                                    text_color=COLORS["accent"] if is_ok else COLORS["error"])
        
        self.label_address.configure(text=f"Adresse : {data.get('address', '')}")
        self.label_ip.configure(text=f"IP Publique : {data.get('ip_publique', 'N/A')}")
        self.label_pppoe.configure(text=f"Session PPP : {data.get('session_ppp', 'N/A')}")
        self.label_provider.configure(text=f"Fournisseur : {data.get('provider', 'N/A')}")
        self.label_brand.configure(text=f"Marque : {data.get('brand', 'N/A')}")
        self.label_pass.configure(text=f"Pass Admin : {data.get('password_device', 'N/A')}")
        
        # Gestion de la date
        last_conn = data.get("last_change_connection_date", "Inconnue")
        if "T" in last_conn:
            formatted_date = f"{last_conn.split('T')[0]} à {last_conn.split('T')[1][:5]}"
        else:
            formatted_date = last_conn
        self.label_last_conn.configure(text=f"Dernière co : {formatted_date}")

        # Alerte atténuation
        att = data.get('attenuation', 0)
        self.label_attenuation.configure(text=f"Atténuation : {att} dB", 
                                         text_color=COLORS["accent"] if att >= -20 else COLORS["error"])

    def set_diag_text(self, text):
        self.diag_result.configure(state="normal")
        self.diag_result.delete("1.0", "end")
        self.diag_result.insert("1.0", text)
        self.diag_result.configure(state="disabled")
    
    # MODIFICATION 3 : Ajoute ces deux méthodes tout à la fin de la classe
    def start_loading(self):
        """Affiche et anime la barre de progression"""
        self.btn_diag.configure(state="disabled") # Bloque les clics multiples
        # On l'affiche juste au-dessus de la zone de résultat
        self.progress_bar.pack(pady=5, before=self.diag_result) 
        self.progress_bar.start()

    def stop_loading(self):
        """Arrête et cache la barre de progression"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_diag.configure(state="normal") # Réactive le bouton