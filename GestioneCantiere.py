import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
from tkinter import simpledialog

class GestioneCantiere:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestione Costi Cantiere")
        self.root.geometry("900x700")
        
        # Inizializzazione del database
        self.conn = self.init_database()
        
        # Creazione dell'interfaccia
        self.create_interface()
        
    def init_database(self):
        # Crea il database se non esiste
        conn = sqlite3.connect("cantieri.db")
        cursor = conn.cursor()
        
        # Crea tabelle se non esistono
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS materiali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            prezzo_unita REAL NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dipendenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tariffa_oraria REAL NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cantieri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cantiere_materiali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cantiere_id INTEGER NOT NULL,
            materiale_id INTEGER NOT NULL,
            quantita REAL NOT NULL,
            data DATE NOT NULL,
            FOREIGN KEY (cantiere_id) REFERENCES cantieri (id),
            FOREIGN KEY (materiale_id) REFERENCES materiali (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cantiere_dipendenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cantiere_id INTEGER NOT NULL,
            dipendente_id INTEGER NOT NULL,
            ore_lavorate REAL NOT NULL,
            data DATE NOT NULL,
            FOREIGN KEY (cantiere_id) REFERENCES cantieri (id),
            FOREIGN KEY (dipendente_id) REFERENCES dipendenti (id)
        )
        ''')
        
        conn.commit()
        return conn
        
    def create_interface(self):
        # Crea un notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crea i tab
        self.tab_materiali = ttk.Frame(self.notebook)
        self.tab_dipendenti = ttk.Frame(self.notebook)
        self.tab_cantieri = ttk.Frame(self.notebook)
        self.tab_cantiere_materiali = ttk.Frame(self.notebook)
        self.tab_cantiere_dipendenti = ttk.Frame(self.notebook)
        self.tab_riepilogo = ttk.Frame(self.notebook)
        
        # Aggiungi i tab al notebook
        self.notebook.add(self.tab_materiali, text="Materiali")
        self.notebook.add(self.tab_dipendenti, text="Dipendenti")
        self.notebook.add(self.tab_cantieri, text="Cantieri")
        self.notebook.add(self.tab_cantiere_materiali, text="Cantiere-Materiali")
        self.notebook.add(self.tab_cantiere_dipendenti, text="Cantiere-Dipendenti")
        self.notebook.add(self.tab_riepilogo, text="Riepilogo Costi")
        
        # Configura i tab
        self.setup_tab_materiali()
        self.setup_tab_dipendenti()
        self.setup_tab_cantieri()
        self.setup_tab_cantiere_materiali()
        self.setup_tab_cantiere_dipendenti()
        self.setup_tab_riepilogo()
    
    def setup_tab_materiali(self):
        # Frame per l'inserimento dei materiali
        frame_inserimento = ttk.LabelFrame(self.tab_materiali, text="Inserimento Materiali")
        frame_inserimento.pack(fill="x", padx=10, pady=10)
        
        # Nome materiale
        ttk.Label(frame_inserimento, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome_materiale = ttk.Entry(frame_inserimento, width=30)
        self.entry_nome_materiale.grid(row=0, column=1, padx=5, pady=5)
        
        # Prezzo unità
        ttk.Label(frame_inserimento, text="Prezzo Unità (€):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_prezzo_unita = ttk.Entry(frame_inserimento, width=10)
        self.entry_prezzo_unita.grid(row=0, column=3, padx=5, pady=5)
        
        # Pulsante per aggiungere materiale
        ttk.Button(frame_inserimento, text="Aggiungi Materiale", command=self.aggiungi_materiale).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame_inserimento, text="Elimina Materiale", command=self.elimina_materiale).grid(row=0, column=5, padx=5, pady=5)
        
        # Frame per visualizzare i materiali
        frame_visualizza = ttk.LabelFrame(self.tab_materiali, text="Lista Materiali")
        frame_visualizza.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i materiali
        self.tree_materiali = ttk.Treeview(frame_visualizza, columns=("ID", "Nome", "Prezzo Unità"), show="headings")
        self.tree_materiali.heading("ID", text="ID")
        self.tree_materiali.heading("Nome", text="Nome")
        self.tree_materiali.heading("Prezzo Unità", text="Prezzo Unità (€)")
        self.tree_materiali.column("ID", width=50)
        self.tree_materiali.column("Nome", width=250)
        self.tree_materiali.column("Prezzo Unità", width=150)
        self.tree_materiali.pack(fill="both", expand=True)
        
        # Carica i materiali al momento dell'avvio
        self.carica_materiali()
    
    def setup_tab_dipendenti(self):
        # Frame per l'inserimento dei dipendenti
        frame_inserimento = ttk.LabelFrame(self.tab_dipendenti, text="Inserimento Dipendenti")
        frame_inserimento.pack(fill="x", padx=10, pady=10)
        
        # Nome dipendente
        ttk.Label(frame_inserimento, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome_dipendente = ttk.Entry(frame_inserimento, width=30)
        self.entry_nome_dipendente.grid(row=0, column=1, padx=5, pady=5)
        
        # Tariffa oraria
        ttk.Label(frame_inserimento, text="Tariffa Oraria (€):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_tariffa_oraria = ttk.Entry(frame_inserimento, width=10)
        self.entry_tariffa_oraria.grid(row=0, column=3, padx=5, pady=5)
        
        # Pulsante per aggiungere dipendente
        ttk.Button(frame_inserimento, text="Aggiungi Dipe", command=self.aggiungi_dipendente).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame_inserimento, text="Elimina Dipe", command=self.elimina_dipendente).grid(row=0, column=5, padx=5, pady=5)
        
        # Frame per visualizzare i dipendenti
        frame_visualizza = ttk.LabelFrame(self.tab_dipendenti, text="Lista Dipendenti")
        frame_visualizza.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i dipendenti
        self.tree_dipendenti = ttk.Treeview(frame_visualizza, columns=("ID", "Nome", "Tariffa Oraria"), show="headings")
        self.tree_dipendenti.heading("ID", text="ID")
        self.tree_dipendenti.heading("Nome", text="Nome")
        self.tree_dipendenti.heading("Tariffa Oraria", text="Tariffa Oraria (€)")
        self.tree_dipendenti.column("ID", width=50)
        self.tree_dipendenti.column("Nome", width=250)
        self.tree_dipendenti.column("Tariffa Oraria", width=150)
        self.tree_dipendenti.pack(fill="both", expand=True)
        
        # Carica i dipendenti al momento dell'avvio
        self.carica_dipendenti()
    
    def setup_tab_cantieri(self):
        # Frame per l'inserimento dei cantieri
        frame_inserimento = ttk.LabelFrame(self.tab_cantieri, text="Inserimento Cantieri")
        frame_inserimento.pack(fill="x", padx=10, pady=10)
        
        # Nome cantiere
        ttk.Label(frame_inserimento, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome_cantiere = ttk.Entry(frame_inserimento, width=30)
        self.entry_nome_cantiere.grid(row=0, column=1, padx=5, pady=5)
        
        # Pulsante per aggiungere cantiere
        ttk.Button(frame_inserimento, text="Aggiungi Cantiere", command=self.aggiungi_cantiere).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame_inserimento, text="Elimina Cantiere", command=self.elimina_cantiere).grid(row=0, column=3, padx=5, pady=5)
        
        # Frame per visualizzare i cantieri
        frame_visualizza = ttk.LabelFrame(self.tab_cantieri, text="Lista Cantieri")
        frame_visualizza.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i cantieri
        self.tree_cantieri = ttk.Treeview(frame_visualizza, columns=("ID", "Nome"), show="headings")
        self.tree_cantieri.heading("ID", text="ID")
        self.tree_cantieri.heading("Nome", text="Nome")
        self.tree_cantieri.column("ID", width=50)
        self.tree_cantieri.column("Nome", width=400)
        self.tree_cantieri.pack(fill="both", expand=True)
        
        # Carica i cantieri al momento dell'avvio
        self.carica_cantieri()
    
    def setup_tab_cantiere_materiali(self):
        # Frame per la selezione del cantiere
        frame_selezione_cantiere = ttk.LabelFrame(self.tab_cantiere_materiali, text="Selezione Cantiere")
        frame_selezione_cantiere.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_selezione_cantiere, text="Cantiere:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_cantiere_materiali = ttk.Combobox(frame_selezione_cantiere, width=30)
        self.combo_cantiere_materiali.grid(row=0, column=1, padx=5, pady=5)
        self.combo_cantiere_materiali.bind("<<ComboboxSelected>>", self.aggiorna_cantiere_materiali)
        
        # Frame per l'inserimento dei materiali nel cantiere
        frame_inserimento = ttk.LabelFrame(self.tab_cantiere_materiali, text="Inserimento Materiali nel Cantiere")
        frame_inserimento.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_inserimento, text="Materiale:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_materiale = ttk.Combobox(frame_inserimento, width=30)
        self.combo_materiale.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_inserimento, text="Quantità:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_quantita = ttk.Entry(frame_inserimento, width=10)
        self.entry_quantita.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_inserimento, text="Data (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_data_materiale = ttk.Entry(frame_inserimento, width=12)
        self.entry_data_materiale.grid(row=0, column=5, padx=5, pady=5)
        # Inserisci data odierna di default
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_data_materiale.insert(0, today)
        
        ttk.Button(frame_inserimento, text="Aggiungi", command=self.aggiungi_materiale_cantiere).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(frame_inserimento, text="Elimina", command=self.elimina_materiale_cantiere).grid(row=0, column=7, padx=5, pady=5)
        
        # Frame per visualizzare i materiali nel cantiere
        frame_visualizza = ttk.LabelFrame(self.tab_cantiere_materiali, text="Materiali nel Cantiere")
        frame_visualizza.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i materiali nel cantiere
        self.tree_cantiere_materiali = ttk.Treeview(frame_visualizza, 
                                                   columns=("ID", "Materiale", "Quantità", "Prezzo Unità", "Costo", "Data"), 
                                                   show="headings")
        self.tree_cantiere_materiali.heading("ID", text="ID")
        self.tree_cantiere_materiali.heading("Materiale", text="Materiale")
        self.tree_cantiere_materiali.heading("Quantità", text="Quantità")
        self.tree_cantiere_materiali.heading("Prezzo Unità", text="Prezzo Unità (€)")
        self.tree_cantiere_materiali.heading("Costo", text="Costo (€)")
        self.tree_cantiere_materiali.heading("Data", text="Data")
        self.tree_cantiere_materiali.column("ID", width=50)
        self.tree_cantiere_materiali.column("Materiale", width=200)
        self.tree_cantiere_materiali.column("Quantità", width=80)
        self.tree_cantiere_materiali.column("Prezzo Unità", width=100)
        self.tree_cantiere_materiali.column("Costo", width=100)
        self.tree_cantiere_materiali.column("Data", width=100)
        self.tree_cantiere_materiali.pack(fill="both", expand=True)
        
        # Label per il totale
        self.label_totale_materiali = ttk.Label(frame_visualizza, text="Totale: 0.00 €", font=("Arial", 12, "bold"))
        self.label_totale_materiali.pack(anchor="e", padx=10, pady=5)
        
        # Popola i combobox
        self.carica_cantieri_combobox()
        self.carica_materiali_combobox()
        
        print(vars(self))  # Mostra tutti gli attributi dell'oggetto

    
    def setup_tab_cantiere_dipendenti(self):
        # Frame per la selezione del cantiere
        frame_selezione_cantiere = ttk.LabelFrame(self.tab_cantiere_dipendenti, text="Selezione Cantiere")
        frame_selezione_cantiere.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_selezione_cantiere, text="Cantiere:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_cantiere_dipendenti = ttk.Combobox(frame_selezione_cantiere, width=30)
        self.combo_cantiere_dipendenti.grid(row=0, column=1, padx=5, pady=5)
        self.combo_cantiere_dipendenti.bind("<<ComboboxSelected>>", self.aggiorna_cantiere_dipendenti)
        
        # Frame per l'inserimento dei dipendenti nel cantiere
        frame_inserimento = ttk.LabelFrame(self.tab_cantiere_dipendenti, text="Inserimento Dipendenti nel Cantiere")
        frame_inserimento.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_inserimento, text="Dipendente:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_dipendente = ttk.Combobox(frame_inserimento, width=30)
        self.combo_dipendente.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_inserimento, text="Ore Lavorate:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_ore_lavorate = ttk.Entry(frame_inserimento, width=10)
        self.entry_ore_lavorate.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_inserimento, text="Data (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_data_dipendente = ttk.Entry(frame_inserimento, width=12)
        self.entry_data_dipendente.grid(row=0, column=5, padx=5, pady=5)
        # Inserisci data odierna di default
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_data_dipendente.insert(0, today)
        
        ttk.Button(frame_inserimento, text="Aggiungi", command=self.aggiungi_dipendente_cantiere).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(frame_inserimento, text="Elimina", command=self.elimina_dipendente_cantiere).grid(row=0, column=7, padx=5, pady=5)
        
        # Frame per visualizzare i dipendenti nel cantiere
        frame_visualizza = ttk.LabelFrame(self.tab_cantiere_dipendenti, text="Dipendenti nel Cantiere")
        frame_visualizza.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i dipendenti nel cantiere
        self.tree_cantiere_dipendenti = ttk.Treeview(frame_visualizza, 
                                                   columns=("ID", "Dipendente", "Ore Lavorate", "Tariffa Oraria", "Costo", "Data"), 
                                                   show="headings")
        self.tree_cantiere_dipendenti.heading("ID", text="ID")
        self.tree_cantiere_dipendenti.heading("Dipendente", text="Dipendente")
        self.tree_cantiere_dipendenti.heading("Ore Lavorate", text="Ore Lavorate")
        self.tree_cantiere_dipendenti.heading("Tariffa Oraria", text="Tariffa Oraria (€)")
        self.tree_cantiere_dipendenti.heading("Costo", text="Costo (€)")
        self.tree_cantiere_dipendenti.heading("Data", text="Data")
        self.tree_cantiere_dipendenti.column("ID", width=50)
        self.tree_cantiere_dipendenti.column("Dipendente", width=200)
        self.tree_cantiere_dipendenti.column("Ore Lavorate", width=100)
        self.tree_cantiere_dipendenti.column("Tariffa Oraria", width=100)
        self.tree_cantiere_dipendenti.column("Costo", width=100)
        self.tree_cantiere_dipendenti.column("Data", width=100)
        self.tree_cantiere_dipendenti.pack(fill="both", expand=True)
        
        # Label per il totale
        self.label_totale_dipendenti = ttk.Label(frame_visualizza, text="Totale: 0.00 €", font=("Arial", 12, "bold"))
        self.label_totale_dipendenti.pack(anchor="e", padx=10, pady=5)
        
        # Popola i combobox
        self.carica_cantieri_combobox()
        self.carica_dipendenti_combobox()
    
    def setup_tab_riepilogo(self):
        # Frame per la selezione del cantiere
        frame_selezione_cantiere = ttk.LabelFrame(self.tab_riepilogo, text="Selezione Cantiere")
        frame_selezione_cantiere.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_selezione_cantiere, text="Cantiere:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_cantiere_riepilogo = ttk.Combobox(frame_selezione_cantiere, width=30)
        self.combo_cantiere_riepilogo.grid(row=0, column=1, padx=5, pady=5)
        self.combo_cantiere_riepilogo.bind("<<ComboboxSelected>>", self.aggiorna_riepilogo)
        
        # Frame per il riepilogo dei materiali
        frame_riepilogo_materiali = ttk.LabelFrame(self.tab_riepilogo, text="Riepilogo Materiali")
        frame_riepilogo_materiali.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i materiali nel riepilogo
        self.tree_riepilogo_materiali = ttk.Treeview(frame_riepilogo_materiali, 
                                                   columns=("Materiale", "Quantità", "Prezzo Unità", "Costo", "Data"), 
                                                   show="headings")
        self.tree_riepilogo_materiali.heading("Materiale", text="Materiale")
        self.tree_riepilogo_materiali.heading("Quantità", text="Quantità")
        self.tree_riepilogo_materiali.heading("Prezzo Unità", text="Prezzo Unità (€)")
        self.tree_riepilogo_materiali.heading("Costo", text="Costo (€)")
        self.tree_riepilogo_materiali.heading("Data", text="Data")
        self.tree_riepilogo_materiali.column("Materiale", width=200)
        self.tree_riepilogo_materiali.column("Quantità", width=80)
        self.tree_riepilogo_materiali.column("Prezzo Unità", width=100)
        self.tree_riepilogo_materiali.column("Costo", width=100)
        self.tree_riepilogo_materiali.column("Data", width=100)
        self.tree_riepilogo_materiali.pack(fill="both", expand=True)
        
        # Label per il totale materiali
        self.label_totale_riepilogo_materiali = ttk.Label(frame_riepilogo_materiali, text="Totale Materiali: 0.00 €", font=("Arial", 12, "bold"))
        self.label_totale_riepilogo_materiali.pack(anchor="e", padx=10, pady=5)
        
        # Frame per il riepilogo dei dipendenti
        frame_riepilogo_dipendenti = ttk.LabelFrame(self.tab_riepilogo, text="Riepilogo Dipendenti")
        frame_riepilogo_dipendenti.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview per visualizzare i dipendenti nel riepilogo
        self.tree_riepilogo_dipendenti = ttk.Treeview(frame_riepilogo_dipendenti, 
                                                   columns=("Dipendente", "Ore Lavorate", "Tariffa Oraria", "Costo", "Data"), 
                                                   show="headings")
        self.tree_riepilogo_dipendenti.heading("Dipendente", text="Dipendente")
        self.tree_riepilogo_dipendenti.heading("Ore Lavorate", text="Ore Lavorate")
        self.tree_riepilogo_dipendenti.heading("Tariffa Oraria", text="Tariffa Oraria (€)")
        self.tree_riepilogo_dipendenti.heading("Costo", text="Costo (€)")
        self.tree_riepilogo_dipendenti.heading("Data", text="Data")
        self.tree_riepilogo_dipendenti.column("Dipendente", width=200)
        self.tree_riepilogo_dipendenti.column("Ore Lavorate", width=100)
        self.tree_riepilogo_dipendenti.column("Tariffa Oraria", width=100)
        self.tree_riepilogo_dipendenti.column("Costo", width=100)
        self.tree_riepilogo_dipendenti.column("Data", width=100)
        self.tree_riepilogo_dipendenti.pack(fill="both", expand=True)
        
        # Label per il totale dipendenti
        self.label_totale_riepilogo_dipendenti = ttk.Label(frame_riepilogo_dipendenti, text="Totale Dipendenti: 0.00 €", font=("Arial", 12, "bold"))
        self.label_totale_riepilogo_dipendenti.pack(anchor="e", padx=10, pady=5)
        
        # Label per il totale generale
        self.label_totale_generale = ttk.Label(self.tab_riepilogo, text="TOTALE GENERALE: 0.00 €", font=("Arial", 14, "bold"))
        self.label_totale_generale.pack(anchor="e", padx=10, pady=10)
        
        # Popola il combobox
        self.carica_cantieri_combobox()
    
    # Funzioni per la gestione dei materiali
    def carica_materiali(self):
        # Svuota la visualizzazione
        for item in self.tree_materiali.get_children():
            self.tree_materiali.delete(item)
        
        # Carica i materiali dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, prezzo_unita FROM materiali ORDER BY nome")
        materiali = cursor.fetchall()
        
        # Inserisci i materiali nella treeview
        for materiale in materiali:
            self.tree_materiali.insert("", "end", values=materiale)
    
    def aggiungi_materiale(self):
        nome = self.entry_nome_materiale.get().strip()
        prezzo_unita = self.entry_prezzo_unita.get().strip()
        
        if not nome or not prezzo_unita:
            messagebox.showerror("Errore", "Inserisci tutti i campi!")
            return
        
        try:
            prezzo_unita = float(prezzo_unita)
            if prezzo_unita < 0:
                messagebox.showerror("Errore", "Il prezzo deve essere positivo!")
                return
        except ValueError:
            messagebox.showerror("Errore", "Il prezzo deve essere un numero valido!")
            return
        
        # Inserisci il materiale nel database
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO materiali (nome, prezzo_unita) VALUES (?, ?)", (nome, prezzo_unita))
            self.conn.commit()
            
            # Pulisci i campi
            self.entry_nome_materiale.delete(0, tk.END)
            self.entry_prezzo_unita.delete(0, tk.END)
            
            # Aggiorna la visualizzazione
            self.carica_materiali()
            self.carica_materiali_combobox()
            
            messagebox.showinfo("Successo", f"Materiale '{nome}' aggiunto con successo!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Errore", f"Il materiale '{nome}' esiste già!")
    
    def elimina_materiale(self):
        # Ottieni l'ID del materiale selezionato
        selection = self.tree_materiali.selection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un materiale da eliminare!")
            return
        
        item = self.tree_materiali.item(selection[0])
        materiale_id = item["values"][0]
        materiale_nome = item["values"][1]
        
        # Verifica se il materiale è utilizzato in un cantiere
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cantiere_materiali WHERE materiale_id = ?", (materiale_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            messagebox.showerror("Errore", f"Impossibile eliminare il materiale '{materiale_nome}' perché è utilizzato in {count} cantieri!")
            return
        
        # Conferma l'eliminazione
        confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare il materiale '{materiale_nome}'?")
        if not confirm:
            return
        
        # Elimina il materiale
        cursor.execute("DELETE FROM materiali WHERE id = ?", (materiale_id,))
        self.conn.commit()
        
        # Aggiorna la visualizzazione
        self.carica_materiali()
        self.carica_materiali_combobox()
        
        messagebox.showinfo("Successo", f"Materiale '{materiale_nome}' eliminato con successo!")

    def carica_dipendenti(self):
        # Svuota la visualizzazione
        for item in self.tree_dipendenti.get_children():
            self.tree_dipendenti.delete(item)
        
        # Carica i dipendenti dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, tariffa_oraria FROM dipendenti ORDER BY nome")
        dipendenti = cursor.fetchall()
        
        # Inserisci i dipendenti nella treeview
        for dipendente in dipendenti:
            self.tree_dipendenti.insert("", "end", values=dipendente)

    def aggiungi_dipendente(self):
        nome = self.entry_nome_dipendente.get().strip()
        tariffa_oraria = self.entry_tariffa_oraria.get().strip()
        
        if not nome or not tariffa_oraria:
            messagebox.showerror("Errore", "Inserisci tutti i campi!")
            return
        
        try:
            tariffa_oraria = float(tariffa_oraria)
            if tariffa_oraria < 0:
                messagebox.showerror("Errore", "La tariffa oraria deve essere positiva!")
                return
        except ValueError:
            messagebox.showerror("Errore", "La tariffa oraria deve essere un numero valido!")
            return
        
        # Inserisci il dipendente nel database
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO dipendenti (nome, tariffa_oraria) VALUES (?, ?)", (nome, tariffa_oraria))
            self.conn.commit()
            
            # Pulisci i campi
            self.entry_nome_dipendente.delete(0, tk.END)
            self.entry_tariffa_oraria.delete(0, tk.END)
            
            # Aggiorna la visualizzazione
            self.carica_dipendenti()
            self.carica_dipendenti_combobox()
            
            messagebox.showinfo("Successo", f"Dipendente '{nome}' aggiunto con successo!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Errore", f"Il dipendente '{nome}' esiste già!")

    def elimina_dipendente(self):
        # Ottieni l'ID del dipendente selezionato
        selection = self.tree_dipendenti.selection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un dipendente da eliminare!")
            return
        
        item = self.tree_dipendenti.item(selection[0])
        dipendente_id = item["values"][0]
        dipendente_nome = item["values"][1]
        
        # Verifica se il dipendente è utilizzato in un cantiere
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cantiere_dipendenti WHERE dipendente_id = ?", (dipendente_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            messagebox.showerror("Errore", f"Impossibile eliminare il dipendente '{dipendente_nome}' perché è utilizzato in {count} cantieri!")
            return
        
        # Conferma l'eliminazione
        confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare il dipendente '{dipendente_nome}'?")
        if not confirm:
            return
        
        # Elimina il dipendente
        cursor.execute("DELETE FROM dipendenti WHERE id = ?", (dipendente_id,))
        self.conn.commit()
        
        # Aggiorna la visualizzazione
        self.carica_dipendenti()
        self.carica_dipendenti_combobox()
        
        messagebox.showinfo("Successo", f"Dipendente '{dipendente_nome}' eliminato con successo!")

    def carica_cantieri(self):
        # Svuota la visualizzazione
        for item in self.tree_cantieri.get_children():
            self.tree_cantieri.delete(item)
        
        # Carica i cantieri dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM cantieri ORDER BY nome")
        cantieri = cursor.fetchall()
        
        # Inserisci i cantieri nella treeview
        for cantiere in cantieri:
            self.tree_cantieri.insert("", "end", values=cantiere)

    def aggiungi_cantiere(self):
        nome = self.entry_nome_cantiere.get().strip()
        
        if not nome:
            messagebox.showerror("Errore", "Inserisci il nome del cantiere!")
            return
        
        # Inserisci il cantiere nel database
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO cantieri (nome) VALUES (?)", (nome,))
            self.conn.commit()
            
            # Pulisci i campi
            self.entry_nome_cantiere.delete(0, tk.END)
            
            # Aggiorna la visualizzazione
            self.carica_cantieri()
            self.carica_cantieri_combobox()
            
            messagebox.showinfo("Successo", f"Cantiere '{nome}' aggiunto con successo!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Errore", f"Il cantiere '{nome}' esiste già!")

    def elimina_cantiere(self):
        # Ottieni l'ID del cantiere selezionato
        selection = self.tree_cantieri.selection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un cantiere da eliminare!")
            return
        
        item = self.tree_cantieri.item(selection[0])
        cantiere_id = item["values"][0]
        cantiere_nome = item["values"][1]
        
        # Verifica se ci sono materiali o dipendenti associati al cantiere
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cantiere_materiali WHERE cantiere_id = ?", (cantiere_id,))
        count_materiali = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cantiere_dipendenti WHERE cantiere_id = ?", (cantiere_id,))
        count_dipendenti = cursor.fetchone()[0]
        
        if count_materiali > 0 or count_dipendenti > 0:
            messagebox.showerror("Errore", f"Impossibile eliminare il cantiere '{cantiere_nome}' perché ha {count_materiali} materiali e {count_dipendenti} dipendenti associati!")
            return
        
        # Conferma l'eliminazione
        confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare il cantiere '{cantiere_nome}'?")
        if not confirm:
            return
        
        # Elimina il cantiere
        cursor.execute("DELETE FROM cantieri WHERE id = ?", (cantiere_id,))
        self.conn.commit()
        
        # Aggiorna la visualizzazione
        self.carica_cantieri()
        self.carica_cantieri_combobox()
        
        messagebox.showinfo("Successo", f"Cantiere '{cantiere_nome}' eliminato con successo!")

    def carica_cantieri_combobox(self):
        # Carica i cantieri dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM cantieri ORDER BY nome")
        cantieri = cursor.fetchall()
        
        # Prepara i dati per i combobox
        cantieri_data = {}
        cantieri_nomi = []
        
        for cantiere in cantieri:
            cantieri_data[cantiere[1]] = cantiere[0]
            cantieri_nomi.append(cantiere[1])
        
        # Aggiorna i combobox
        self.combo_cantiere_materiali['values'] = cantieri_nomi
        self.combo_cantiere_dipendenti['values'] = cantieri_nomi
        self.combo_cantiere_riepilogo['values'] = cantieri_nomi
        
        # Memorizza i dati per un uso successivo
        self.cantieri_data = cantieri_data

    def carica_materiali_combobox(self):
        # Carica i materiali dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM materiali ORDER BY nome")
        materiali = cursor.fetchall()
        
        # Prepara i dati per il combobox
        materiali_data = {}
        materiali_nomi = []
        
        for materiale in materiali:
            materiali_data[materiale[1]] = materiale[0]
            materiali_nomi.append(materiale[1])
        
        # Aggiorna il combobox
        self.combo_materiale['values'] = materiali_nomi
        
        # Memorizza i dati per un uso successivo
        self.materiali_data = materiali_data

    def carica_dipendenti_combobox(self):
        # Carica i dipendenti dal database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM dipendenti ORDER BY nome")
        dipendenti = cursor.fetchall()
        
        # Prepara i dati per il combobox
        dipendenti_data = {}
        dipendenti_nomi = []
        
        for dipendente in dipendenti:
            dipendenti_data[dipendente[1]] = dipendente[0]
            dipendenti_nomi.append(dipendente[1])
        
        # Aggiorna il combobox
        self.combo_dipendente['values'] = dipendenti_nomi
        
        # Memorizza i dati per un uso successivo
        self.dipendenti_data = dipendenti_data

    def aggiorna_cantiere_materiali(self, event=None):
        cantiere_nome = self.combo_cantiere_materiali.get()
        if not cantiere_nome:
            return
        
        cantiere_id = self.cantieri_data.get(cantiere_nome)
        if not cantiere_id:
            return
        
        # Svuota la visualizzazione
        for item in self.tree_cantiere_materiali.get_children():
            self.tree_cantiere_materiali.delete(item)
        
        # Carica i materiali del cantiere dal database
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cm.id, m.nome, cm.quantita, m.prezzo_unita, (cm.quantita * m.prezzo_unita), cm.data
            FROM cantiere_materiali cm
            JOIN materiali m ON cm.materiale_id = m.id
            WHERE cm.cantiere_id = ?
            ORDER BY cm.data DESC
        """, (cantiere_id,))
        
        materiali = cursor.fetchall()
        
        # Inserisci i materiali nella treeview
        for materiale in materiali:
            self.tree_cantiere_materiali.insert("", "end", values=materiale)
        
        # Calcola e mostra il totale
        totale = sum(materiale[4] for materiale in materiali)
        self.label_totale_materiali.configure(text=f"Totale: {totale:.2f} €")

    def aggiungi_materiale_cantiere(self):
        cantiere_nome = self.combo_cantiere_materiali.get()
        materiale_nome = self.combo_materiale.get()
        quantita = self.entry_quantita.get().strip()
        data = self.entry_data_materiale.get().strip()
        
        if not cantiere_nome or not materiale_nome or not quantita or not data:
            messagebox.showerror("Errore", "Inserisci tutti i campi!")
            return
        
        cantiere_id = self.cantieri_data.get(cantiere_nome)
        materiale_id = self.materiali_data.get(materiale_nome)
        
        if not cantiere_id or not materiale_id:
            messagebox.showerror("Errore", "Cantiere o materiale non valido!")
            return
        
        try:
            quantita = float(quantita)
            if quantita <= 0:
                messagebox.showerror("Errore", "La quantità deve essere positiva!")
                return
        except ValueError:
            messagebox.showerror("Errore", "La quantità deve essere un numero valido!")
            return
        
        try:
            # Verifica il formato della data
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Errore", "Il formato della data deve essere YYYY-MM-DD!")
            return
        
        # Inserisci il materiale nel cantiere
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cantiere_materiali (cantiere_id, materiale_id, quantita, data)
            VALUES (?, ?, ?, ?)
        """, (cantiere_id, materiale_id, quantita, data))
        
        self.conn.commit()
        
        # Pulisci i campi
        self.entry_quantita.delete(0, tk.END)
        # Lascia la data com'è
        
        # Aggiorna la visualizzazione
        self.aggiorna_cantiere_materiali()
        
        messagebox.showinfo("Successo", f"Materiale '{materiale_nome}' aggiunto al cantiere '{cantiere_nome}'!")

    def elimina_materiale_cantiere(self):
        # Ottieni l'ID del materiale selezionato
        selection = self.tree_cantiere_materiali.selection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un materiale da eliminare!")
            return
        
        item = self.tree_cantiere_materiali.item(selection[0])
        record_id = item["values"][0]
        materiale_nome = item["values"][1]
        
        # Conferma l'eliminazione
        confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare il materiale '{materiale_nome}' da questo cantiere?")
        if not confirm:
            return
        
        # Elimina il materiale dal cantiere
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cantiere_materiali WHERE id = ?", (record_id,))
        self.conn.commit()
        
        # Aggiorna la visualizzazione
        self.aggiorna_cantiere_materiali()
        
        messagebox.showinfo("Successo", f"Materiale '{materiale_nome}' eliminato dal cantiere!")

    def aggiorna_cantiere_dipendenti(self, event=None):
        cantiere_nome = self.combo_cantiere_dipendenti.get()
        if not cantiere_nome:
            return
        
        cantiere_id = self.cantieri_data.get(cantiere_nome)
        if not cantiere_id:
            return
        
        # Svuota la visualizzazione
        for item in self.tree_cantiere_dipendenti.get_children():
            self.tree_cantiere_dipendenti.delete(item)
        
        # Carica i dipendenti del cantiere dal database
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cd.id, d.nome, cd.ore_lavorate, d.tariffa_oraria, (cd.ore_lavorate * d.tariffa_oraria), cd.data
            FROM cantiere_dipendenti cd
            JOIN dipendenti d ON cd.dipendente_id = d.id
            WHERE cd.cantiere_id = ?
            ORDER BY cd.data DESC
        """, (cantiere_id,))
        
        dipendenti = cursor.fetchall()
        
        # Inserisci i dipendenti nella treeview
        for dipendente in dipendenti:
            self.tree_cantiere_dipendenti.insert("", "end", values=dipendente)
        
        # Calcola e mostra il totale
        totale = sum(dipendente[4] for dipendente in dipendenti)
        self.label_totale_dipendenti.configure(text=f"Totale: {totale:.2f} €")

    def aggiungi_dipendente_cantiere(self):
        cantiere_nome = self.combo_cantiere_dipendenti.get()
        dipendente_nome = self.combo_dipendente.get()
        ore_lavorate = self.entry_ore_lavorate.get().strip()
        data = self.entry_data_dipendente.get().strip()
        
        if not cantiere_nome or not dipendente_nome or not ore_lavorate or not data:
            messagebox.showerror("Errore", "Inserisci tutti i campi!")
            return
        
        cantiere_id = self.cantieri_data.get(cantiere_nome)
        dipendente_id = self.dipendenti_data.get(dipendente_nome)
        
        if not cantiere_id or not dipendente_id:
            messagebox.showerror("Errore", "Cantiere o dipendente non valido!")
            return
        
        try:
            ore_lavorate = float(ore_lavorate)
            if ore_lavorate <= 0:
                messagebox.showerror("Errore", "Le ore lavorate devono essere positive!")
                return
        except ValueError:
            messagebox.showerror("Errore", "Le ore lavorate devono essere un numero valido!")
            return
        
        try:
            # Verifica il formato della data
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Errore", "Il formato della data deve essere YYYY-MM-DD!")
            return
        
        # Inserisci il dipendente nel cantiere
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cantiere_dipendenti (cantiere_id, dipendente_id, ore_lavorate, data)
            VALUES (?, ?, ?, ?)
        """, (cantiere_id, dipendente_id, ore_lavorate, data))
        
        self.conn.commit()
        
        # Pulisci i campi
        self.entry_ore_lavorate.delete(0, tk.END)
        # Lascia la data com'è
        
        # Aggiorna la visualizzazione
        self.aggiorna_cantiere_dipendenti()
        
        messagebox.showinfo("Successo", f"Dipendente '{dipendente_nome}' aggiunto al cantiere '{cantiere_nome}'!")

    def elimina_dipendente_cantiere(self):
        # Ottieni l'ID del dipendente selezionato
        selection = self.tree_cantiere_dipendenti.selection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un dipendente da eliminare!")
            return
        
        item = self.tree_cantiere_dipendenti.item(selection[0])
        record_id = item["values"][0]
        dipendente_nome = item["values"][1]
        
        # Conferma l'eliminazione
        confirm = messagebox.askyesno("Conferma", f"Sei sicuro di voler eliminare il dipendente '{dipendente_nome}' da questo cantiere?")
        if not confirm:
            return
        
        # Elimina il dipendente dal cantiere
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM cantiere_dipendenti WHERE id = ?", (record_id,))
        self.conn.commit()
        
        # Aggiorna la visualizzazione
        self.aggiorna_cantiere_dipendenti()
        
        messagebox.showinfo("Successo", f"Dipendente '{dipendente_nome}' eliminato dal cantiere!")

    def aggiorna_riepilogo(self, event=None):
        cantiere_nome = self.combo_cantiere_riepilogo.get()
        if not cantiere_nome:
            return
        
        cantiere_id = self.cantieri_data.get(cantiere_nome)
        if not cantiere_id:
            return
        
        # Svuota le visualizzazioni
        for item in self.tree_riepilogo_materiali.get_children():
            self.tree_riepilogo_materiali.delete(item)
        
        for item in self.tree_riepilogo_dipendenti.get_children():
            self.tree_riepilogo_dipendenti.delete(item)
        
        # Carica i materiali del cantiere dal database
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.nome, cm.quantita, m.prezzo_unita, (cm.quantita * m.prezzo_unita), cm.data
            FROM cantiere_materiali cm
            JOIN materiali m ON cm.materiale_id = m.id
            WHERE cm.cantiere_id = ?
            ORDER BY cm.data DESC
        """, (cantiere_id,))
        
        materiali = cursor.fetchall()
        
        # Inserisci i materiali nella treeview
        for materiale in materiali:
            self.tree_riepilogo_materiali.insert("", "end", values=materiale)
        
        # Calcola e mostra il totale materiali
        totale_materiali = sum(materiale[3] for materiale in materiali)
        self.label_totale_riepilogo_materiali.configure(text=f"Totale Materiali: {totale_materiali:.2f} €")
        
        # Carica i dipendenti del cantiere dal database
        cursor.execute("""
            SELECT d.nome, cd.ore_lavorate, d.tariffa_oraria, (cd.ore_lavorate * d.tariffa_oraria), cd.data
            FROM cantiere_dipendenti cd
            JOIN dipendenti d ON cd.dipendente_id = d.id
            WHERE cd.cantiere_id = ?
            ORDER BY cd.data DESC
        """, (cantiere_id,))
        
        dipendenti = cursor.fetchall()
        
        # Inserisci i dipendenti nella treeview
        for dipendente in dipendenti:
            self.tree_riepilogo_dipendenti.insert("", "end", values=dipendente)
        
        # Calcola e mostra il totale dipendenti
        totale_dipendenti = sum(dipendente[3] for dipendente in dipendenti)
        self.label_totale_riepilogo_dipendenti.configure(text=f"Totale Dipendenti: {totale_dipendenti:.2f} €")
        
        # Calcola e mostra il totale generale
        totale_generale = totale_materiali + totale_dipendenti
        self.label_totale_generale.configure(text=f"TOTALE GENERALE: {totale_generale:.2f} €")

# Codice per eseguire l'applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = GestioneCantiere(root)
    root.mainloop()