# (kısaltmıyorum, aynen koy)
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

APP_TITLE = "Akıllı Restoran Menü Öneri Sistemi"

RULES = {
    "diyabet": {
        "bad": ["baklava", "kola", "tatlı", "pasta", "şeker", "pilav", "makarna", "patates", "pizza"],
        "good": ["ızgara tavuk", "salata", "ayran", "yoğurt", "balık", "sebze"]
    },
    "tansiyon": {
        "bad": ["turşu", "sucuk", "salam", "sosis", "cips", "kola", "burger"],
        "good": ["salata", "ızgara tavuk", "balık", "sebze", "yoğurt"]
    },
    "diyet": {
        "bad": ["baklava", "tatlı", "pasta", "kola", "patates", "hamburger", "pizza"],
        "good": ["salata", "ızgara tavuk", "balık", "yoğurt", "sebze", "çorba"]
    }
}

def split_menu(text):
    text = text.replace("\n", ",")
    return [x.strip() for x in text.split(",") if x.strip()]

def analyze_item(item, profile):
    item_l = item.lower()
    rules = RULES.get(profile, {})

    for word in rules.get("bad", []):
        if word in item_l:
            return "ÖNERİLMEZ"

    for word in rules.get("good", []):
        if word in item_l:
            return "UYGUN"

    return "DİKKATLİ"

def analyze():
    for row in tree.get_children():
        tree.delete(row)

    menu = text_box.get("1.0", "end").strip()
    profile = profile_box.get()

    if not menu:
        messagebox.showwarning("Uyarı", "Lütfen menü giriniz.")
        return

    foods = split_menu(menu)
    statuses = []

    for food in foods:
        status = analyze_item(food, profile)
        statuses.append(status)
        tree.insert("", "end", values=(food, status))

    counts = Counter(statuses)
    result_text.delete("1.0", "end")
    result_text.insert("end", f"Profil: {profile.upper()}\n\n")
    result_text.insert("end", f"Uygun: {counts.get('UYGUN', 0)}\n")
    result_text.insert("end", f"Dikkatli: {counts.get('DİKKATLİ', 0)}\n")
    result_text.insert("end", f"Önerilmez: {counts.get('ÖNERİLMEZ', 0)}\n")

def clipboard_analyze(event=None):
    try:
        copied = root.clipboard_get()
        text_box.delete("1.0", "end")
        text_box.insert("1.0", copied)
        analyze()
    except:
        messagebox.showwarning("Uyarı", "Önce Ctrl+C yap")

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("850x600")

title = tk.Label(root, text=APP_TITLE, font=("Arial", 18, "bold"))
title.pack()

profile_box = ttk.Combobox(root, values=["diyabet", "tansiyon", "diyet"], state="readonly")
profile_box.set("diyabet")
profile_box.pack()

text_box = tk.Text(root, height=8)
text_box.pack()

btn = tk.Button(root, text="Analiz Et", command=analyze)
btn.pack()

tree = ttk.Treeview(root, columns=("Yemek", "Durum"), show="headings")
tree.heading("Yemek", text="Yemek")
tree.heading("Durum", text="Durum")
tree.pack(fill="both", expand=True)

result_text = tk.Text(root, height=5)
result_text.pack()

root.bind("<F8>", clipboard_analyze)

root.mainloop()
