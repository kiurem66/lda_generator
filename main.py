#!/usr/bin/env python3
"""
Vampire: The Masquerade Character Sheet Generator
Genera schede personaggio a partire da un template PSD
"""

import os
import json
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import psd_tools
from psd_tools.api.psd_image import PSDImage
import shutil

# Costanti per i layer del PSD basate sull'analisi

# Layer di testo per le informazioni generali (da modificare con i valori dell'utente)
TEXT_LAYERS = {
    "nome_pg_label": "Nome PG",
    "player_label": "Player", 
    "clan_label": "Clan",
    "generazione_label": "Generazione",
    "pregi_difetti_label": "Pregi&Difetti",
    "salute_label": "Salute",
    "background_label": "Background",
    "discipline_label": "Discipline",
    "punti_sangue_label": "Punti Sangue",
    "volonta_label": "Volontà",
    "umanita_label": "Umanità/Sentiero",
    "fisici_label": "Fisici",
    "sociali_label": "Sociali", 
    "mentali_label": "Mentali",
}

# Layer per i punteggi delle abilità (testo)
SKILL_SCORE_LAYERS = {
    "agilita": "Punteggio Agilità",
    "armi_da_fuoco": "Punteggio Armi da Fuoco",
    "armi_da_mischia": "Punteggio Armi da Mischia",
    "manualita": "Punteggio Manualità",
    "rissa": "Punteggio Rissa",
    "sopravvivenza": "Punteggio Sopravvivenza",
    "accademiche": "Punteggio Accademiche",
    "affinita_animale": "Punteggio Affinità Animale",
    "empatia": "Punteggio Empatia",
    "intimidire": "Punteggio Intimidire",
    "autocontrollo": "Punteggio Autocontrollo",
    "espressione_artistica": "Punteggio Espressione Artistica",
    "sotterfugio": "Punteggio Sotterfugio",
    "intuito": "Punteggio Intuito",
    "investigare": "Punteggio Investigare",
    "medicina": "Punteggio Medicina",
    "occulto": "Punteggio Occulto",
    "tecnologia": "Punteggio Tecnologia",
}

# Layer per le barre colorate delle abilità (Colore = attivo, B&N = disattivato)
SKILL_COLOR_LAYERS = {
    "agilita": {"color": "Colore Agilita", "bn": "B&N Agilita"},
    "armi_da_fuoco": {"color": "Colore Armi da Fuoco", "bn": "B&N Armi da Fuoco"},
    "armi_da_mischia": {"color": "Colore Armi da Mischia", "bn": "B&N Armi da Mischia"},
    "manualita": {"color": "Colore Manualità", "bn": "B&N Manualità"},
    "rissa": {"color": "Colore Rissa", "bn": "B&N Rissa"},
    "sopravvivenza": {"color": "Colore Sopravvivenza", "bn": "B&N Sopravvivenza"},
    "accademiche": {"color": "Colore Accademiche", "bn": "B&N Accademiche"},
    "affinita_animale": {"color": "Colore Affinità Animale", "bn": "B&N Affinità Animale"},
    "empatia": {"color": "Colore Empatia", "bn": "B&N Empatia"},
    "intimidire": {"color": "Colore Intimidire", "bn": "B&N Intimidire"},
    "autocontrollo": {"color": "Colore Autocontrollo", "bn": "Bianco e nero Autocontrollo"},
    "espressione_artistica": {"color": "Colore Espressione Artistica", "bn": "B&N Espressione Artistica copy"},
    "sotterfugio": {"color": "Colore Sotterfugio", "bn": "B&N Sotterfugio"},
    "intuito": {"color": "Colore Intuito", "bn": "B&N Intuito"},
    "investigare": {"color": "Colore Investigare", "bn": "B&N Investigare"},
    "medicina": {"color": "Colore Medicina", "bn": "B&N Medicina"},
    "occulto": {"color": "Colore Occulto", "bn": "B&N Occulto"},
    "tecnologia": {"color": "Colore Tecnologia", "bn": "B&N Tecnologia"},
}

