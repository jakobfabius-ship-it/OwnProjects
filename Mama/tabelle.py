#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class ListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Liste mit Unterpunkten")
        self.root.geometry("600x500")
        
        # Buttons Frame
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="➕ Element hinzufügen", command=self.add_main_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="➕ Unterpunkt hinzufügen", command=self.add_sub_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Bearbeiten", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Löschen", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        
        # Treeview Widget erstellen
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("#0", text="Name")
        
        # Bindings für Checkbox-Toggling
        self.tree.bind("<Button-1>", self.on_click)
        
        # Beispiel-Daten laden
        self.load_sample_data()
    
    def load_sample_data(self):
        """Laden Sie Beispiel-Daten"""
        item1 = self.tree.insert("", tk.END, text="☐ Obst", open=True)
        self.tree.insert(item1, tk.END, text="☐ Apfel")
        self.tree.insert(item1, tk.END, text="☐ Banane")
        
        item2 = self.tree.insert("", tk.END, text="☐ Gemüse")
        self.tree.insert(item2, tk.END, text="☐ Karotte")
        self.tree.insert(item2, tk.END, text="☐ Gurke")
    
    def on_click(self, event):
        """Click-Handler für Checkbox-Toggling"""
        # Identifiziere das geklickte Item
        item_id = self.tree.identify('item', event.x, event.y)
        
        if item_id:
            self.tree.selection_set(item_id)
            
            # Versuche zu erkennen, ob auf Text oder Button geklickt wurde
            # Auf den Expand/Collapse Button wird nicht reagiert, nur auf Text
            column = self.tree.identify_column(event.x)
            if column == '#0':  # Main column
                # Prüfe ob es nicht der Expand/Collapse Button ist
                # Der Button ist normalerweise in den ersten ~20 Pixeln
                # Der Text beginnt nach dem Button
                children = self.tree.get_children(item_id)
                
                # Wenn item keine Kinder hat, immer abhaken
                if not children:
                    self.toggle_checkbox()
                else:
                    # Wenn item Kinder hat, nur abhaken wenn nicht auf den Button geklickt
                    # Der Expand/Collapse Button ist etwa in den ersten 20 Pixeln
                    if event.x > 30:
                        self.toggle_checkbox()
    
    def toggle_checkbox(self, event=None):
        """Abhaken/Abhaken-Symbol toggen"""
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_id = selection[0]
        current_text = self.tree.item(selected_id, 'text')
        
        # Prüfe ob es ein Oberpunkt oder Unterpunkt ist
        children = self.tree.get_children(selected_id)
        parent = self.tree.parent(selected_id)
        
        # Wenn es ein Oberpunkt mit Unterpunkten ist und versucht wird abzuhaken
        if children and current_text.startswith("☐ "):
            # Prüfe ob alle Unterpunkte abgehakt sind
            all_checked = True
            for child in children:
                child_text = self.tree.item(child, 'text')
                if not child_text.startswith("☑ "):
                    all_checked = False
                    break
            
            # Nur abhaken wenn alle Unterpunkte abgehakt sind
            if not all_checked:
                return  # Stillfschweigend ignorieren
            
            # Alle Unterpunkte sind abgehakt, hacke ab
            new_text = "☑ " + current_text[2:]
            self.tree.item(selected_id, text=new_text)
        
        elif current_text.startswith("☐ "):
            new_text = "☑ " + current_text[2:]
            self.tree.item(selected_id, text=new_text)
            
            # Wenn es ein Oberpunkt mit Unterpunkten ist, alle Unterpunkte auch abhaken
            if children:
                for child in children:
                    child_text = self.tree.item(child, 'text')
                    if child_text.startswith("☐ "):
                        self.tree.item(child, text="☑ " + child_text[2:])
        
        elif current_text.startswith("☑ "):
            new_text = "☐ " + current_text[2:]
            self.tree.item(selected_id, text=new_text)
            
            # Wenn es ein Oberpunkt mit Unterpunkten ist, alle Unterpunkte auch abhaken
            if children:
                for child in children:
                    child_text = self.tree.item(child, 'text')
                    if child_text.startswith("☑ "):
                        self.tree.item(child, text="☐ " + child_text[2:])
        
        # Wenn es ein Unterpunkt ist, prüfe ob der Parent automatisch abgehakt werden soll
        if parent:
            self.update_parent_checkbox(parent)

    
    def update_parent_checkbox(self, parent_id):
        """Prüfe ob alle Unterpunkte abgehakt sind und hacke Parent automatisch ab"""
        children = self.tree.get_children(parent_id)
        
        if not children:
            return  # Keine Unterpunkte
        
        # Prüfe ob alle Unterpunkte abgehakt sind
        all_checked = True
        for child in children:
            child_text = self.tree.item(child, 'text')
            if not child_text.startswith("☑ "):
                all_checked = False
                break
        
        parent_text = self.tree.item(parent_id, 'text')
        
        if all_checked:
            # Alle Unterpunkte sind abgehakt, hacke Parent ab
            if parent_text.startswith("☐ "):
                self.tree.item(parent_id, text="☑ " + parent_text[2:])
        else:
            # Nicht alle Unterpunkte sind abgehakt, hacke Parent ab
            if parent_text.startswith("☑ "):
                self.tree.item(parent_id, text="☐ " + parent_text[2:])

    
    def add_main_item(self):
        """Neues Hauptelement hinzufügen"""
        dialog = simpledialog.askstring("Neues Element", "Elementname eingeben:")
        if dialog:
            self.tree.insert("", tk.END, text=f"☐ {dialog.strip()}", open=True)
            messagebox.showinfo("Erfolg", f"'{dialog}' hinzugefügt!")
    
    def add_sub_item(self):
        """Unterpunkt hinzufügen"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Hauptelement aus!")
            return
        
        selected_id = selection[0]
        parent = self.tree.parent(selected_id)
        
        # Wenn ein Unterpunkt selected ist, nimm seinen Parent
        if parent:
            selected_id = parent
        
        dialog = simpledialog.askstring("Neuer Unterpunkt", "Unterpunkt eingeben:")
        if dialog:
            self.tree.insert(selected_id, tk.END, text=f"☐ {dialog.strip()}")
            messagebox.showinfo("Erfolg", f"Unterpunkt '{dialog}' hinzugefügt!")
    
    def edit_item(self):
        """Element bearbeiten"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Element aus!")
            return
        
        selected_id = selection[0]
        current_text = self.tree.item(selected_id, 'text')
        
        # Entferne das Checkbox-Symbol für die Eingabe
        current_text = current_text.replace("☐ ", "").replace("☑ ", "")
        
        new_text = simpledialog.askstring("Bearbeiten", "Neuer Text:", initialvalue=current_text)
        if new_text:
            # Checkbox-Symbol beibehalten
            original_full = self.tree.item(selected_id, 'text')
            checkbox = original_full[0]
            self.tree.item(selected_id, text=f"{checkbox} {new_text.strip()}")
            messagebox.showinfo("Erfolg", "Text aktualisiert!")
    
    def delete_item(self):
        """Element löschen"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Element zum Löschen aus!")
            return
        
        if messagebox.askyesno("Bestätigung", "Wirklich löschen?"):
            selected_id = selection[0]
            self.tree.delete(selected_id)
            messagebox.showinfo("Erfolg", "Gelöscht!")

# Hauptfenster erstellen
root = tk.Tk()
app = ListApp(root)
root.mainloop()
