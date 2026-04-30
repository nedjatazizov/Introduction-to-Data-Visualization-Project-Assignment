import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

APP_TITLE = "Akıllı Restoran Menü Öneri Sistemi"

RULES = {
    "diyabet": {
        "bad": ["baklava", "kola", "tatlı", "pasta", "şeker", "pilav", "makarna", "patates", "pizza"],
        "good": ["ızgara tavuk", "salata", "ayran", "yoğurt", "balık", "sebze", "çorba"]
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

def draw_chart(counts):
    canvas.delete("all")

    labels = ["UYGUN", "DİKKATLİ", "ÖNERİLMEZ"]
    values = [counts.get(label, 0) for label in labels]

    max_value = max(values) if max(values) > 0 else 1

    x_start = 60
    y_base = 220
    bar_width = 70
    gap = 45

    canvas.create_text(210, 25, text="Menü Analiz Grafiği", font=("Arial", 14, "bold"))

    for i, label in enumerate(labels):
        value = values[i]
        height = int((value / max_value) * 140)

        x1 = x_start + i * (bar_width + gap)
        y1 = y_base - height
        x2 = x1 + bar_width
        y2 = y_base

        canvas.create_rectangle(x1, y1, x2, y2, fill="#4F81BD")
        canvas.create_text(x1 + 35, y1 - 12, text=str(value), font=("Arial", 11, "bold"))
        canvas.create_text(x1 + 35, y_base + 20, text=label, font=("Arial", 9))

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
    draw_chart(counts)

    result_text.delete("1.0", "end")
    result_text.insert("end", f"Profil: {profile.upper()}\n\n")
    result_text.insert("end", f"Uygun yemek sayısı: {counts.get('UYGUN', 0)}\n")
    result_text.insert("end", f"Dikkatli tüketilecek yemek sayısı: {counts.get('DİKKATLİ', 0)}\n")
    result_text.insert("end", f"Önerilmeyen yemek sayısı: {counts.get('ÖNERİLMEZ', 0)}\n")

    result_text.insert("end", "\nGenel Öneri:\n")

    if profile == "diyabet":
        result_text.insert("end", "Diyabet profili için tatlı, kola, pilav ve yüksek karbonhidratlı yiyeceklerden kaçınılmalıdır.\n")
        result_text.insert("end", "Izgara tavuk, salata, yoğurt ve sebze ağırlıklı seçenekler daha uygundur.\n")
    elif profile == "tansiyon":
        result_text.insert("end", "Tansiyon profili için tuzlu ve işlenmiş gıdalardan uzak durulmalıdır.\n")
        result_text.insert("end", "Salata, balık, sebze ve yoğurt gibi seçenekler daha uygundur.\n")
    elif profile == "diyet":
        result_text.insert("end", "Diyet profili için kızartma, tatlı ve gazlı içeceklerden kaçınılmalıdır.\n")
        result_text.insert("end", "Protein ve sebze ağırlıklı düşük kalorili seçenekler tercih edilmelidir.\n")

    result_text.insert("end", "\nNot: Bu uygulama eğitim amaçlıdır. Tıbbi tavsiye yerine geçmez.")

def clipboard_analyze(event=None):
    try:
        copied = root.clipboard_get()
        text_box.delete("1.0", "end")
        text_box.insert("1.0", copied)
        analyze()
    except:
        messagebox.showwarning("Uyarı", "Önce menü metnini seçip Ctrl+C yapınız.")

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1050x720")
root.configure(bg="#f4f6f9")

title = tk.Label(
    root,
    text=APP_TITLE,
    font=("Arial", 22, "bold"),
    bg="#f4f6f9"
)
title.pack(pady=15)

info = tk.Label(
    root,
    text="Menüyü yazın veya dışarıdan kopyalayıp uygulama açıkken F8 tuşuna basın.",
    font=("Arial", 11),
    bg="#f4f6f9"
)
info.pack()

profile_box = ttk.Combobox(
    root,
    values=["diyabet", "tansiyon", "diyet"],
    state="readonly",
    width=25
)
profile_box.set("diyabet")
profile_box.pack(pady=10)

text_box = tk.Text(root, height=7, width=100, font=("Arial", 11))
text_box.pack(pady=5)
text_box.insert("1.0", "Izgara Tavuk, Pilav, Baklava, Ayran, Kola, Salata, Mercimek Çorbası, Patates Kızartması, Balık, Yoğurt")

btn = tk.Button(
    root,
    text="Analiz Et",
    command=analyze,
    font=("Arial", 12, "bold"),
    bg="#2E86C1",
    fg="white",
    padx=20,
    pady=6
)
btn.pack(pady=10)

middle_frame = tk.Frame(root, bg="#f4f6f9")
middle_frame.pack(fill="both", expand=True, padx=20)

tree = ttk.Treeview(middle_frame, columns=("Yemek", "Durum"), show="headings", height=12)
tree.heading("Yemek", text="Yemek")
tree.heading("Durum", text="Durum")
tree.column("Yemek", width=330)
tree.column("Durum", width=160)
tree.pack(side="left", fill="both", expand=True, padx=10)

canvas = tk.Canvas(middle_frame, width=420, height=270, bg="white")
canvas.pack(side="right", padx=10)

result_text = tk.Text(root, height=8, width=115, font=("Arial", 10))
result_text.pack(pady=15)

root.bind("<F8>", clipboard_analyze)

analyze()

root.mainloop()