# Layer per le caselle di Salute
HEALTH_BOX_LAYERS = {
    "active": [
        "Nuovo progetto - 2026-08-22T194053.003",
        "Nuovo progetto - 2026-08-22T194053.003 copy",
        "Nuovo progetto - 2026-08-22T194053.003 copy 2",
        "Nuovo progetto - 2026-08-22T194053.003 copy 3",
        "Nuovo progetto - 2026-08-22T194053.003 copy 4",
    ],
    "inactive": [
        "Nuovo progetto - 2026-08-22T194053.003 copy 5",
        "Nuovo progetto - 2026-08-22T194053.003 copy 6",
    ],
}


class CharacterSheetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vampire: The Masquerade - Generatore Schede")
        self.root.geometry("1200x800")
        
        # Mappa per salvare le informazioni dei layer di testo (posizione e testo originale)
        self.text_layers_info = {}
        
        # Variabili per i dati del personaggio
        self.character_data = {
            "nome_pg": tk.StringVar(),
            "player": tk.StringVar(),
            "clan": tk.StringVar(),
            "generazione": tk.StringVar(),
            "pregi": tk.StringVar(),
            "difetti": tk.StringVar(),
            
            "fisici": tk.IntVar(value=0),
            "sociali": tk.IntVar(value=0),
            "mentali": tk.IntVar(value=0),
            
            "punti_sangue": tk.IntVar(value=0),
            "volonta": tk.IntVar(value=0),
            "umanita": tk.IntVar(value=0),
            
            "salute": tk.IntVar(value=0),
            
            "discipline": tk.StringVar(),
            "background": tk.StringVar(),
            
            "skills": {}
        }
        
        # Inizializza le abilità
        self.skills_list = [
            "agilita", "armi_da_fuoco", "armi_da_mischia", "manualita", "rissa", "sopravvivenza",
            "accademiche", "affinita_animale", "empatia", "intimidire", 
            "autocontrollo", "espressione_artistica", "sotterfugio",
            "intuito", "investigare", "medicina", "occulto", "tecnologia"
        ]
        
        for skill in self.skills_list:
            self.character_data["skills"][skill] = {
                "active": tk.BooleanVar(value=False),
                "score": tk.IntVar(value=0)
            }
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Percorso del file PSD
        self.psd_path = os.path.join(os.path.dirname(__file__), "Scheda Lanterna d'Avorio.psd")
        
        # Finestra di caricamento
        self.loading_window = None
        
        if not os.path.exists(self.psd_path):
            messagebox.showerror("Errore", f"File PSD non trovato: {self.psd_path}")
            self.root.destroy()
            return
    
    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia"""
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_general_tab(notebook)
        self.create_attributes_tab(notebook)
        self.create_skills_tab(notebook)
        self.create_points_tab(notebook)

        self.create_discipline_bg_tab(notebook)
        
        notebook.add(self.general_frame, text="Dati Generali")
        notebook.add(self.attributes_frame, text="Attributi")
        notebook.add(self.skills_frame, text="Abilità")
        notebook.add(self.points_frame, text="Punti e Salute")
        notebook.add(self.discipline_bg_frame, text="Discipline & Background")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Salva in JSON", command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Carica da JSON", command=self.load_from_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Genera PNG", command=self.generate_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Genera PSD", command=self.generate_psd).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Esci", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def create_general_tab(self, notebook):
        """Crea il tab per i dati generali"""
        self.general_frame = ttk.Frame(notebook, padding="10")
        
        ttk.Label(self.general_frame, text="Nome PG:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["nome_pg"]).grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.general_frame, text="Player:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["player"]).grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.general_frame, text="Clan:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["clan"]).grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.general_frame, text="Generazione:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["generazione"]).grid(row=3, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.general_frame, text="Pregi:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["pregi"]).grid(row=4, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.general_frame, text="Difetti:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.general_frame, textvariable=self.character_data["difetti"]).grid(row=5, column=1, sticky=tk.EW, pady=2)
        
        self.general_frame.columnconfigure(1, weight=1)
    
    def create_attributes_tab(self, notebook):
        """Crea il tab per gli attributi"""
        self.attributes_frame = ttk.Frame(notebook, padding="10")
        
        ttk.Label(self.attributes_frame, text="Fisici:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.attributes_frame, from_=0, to=5, textvariable=self.character_data["fisici"]).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.attributes_frame, text="Sociali:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.attributes_frame, from_=0, to=5, textvariable=self.character_data["sociali"]).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.attributes_frame, text="Mentali:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.attributes_frame, from_=0, to=5, textvariable=self.character_data["mentali"]).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.attributes_frame, text="Inserisci il numero di cerchi attivi (0-5)", font=('Arial', 8, 'italic')).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_skills_tab(self, notebook):
        """Crea il tab per le abilità"""
        self.skills_frame = ttk.Frame(notebook, padding="10")
        
        skill_categories = {
            "Talenti": ["agilita", "armi_da_fuoco", "armi_da_mischia", "manualita", "rissa", "sopravvivenza"],
            "Abilità": ["affinita_animale", "empatia", "intimidire", "autocontrollo", "espressione_artistica", "sotterfugio"],
            "Conoscenze": ["accademiche", "intuito", "investigare", "medicina", "occulto", "tecnologia"]
        }
        
        row = 0
        for category, skills in skill_categories.items():
            ttk.Label(self.skills_frame, text=category, font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
            row += 1
            
            for skill in skills:
                cb = ttk.Checkbutton(
                    self.skills_frame, 
                    text=self.get_skill_display_name(skill),
                    variable=self.character_data["skills"][skill]["active"],
                    command=lambda s=skill: self.toggle_skill_score(s)
                )
                cb.grid(row=row, column=0, sticky=tk.W, pady=2)
                
                spinbox = ttk.Spinbox(
                    self.skills_frame, 
                    from_=0, 
                    to=5, 
                    textvariable=self.character_data["skills"][skill]["score"],
                    state='disabled',
                    width=3
                )
                spinbox.grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
                
                setattr(self, f"{skill}_spinbox", spinbox)
                row += 1
            
            row += 1
        
        ttk.Label(self.skills_frame, text="Seleziona le abilità possedute e inserisci il punteggio (1-5)", 
                  font=('Arial', 8, 'italic')).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    def get_skill_display_name(self, skill_id):
        """Converte l'ID dell'abilità in nome visualizzabile"""
        names = {
            "agilita": "Agilità",
            "armi_da_fuoco": "Armi da Fuoco",
            "armi_da_mischia": "Armi da Mischia",
            "manualita": "Manualità",
            "rissa": "Rissa",
            "sopravvivenza": "Sopravvivenza",
            "accademiche": "Accademiche",
            "affinita_animale": "Affinità Animale",
            "empatia": "Empatia",
            "intimidire": "Intimidire",
            "autocontrollo": "Autocontrollo",
            "espressione_artistica": "Espressione Artistica",
            "sotterfugio": "Sotterfugio",
            "intuito": "Intuito",
            "investigare": "Investigare",
            "medicina": "Medicina",
            "occulto": "Occulto",
            "tecnologia": "Tecnologia"
        }
        return names.get(skill_id, skill_id)
    
    def toggle_skill_score(self, skill):
        """Abilita/disabilita il campo punteggio in base allo stato del checkbox"""
        spinbox = getattr(self, f"{skill}_spinbox", None)
        if spinbox:
            if self.character_data["skills"][skill]["active"].get():
                spinbox.config(state='normal')
            else:
                spinbox.config(state='disabled')
                self.character_data["skills"][skill]["score"].set(0)
    
    def create_points_tab(self, notebook):
        """Crea il tab per Punti Sangue, Volontà, Umanità e Salute"""
        self.points_frame = ttk.Frame(notebook, padding="10")
        
        ttk.Label(self.points_frame, text="Punti Sangue:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.points_frame, from_=5, to=10, textvariable=self.character_data["punti_sangue"]).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.points_frame, text="Volontà:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.points_frame, from_=1, to=5, textvariable=self.character_data["volonta"]).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.points_frame, text="Umanità/Sentiero:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.points_frame, from_=2, to=10, textvariable=self.character_data["umanita"]).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.points_frame, text="Salute:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(self.points_frame, from_=5, to=8, textvariable=self.character_data["salute"]).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(self.points_frame, text="Inserisci il numero di cerchi/caselle piene", 
                  font=('Arial', 8, 'italic')).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_discipline_bg_tab(self, notebook):
        """Crea il tab per Discipline e Background"""
        self.discipline_bg_frame = ttk.Frame(notebook, padding="10")
        
        ttk.Label(self.discipline_bg_frame, text="Discipline (es: Auspex 1, Demenza 2):", 
                  font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.discipline_bg_frame, textvariable=self.character_data["discipline"]).grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        ttk.Label(self.discipline_bg_frame, text="Background (es: Generazione 13, Risorse 2):", 
                  font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.discipline_bg_frame, textvariable=self.character_data["background"]).grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        self.discipline_bg_frame.columnconfigure(1, weight=1)
    
    def show_loading_screen(self, title="Operazione in corso"):
        """Mostra una schermata di caricamento modale"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title(title)
        self.loading_window.geometry("300x100")
        self.loading_window.resizable(False, False)
        
        # Centra la finestra
        self.loading_window.tk.call('tk::PlaceWindow', self.loading_window, 'center')
        
        # Rendi modale
        self.loading_window.grab_set()
        self.loading_window.transient(self.root)
        
        # Contenuto
        main_frame = ttk.Frame(self.loading_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Elaborazione in corso...", font=('Arial', 10)).pack(pady=5)
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(pady=5)
        self.progress_bar.start(10)
        
        # Impedisci la chiusura manuale
        self.loading_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Forza l'aggiornamento della finestra
        self.root.update_idletasks()
    
    def hide_loading_screen(self):
        """Nasconde la schermata di caricamento"""
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.grab_release()
            self.loading_window.destroy()
            self.loading_window = None
    
    def save_to_json(self):
        """Salva i dati del personaggio in un file JSON"""
        data = {
            "nome_pg": self.character_data["nome_pg"].get(),
            "player": self.character_data["player"].get(),
            "clan": self.character_data["clan"].get(),
            "generazione": self.character_data["generazione"].get(),
            "pregi": self.character_data["pregi"].get(),
            "difetti": self.character_data["difetti"].get(),
            "fisici": self.character_data["fisici"].get(),
            "sociali": self.character_data["sociali"].get(),
            "mentali": self.character_data["mentali"].get(),
            "punti_sangue": self.character_data["punti_sangue"].get(),
            "volonta": self.character_data["volonta"].get(),
            "umanita": self.character_data["umanita"].get(),
            "salute": self.character_data["salute"].get(),
            "discipline": self.character_data["discipline"].get(),
            "background": self.character_data["background"].get(),
            "skills": {}
        }
        
        for skill, values in self.character_data["skills"].items():
            data["skills"][skill] = {
                "active": values["active"].get(),
                "score": values["score"].get()
            }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Salva file JSON"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Successo", f"Dati salvati in {file_path}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")
    
    def load_from_json(self):
        """Carica i dati del personaggio da un file JSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Carica file JSON"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.character_data["nome_pg"].set(data.get("nome_pg", ""))
                self.character_data["player"].set(data.get("player", ""))
                self.character_data["clan"].set(data.get("clan", ""))
                self.character_data["generazione"].set(data.get("generazione", ""))
                # Supporto per vecchi file JSON con pregi_difetti
                if "pregi_difetti" in data:
                    # Se c'è il campo vecchio, lo dividiamo in pregi e difetti
                    pregi_difetti = data.get("pregi_difetti", "")
                    # Dividi per virgola o a capo
                    parts = pregi_difetti.replace("\r", ",").replace("\n", ",").split(",", 1)
                    self.character_data["pregi"].set(parts[0].strip() if len(parts) > 0 else "")
                    self.character_data["difetti"].set(parts[1].strip() if len(parts) > 1 else "")
                else:
                    self.character_data["pregi"].set(data.get("pregi", ""))
                    self.character_data["difetti"].set(data.get("difetti", ""))
                
                self.character_data["fisici"].set(data.get("fisici", 0))
                self.character_data["sociali"].set(data.get("sociali", 0))
                self.character_data["mentali"].set(data.get("mentali", 0))
                
                self.character_data["punti_sangue"].set(data.get("punti_sangue", 0))
                self.character_data["volonta"].set(data.get("volonta", 0))
                self.character_data["umanita"].set(data.get("umanita", 0))
                self.character_data["salute"].set(data.get("salute", 0))
                
                self.character_data["discipline"].set(data.get("discipline", ""))
                self.character_data["background"].set(data.get("background", ""))
                
                if "skills" in data:
                    for skill, values in data["skills"].items():
                        if skill in self.character_data["skills"]:
                            self.character_data["skills"][skill]["active"].set(values.get("active", False))
                            self.character_data["skills"][skill]["score"].set(values.get("score", 0))
                            self.toggle_skill_score(skill)
                
                messagebox.showinfo("Successo", f"Dati caricati da {file_path}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel caricamento: {str(e)}")
    
    def generate_png(self):
        """Genera il file PNG dalla scheda compilata"""
        try:
            self.show_loading_screen("Generazione PNG")
            self.root.update()
            
            with tempfile.NamedTemporaryFile(suffix='.psd', delete=False) as temp_psd:
                temp_psd_path = temp_psd.name
            
            shutil.copy2(self.psd_path, temp_psd_path)
            
            psd = PSDImage.open(temp_psd_path)
            
            self.modify_psd_layers(psd)
            
            output_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Salva immagine PNG"
            )
            
            if output_path:
                image = psd.composite()
                # Disegna il testo sull'immagine usando PIL
                self.draw_text_on_image(image)
                image.save(output_path, format='PNG')
                messagebox.showinfo("Successo", f"Scheda generata e salvata in {output_path}")
            
            os.unlink(temp_psd_path)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.hide_loading_screen()
    
    def generate_psd(self):
        """Genera il file PSD dalla scheda compilata"""
        try:
            self.show_loading_screen("Generazione PSD")
            self.root.update()
            
            with tempfile.NamedTemporaryFile(suffix='.psd', delete=False) as temp_psd:
                temp_psd_path = temp_psd.name
            
            shutil.copy2(self.psd_path, temp_psd_path)
            
            psd = PSDImage.open(temp_psd_path)
            
            self.modify_psd_layers(psd)
            
            output_path = filedialog.asksaveasfilename(
                defaultextension=".psd",
                filetypes=[("PSD files", "*.psd"), ("All files", "*.*")],
                title="Salva file PSD"
            )
            
            if output_path:
                psd.save(output_path)
                messagebox.showinfo("Successo", f"Scheda PSD generata e salvata in {output_path}")
            
            os.unlink(temp_psd_path)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella generazione PSD: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.hide_loading_screen()
    
    def draw_text_on_image(self, image):
        """Disegna il testo sull'immagine usando PIL e i font del template PSD (Walshes-Regular, VeteranTypewriter)."""
        draw = ImageDraw.Draw(image)
        
        # Configurazione dei font basata sull'analisi del PSD
        font_config = {
            # Layer principali (Walshes-Regular, 100pt)
            "Nome PG": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Player": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Clan": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Generazione": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Fisici": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Sociali": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Mentali": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Umanità/Sentiero": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Volontà": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Punti Sangue": {"name": "Walshes-Regular", "size": 100, "bold": False},
            "Salute": {"name": "Walshes-Regular", "size": 80, "bold": False},
            "Background": {"name": "Walshes-Regular", "size": 80, "bold": False},
            "Discipline": {"name": "Walshes-Regular", "size": 80, "bold": False},
            "Pregi&Difetti": {"name": "Walshes-Regular", "size": 80, "bold": False},
            "Pregi e Difetti": {"name": "Walshes-Regular", "size": 80, "bold": False},
            
            # Punteggi delle abilità (Walshes-Regular, 56pt)
            "Punteggio Agilità": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Armi da Fuoco": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Armi da Mischia": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Manualità": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Rissa": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Sopravvivenza": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Accademiche": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Affinità Animale": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Empatia": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Intimidire": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Autocontrollo": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Espressione Artistica": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Sotterfugio": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Intuito": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Investigare": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Medicina": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Occulto": {"name": "Walshes-Regular", "size": 56, "bold": False},
            "Punteggio Tecnologia": {"name": "Walshes-Regular", "size": 56, "bold": False},
            
            # Discipline e Background (Walshes-Regular, dimensioni specifiche)
            "discipline_text": {"name": "Walshes-Regular", "size": 83, "bold": False},
            "bg_text": {"name": "Walshes-Regular", "size": 64, "bold": False},
            
            # Layer con VeteranTypewriter
            "Mr. Prova": {"name": "VeteranTypewriter", "size": 89, "bold": False},
            "Genoveffo Rossi": {"name": "VeteranTypewriter", "size": 77, "bold": False},
            "Malkavian": {"name": "VeteranTypewriter", "size": 77, "bold": False},
            "13": {"name": "VeteranTypewriter", "size": 77, "bold": False},
        }
        
        # Funzione per caricare un font dalla cartella locale 'fonts/' o dal sistema
        def load_font(font_name, size, bold=False):
            font_dir = os.path.join(os.path.dirname(__file__), "fonts")
            font_path = None
            
            # Mappa dei font personalizzati ai file nella cartella fonts/
            font_files = {
                "Walshes-Regular": "walshes.otf",
                "VeteranTypewriter": "veteran typewriter.ttf",
            }
            
            if font_name in font_files:
                font_path = os.path.join(font_dir, font_files[font_name])
            
            # Prova a caricare il font locale
            if font_path and os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"Errore nel caricare {font_path}: {e}")
            
            # Fallback: prova a caricare il font dal sistema
            try:
                return ImageFont.truetype(font_name, size)
            except:
                pass
            
            # Fallback finale: font di default
            return ImageFont.load_default()
        
        # Disegna tutti i testi salvati nelle loro posizioni originali
        for layer_name, info in self.text_layers_info.items():
            bbox = info["bbox"]
            text = info["text"]
            
            # Sostituisci \r con \n per PIL (gestione dei capi di riga)
            text = text.replace("\r", "\n")
            
            # Calcola la posizione (centro del bbox)
            x = (bbox[0] + bbox[2]) // 2
            y = (bbox[1] + bbox[3]) // 2
            
            # Ottieni la configurazione del font per questo layer
            font_config_entry = font_config.get(layer_name, {"name": "Walshes-Regular", "size": 56, "bold": False})
            font = load_font(
                font_config_entry["name"],
                font_config_entry["size"],
                font_config_entry["bold"]
            )
            
            try:
                # Gestione testo multilinea
                if "\n" in text:
                    lines = text.split("\n")
                    ascent, descent = font.getmetrics()
                    line_height = (ascent + descent) * 0.75  # Riduce lo spazio tra le righe
                    total_height = len(lines) * line_height
                    
                    start_y = y - total_height // 2 + ascent
                    
                    for line in lines:
                        if line.strip():  # Salta righe vuote
                            width = font.getlength(line)
                            draw.text((x - width // 2, start_y), line, font=font, fill="black")
                            start_y += line_height
                        else:
                            # Per righe vuote, aggiungi solo metà dell'altezza per ridurre lo spazio
                            start_y += line_height * 0.5
                else:
                    # Disegna il testo con lo stesso contenuto del layer nascosto
                    draw.text((x, y), text, font=font, fill="black", anchor="mm")
            except Exception as e:
                # Se c'è un errore, usa il font di default
                print(f"Errore nel disegnare '{text}' con {font_config_entry}: {e}. Tentativo con font di default...")
                default_font = ImageFont.load_default()
                if "\n" in text:
                    lines = text.split("\n")
                    for i, line in enumerate(lines):
                        if line.strip():
                            draw.text((x, y + i * 15), line, font=default_font, fill="black")
                else:
                    draw.text((x, y), text, font=default_font, fill="black", anchor="mm")
    
    def modify_psd_layers(self, psd):
        """Modifica i layer del PSD in base ai dati del personaggio"""
        try:
            layer_map = {}
            # Chiamare psd.descendants() per ottenere l'elenco dei layer
            descendants = list(psd.descendants()) if hasattr(psd, 'descendants') and callable(psd.descendants) else []
            for layer in descendants:
                if hasattr(layer, 'name') and layer.name:
                    layer_map[layer.name] = layer
            
            self.update_text_layers(layer_map)
            self.update_skill_color_layers(layer_map)
            self.update_skill_score_layers(layer_map)
            self.update_attribute_layers(layer_map)
            self.update_blood_will_humanity_layers(layer_map)
            self.update_health_boxes(layer_map)
            self.update_discipline_bg_layers(layer_map)
        except Exception as e:
            raise RuntimeError(f"Errore nella modifica dei layer: {str(e)}") from e
    
    def update_text_layers(self, layer_map):
        """Salva le informazioni dei layer di testo (posizione e testo) e li nasconde."""
        
        text_updates = {
            "Mr. Prova": self.character_data["nome_pg"].get(),
            "Genoveffo Rossi": self.character_data["player"].get(),
            "Malkavian": self.character_data["clan"].get(),
            "13": str(self.character_data["generazione"].get() or ""),
        }
        
        for layer_name, text in text_updates.items():
            if layer_name in layer_map:
                layer = layer_map[layer_name]
                if hasattr(layer, 'kind') and layer.kind == 'type':
                    # Salva bbox e testo
                    if hasattr(layer, 'bbox'):
                        self.text_layers_info[layer_name] = {
                            "bbox": layer.bbox,
                            "text": text
                        }
                    # Nascondi il layer di testo originale
                    layer.visible = False
        
        pregi = self.character_data["pregi"].get() or ""
        difetti = self.character_data["difetti"].get() or ""
        
        # Separa pregi e difetti in linee se contengono virgole
        pregi_lines = [p.strip() for p in pregi.split(",") if p.strip()]
        difetti_lines = [d.strip() for d in difetti.split(",") if d.strip()]
        
        # Combina tutto in un testo multilinea con separazione tra pregi e difetti
        all_lines = pregi_lines
        if pregi_lines and difetti_lines:
            all_lines.append("")  # Aggiungi una riga vuota tra pregi e difetti
        all_lines.extend(difetti_lines)
        
        combined_text = "\n".join(all_lines)
        
        if "Pregi e Difetti" in layer_map:
            layer = layer_map["Pregi e Difetti"]
            if hasattr(layer, 'kind') and layer.kind == 'type':
                # Salva bbox e testo combinato
                if hasattr(layer, 'bbox'):
                    self.text_layers_info["Pregi e Difetti"] = {
                        "bbox": layer.bbox,
                        "text": combined_text
                    }
                # Nascondi il layer originale
                layer.visible = False
    
    def update_skill_color_layers(self, layer_map):
        """Mostra/nasconde i layer delle abilità in base allo stato attivo/disattivato"""
        
        for skill, values in self.character_data["skills"].items():
            active = values["active"].get()
            
            if skill in SKILL_COLOR_LAYERS:
                color_layer_name = SKILL_COLOR_LAYERS[skill]["color"]
                bn_layer_name = SKILL_COLOR_LAYERS[skill]["bn"]
                
                if color_layer_name and color_layer_name in layer_map:
                    layer_map[color_layer_name].visible = active
                
                if bn_layer_name and bn_layer_name in layer_map:
                    layer_map[bn_layer_name].visible = not active
    
    def update_skill_score_layers(self, layer_map):
        """Aggiorna i punteggi delle abilità (nascondendo i layer e salvando le info per il disegno)."""
        
        for skill, values in self.character_data["skills"].items():
            score = values["score"].get()
            layer_name = SKILL_SCORE_LAYERS.get(skill)
            
            if layer_name and layer_name in layer_map:
                layer = layer_map[layer_name]
                if hasattr(layer, 'kind') and layer.kind == 'type':
                    if hasattr(layer, 'bbox'):
                        self.text_layers_info[layer_name] = {
                            "bbox": layer.bbox,
                            "text": str(score)
                        }
                    layer.visible = False
    
    def update_attribute_layers(self, layer_map):
        """Aggiorna i cerchi degli attributi"""
        
        fisici = self.character_data["fisici"].get()
        sociali = self.character_data["sociali"].get()
        mentali = self.character_data["mentali"].get()
        

        for i in range(2, fisici+1):
            layer_map[f"fis{i}"].visible = True

        for i in range(2, sociali+1):
            layer_map[f"soc{i}"].visible = True

        for i in range(2, mentali+1):
            layer_map[f"men{i}"].visible = True
    
    def update_blood_will_humanity_layers(self, layer_map):
        """Aggiorna i cerchi di Punti Sangue, Volontà, Umanità"""
        
        punti_sangue = self.character_data["punti_sangue"].get()
        volonta = self.character_data["volonta"].get()
        umanita = self.character_data["umanita"].get()
        


        for i in range(6, punti_sangue+1):
            layer_map[f"B&N Punti Sangue {i}"].visible = False
        

        for i in range(2, volonta+1):
            layer_map[f"B&N Punti Volontà {i}"].visible = False
    

        for i in range(3, umanita+1):
            layer_map[f"B&N Punti Umanità {i}"].visible = False

    
    def update_health_boxes(self, layer_map):
        """Aggiorna le caselle di Salute"""
        
        salute = self.character_data["salute"].get()
        
        for i in range(6, salute+1):
            layer_map[f"PV{i}"].visible = True
    
    def update_discipline_bg_layers(self, layer_map):
        """Aggiorna i layer di Discipline e Background.
        
        I valori inseriti dall'utente sono separati da virgole.
        Esempio:
            Auspex 1, Demenza 2, Dominazione 3
        
        Nel PNG verranno visualizzati su righe separate.
        """

        # Recupera i valori inseriti
        discipline_raw = self.character_data["discipline"].get() or ""
        background_raw = self.character_data["background"].get() or ""

        # Divide per virgola, rimuove gli spazi inutili
        # e ignora eventuali elementi vuoti
        discipline = [
            item.strip()
            for item in discipline_raw.split(",")
            if item.strip()
        ]

        background = [
            item.strip()
            for item in background_raw.split(",")
            if item.strip()
        ]

        # Trasforma le liste in testo multilinea
        discipline_text = "\n".join(discipline)
        background_text = "\n".join(background)

        # -------------------------
        # DISCIPLINE
        # -------------------------
        if "discipline_text" in layer_map:
            layer = layer_map["discipline_text"]
            
            if hasattr(layer, "bbox"):
                self.text_layers_info["discipline_text"] = {
                    "bbox": layer.bbox,
                    "text": discipline_text
                }
            # Nasconde il layer originale del PSD (indipendentemente dal tipo)
            layer.visible = False

        # -------------------------
        # BACKGROUND
        # -------------------------
        if "bg_text" in layer_map:
            layer = layer_map["bg_text"]
            
            if hasattr(layer, "bbox"):
                self.text_layers_info["bg_text"] = {
                    "bbox": layer.bbox,
                    "text": background_text
                }
            # Nasconde il layer originale del PSD (indipendentemente dal tipo)
            layer.visible = False



if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterSheetApp(root)
    root.mainloop()
