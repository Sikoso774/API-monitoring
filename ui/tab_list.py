"""Module gérant l'onglet 'Liste des Liens'.

Cet onglet permet d'afficher la liste des liens réseau via une API,
de les filtrer et de les exporter au format CSV.
"""

import csv
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox

from config.settings import COLORS, FONTS
from services.api_client import API_Client


class TabListe:
    """Classe représentant l'onglet Liste des Liens.

    Permet de charger les données depuis l'API, de les afficher sous forme
    de cartes, de filtrer les résultats et d'exporter en CSV.

    Attributes:
        parent (ctk.CTkFrame): Le widget parent contenant cet onglet.
        api (API_Client): Le client API pour récupérer les données.
        on_supervise (Callable): Fonction callback pour passer à l'onglet Supervision.
        all_links (List[Dict[str, Any]]): Liste complète des liens récupérés.
    """

    def __init__(
        self,
        parent_frame: ctk.CTkFrame,
        api_client: API_Client,
        on_supervise_callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Initialise l'onglet de liste des liens.

        Args:
            parent_frame (ctk.CTkFrame): Conteneur parent de l'onglet.
            api_client (API_Client): Client API pour requêter la liste.
            on_supervise_callback (Callable): Callback exécuté au clic sur "SUPERVISER".
        """
        self.parent: ctk.CTkFrame = parent_frame
        self.api: API_Client = api_client
        self.on_supervise: Callable[[Dict[str, Any]], None] = on_supervise_callback
        self.all_links: List[Dict[str, Any]] = []

        self.setup_ui()

    def setup_ui(self) -> None:
        """Construit l'interface graphique de l'onglet (barre de recherche, boutons, scroll)."""
        self.ctrl_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(
            self.ctrl_frame, placeholder_text="Rechercher...", width=350, height=35
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_links)

        self.btn_load = ctk.CTkButton(
            self.ctrl_frame,
            text="CHARGER API",
            font=FONTS["button"],
            fg_color=COLORS["primary"],
            command=self.load_links
        )
        self.btn_load.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(
            self.ctrl_frame,
            text="EXPORTER CSV",
            font=FONTS["button"],
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_hover"],
            command=self.export_to_csv
        )
        self.btn_export.pack(side="left", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def load_links(self) -> None:
        """Récupère la liste complète des liens depuis l'API et met à jour l'affichage."""
        try:
            self.all_links = self.api.get_links()
            self.display_links(self.all_links)
        except Exception as e:
            self.show_message(f"Erreur : {e}")

    def display_links(self, links_to_show: List[Dict[str, Any]]) -> None:
        """Affiche les cartes d'informations pour une liste de liens donnée.

        Nettoie la zone d'affichage avant de générer les nouvelles cartes.

        Args:
            links_to_show (List[Dict[str, Any]]): La liste des liens à afficher.
        """
        # Nettoyage des widgets existants
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for link in links_to_show:
            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=COLORS["card"],
                border_width=1,
                border_color=COLORS["border"]
            )
            card.pack(fill="x", padx=10, pady=5)

            client_name: str = link.get("client_name", "Inconnu")
            link_code: str = link.get("link_code", "N/A")
            techno_name: str = link.get("techno_name", "N/A")
            info: str = f"{client_name}\n{link_code} | {techno_name}"

            ctk.CTkLabel(
                card, text=info, font=("Arial", 13, "bold"), justify="left"
            ).pack(side="left", padx=15, pady=10)

            status: str = link.get("status_admin", "Inconnu")
            color: str = COLORS["accent"] if status == "Livré" else "#f1c40f"
            ctk.CTkLabel(card, text=f"● {status}", text_color=color).pack(side="left", padx=20)

            # Appel de la fonction callback injectée depuis app.py
            ctk.CTkButton(
                card,
                text="SUPERVISER",
                font=FONTS["button"],
                width=100,
                fg_color=COLORS["primary"],
                command=lambda l=link: self.on_supervise(l)
            ).pack(side="right", padx=15)

    def filter_links(self, event: Any = None) -> None:
        """Filtre la liste des liens affichés en fonction de la barre de recherche.

        Args:
            event (Any, optional): Événement Tkinter ayant déclenché l'appel. Par défaut None.
        """
        query: str = self.search_entry.get().lower()
        # Filtrage basé sur la conversion en chaîne brute du dictionnaire
        filtered: List[Dict[str, Any]] = [
            l for l in self.all_links if query in str(l).lower()
        ]
        self.display_links(filtered)

    def export_to_csv(self) -> None:
        """Exporte la liste complète des liens chargés vers un fichier CSV.

        Affiche une boîte de dialogue pour la sélection de l'emplacement de sauvegarde.
        """
        if not self.all_links:
            messagebox.showwarning("Export Impossible", "Veuillez d'abord charger la liste.")
            return

        file_path: str = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile="inventaire_noxia.csv"
        )

        if file_path:
            try:
                # Utilisation de utf-8-sig pour la compatibilité Excel (BOM)
                with open(file_path, mode="w", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow([
                        "Client", "Code Lien", "Adresse", "Techno",
                        "Débit", "Statut Admin", "Référence Partenaire"
                    ])
                    for link in self.all_links:
                        writer.writerow([
                            link.get("client_name"),
                            link.get("link_code"),
                            link.get("address"),
                            link.get("techno_name"),
                            link.get("bandwidth_display"),
                            link.get("status_admin"),
                            link.get("reference_partner")
                        ])
                messagebox.showinfo("Succès", "Inventaire exporté.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'écrire le fichier : {e}")

    def show_message(self, msg: str) -> None:
        """Affiche un message temporaire (souvent d'erreur) au sein du conteneur défilable.

        Args:
            msg (str): Message à afficher.
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.scroll_frame, text=msg).pack(pady=20)