#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from pathlib import Path

class ListItem:
    def __init__(self, text, level=0, checked=False, item_id=None):
        self.text = text
        self.level = level
        self.checked = checked
        self.children = []
        self.item_id = item_id or id(self)
    
    def toggle_check(self):
        self.checked = not self.checked
    
    def to_dict(self):
        return {
            'text': self.text,
            'checked': self.checked,
            'children': [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(data, level=0):
        item = ListItem(data['text'], level, data['checked'])
        for child_data in data.get('children', []):
            item.children.append(ListItem.from_dict(child_data, level + 1))
        return item

class TodoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aufgabenliste")
        self.root.geometry("700x600")
        
        self.filename = 'todo.json'
        self.items = []
        self.tree_id_map = {}  # Mapping von tree_id zu (item, parent_item)
        self.load()
        
        # Stile
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame für die Baumansicht
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, height=20)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Spalten definieren
        self.tree['columns'] = ('text',)
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('text', anchor=tk.W, width=600)
        
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('text', text='Aufgaben', anchor=tk.W)
        
        # Bindings
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<Delete>', self.delete_selected)
        self.tree.bind('<Double-Button-1>', self.edit_item)
        
        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="➕ Aufgabe hinzufügen", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="➕ Unterpunkt hinzufügen", command=self.add_subitem).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Bearbeiten", command=self.edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Löschen", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Aktualisieren", command=self.refresh_tree).pack(side=tk.LEFT, padx=5)
        
        self.refresh_tree()
    
    def load(self):
        if Path(self.filename).exists():
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [ListItem.from_dict(item) for item in data]
            except:
                self.items = []
        else:
            self.items = []
    
    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in self.items], f, ensure_ascii=False, indent=2)
    
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tree_id_map = {}
        
        for item in self.items:
            self.add_tree_item(item, '', item)
    
    def add_tree_item(self, item, parent, parent_item_obj):
        checkbox = "☑" if item.checked else "☐"
        text = item.text
        if item.checked:
            text = f"~~{text}~~"
        
        # Visuelle Indentation für Unterpunkte
        if item.level > 0:
            indent = "    " * item.level
            display_text = f"{indent}{checkbox} {text}"
        else:
            display_text = f"{checkbox} {text}"
        
        node = self.tree.insert(parent, 'end', text=display_text, values=(display_text,), open=True)
        self.tree_id_map[node] = (item, parent_item_obj)
        
        for child in item.children:
            self.add_tree_item(child, node, item)
        
        return node
    
    def on_tree_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        
        selected_id = item[0]
        
        # Prüfe ob auf Checkbox geklickt (die ersten 1-2 Zeichen)
        col = self.tree.identify_column(event.x)
        if col == '#0':  # Main column
            # Prüfe ob auf dem Checkbox-Symbol geklickt wurde (ungefähr erste 30 Pixel)
            if event.x < 50:
                self.toggle_item_at_selection()
    
    def toggle_item_at_selection(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_id = selection[0]
        self.toggle_item_by_tree_id(selected_id)
        self.save()
        self.refresh_tree()
    
    def toggle_item_by_tree_id(self, tree_id):
        if tree_id not in self.tree_id_map:
            return
        
        item, parent_item = self.tree_id_map[tree_id]
        item.toggle_check()
    
    def add_item(self):
        dialog = simpledialog.askstring("Neue Aufgabe", "Aufgabe eingeben:")
        if dialog:
            self.items.append(ListItem(dialog.strip(), 0))
            self.save()
            self.refresh_tree()
            messagebox.showinfo("Erfolg", f"Aufgabe '{dialog}' hinzugefügt!")
    
    def add_subitem(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Hauptaufgabe aus!")
            return
        
        selected_id = selection[0]
        
        if selected_id not in self.tree_id_map:
            messagebox.showwarning("Warnung", "Ungültige Auswahl!")
            return
        
        item, parent_item = self.tree_id_map[selected_id]
        
        # Prüfe ob das Item bereits ein Unterpunkt ist (parent_item ist nicht None und nicht in items)
        if parent_item not in self.items and parent_item is not None:
            messagebox.showwarning("Warnung", "Sie können nur Unterpunkte zu Hauptaufgaben hinzufügen!")
            return
        
        dialog = simpledialog.askstring("Neuer Unterpunkt", "Unterpunkt eingeben:")
        
        if dialog:
            item.children.append(ListItem(dialog.strip(), 1))
            self.save()
            self.refresh_tree()
            messagebox.showinfo("Erfolg", f"Unterpunkt '{dialog}' hinzugefügt!")
    
    def edit_item(self, event=None):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Element aus!")
            return
        
        selected_id = selection[0]
        
        if selected_id not in self.tree_id_map:
            messagebox.showwarning("Warnung", "Ungültige Auswahl!")
            return
        
        item, parent_item = self.tree_id_map[selected_id]
        
        current_text = item.text
        new_text = simpledialog.askstring("Bearbeiten", "Neuer Text:", initialvalue=current_text)
        
        if new_text:
            item.text = new_text.strip()
            self.save()
            self.refresh_tree()
            messagebox.showinfo("Erfolg", "Text aktualisiert!")
    
    def delete_selected(self, event=None):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Element zum Löschen aus!")
            return
        
        selected_id = selection[0]
        
        if selected_id not in self.tree_id_map:
            messagebox.showwarning("Warnung", "Ungültige Auswahl!")
            return
        
        if messagebox.askyesno("Bestätigung", "Wirklich löschen?"):
            item, parent_item = self.tree_id_map[selected_id]
            
            if parent_item in self.items:
                # Es ist ein Hauptpunkt
                self.items.remove(item)
            else:
                # Es ist ein Unterpunkt
                parent_item.children.remove(item)
            
            self.save()
            self.refresh_tree()
            messagebox.showinfo("Erfolg", "Gelöscht!")

def main():
    root = tk.Tk()
    app = TodoListApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
