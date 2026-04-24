import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox
from config.settings import COLORS, FONTS

class TabListe:
    def __init__(self, parent_frame, api_client, on_supervise_callback):
        self.parent = parent_frame
        self.api = api_client
        self.on_supervise = on_supervise_callback # La fonction go_to_monitoring de app.py
        self.all_links = []
        
        self.setup_ui()

    def setup_ui(self):
        self.ctrl_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(self.ctrl_frame, placeholder_text="Rechercher...", width=350, height=35)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_links)

        self.btn_load = ctk.CTkButton(self.ctrl_frame, 
                                      text="CHARGER API", 
                                      font=FONTS["button"], 
                                      fg_color=COLORS["primary"], 
                                      command=self.load_links)
        
        self.btn_load.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(self.ctrl_frame, 
                                        text="EXPORTER CSV", 
                                        font=FONTS["button"], 
                                        fg_color=COLORS["secondary"], 
                                        hover_color=COLORS["secondary_hover"], 
                                        command=self.export_to_csv)
        
        self.btn_export.pack(side="left", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def load_links(self):
        try:
            self.all_links = self.api.get_links()
            self.display_links(self.all_links)
        except Exception as e:
            self.show_message(f"Erreur : {e}")

    def display_links(self, links_to_show):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        for link in links_to_show:
            card = ctk.CTkFrame(self.scroll_frame, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", padx=10, pady=5)

            info = f"{link.get('client_name')}\n{link.get('link_code')} | {link.get('techno_name')}"
            ctk.CTkLabel(card, text=info, font=("Arial", 13, "bold"), justify="left").pack(side="left", padx=15, pady=10)

            status = link.get('status_admin')
            color = COLORS["accent"] if status == "Livré" else "#f1c40f"
            ctk.CTkLabel(card, text=f"● {status}", text_color=color).pack(side="left", padx=20)

            # Appel de la fonction callback injectée depuis app.py
            ctk.CTkButton(card, text="SUPERVISER", font=FONTS["button"], width=100, fg_color=COLORS["primary"],
                          command=lambda l=link: self.on_supervise(l)).pack(side="right", padx=15)

    def filter_links(self, event=None):
        query = self.search_entry.get().lower()
        filtered = [l for l in self.all_links if query in str(l).lower()]
        self.display_links(filtered)

    def export_to_csv(self):
        if not self.all_links:
            messagebox.showwarning("Export Impossible", "Veuillez d'abord charger la liste.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")], initialfile="inventaire_noxia.csv")
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(["Client", "Code Lien", "Adresse", "Techno", "Débit", "Statut Admin", "Référence Partenaire"])
                    for link in self.all_links:
                        writer.writerow([link.get('client_name'), link.get('link_code'), link.get('address'), link.get('techno_name'), link.get('bandwidth_display'), link.get('status_admin'), link.get('reference_partner')])
                messagebox.showinfo("Succès", f"Inventaire exporté.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'écrire le fichier : {e}")

    def show_message(self, msg):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.scroll_frame, text=msg).pack(pady=20)