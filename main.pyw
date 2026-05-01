import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import requests
import threading

APP_TITLE = "Akıllı Restoran Menü Öneri Sistemi"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

RULES = {
    "diyabet": {
        "bad": ["baklava", "kola", "tatlı", "pasta", "şeker", "pilav", "makarna", "patates", "pizza", "hamburger"],
        "good": ["ızgara tavuk", "salata", "ayran", "yoğurt", "balık", "sebze", "çorba"]
    },
    "tansiyon": {
        "bad": ["turşu", "sucuk", "salam", "sosis", "cips", "kola", "burger", "fast food"],
        "good": ["salata", "ızgara tavuk", "balık", "sebze", "yoğurt", "ayran"]
    },
    "diyet": {
        "bad": ["baklava", "tatlı", "pasta", "kola", "patates", "hamburger", "pizza", "kızartma"],
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

def ask_ollama(menu, profile):
    prompt = f"""
Sen sağlık odaklı bir restoran menüsü analiz asistanısın.

Kullanıcı profili: {profile}

Restoran menüsü:
{menu}

Görevin:
1. Menüdeki yemekleri sağlık profiline göre analiz et.
2. UYGUN, DİKKATLİ ve ÖNERİLMEZ olarak sınıflandır.
3. Kısa, anlaşılır ve Türkçe cevap ver.
4. Kullanıcıya en mantıklı yemek seçimini öner.
5. Cevabın sonunda bunun tıbbi tavsiye olmadığını belirt.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=90
    )

    data = response.json()
    return data.get("response", "Ollama cevap üretmedi.")

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

        color = "#2ECC71" if label == "UYGUN" else "#F1C40F" if label == "DİKKATLİ" else "#E74C3C"

        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        canvas.create_text(x1 + 35, y1 - 12, text=str(value), font=("Arial", 11, "bold"))
        canvas.create_text(x1 + 35, y_base + 20, text=label, font=("Arial", 9, "bold"))

def run_ollama_thread(menu, profile):
    result_text.insert("end", "\n\nOllama AI Yorumu hazırlanıyor...\n")
    root.update_idletasks()

    try:
        ai_answer = ask_ollama(menu, profile)
        result_text.insert("end", "\n--- Ollama AI Yorumu ---\n")
        result_text.insert("end", ai_answer)
    except Exception:
        result_text.insert("end", "\n\nOllama bağlantı hatası!\n")
        result_text.insert("end", "Lütfen Ollama'nın açık olduğundan emin olun.\n")
        result_text.insert("end", "Terminalde şu komutları çalıştırabilirsiniz:\n")
        result_text.insert("end", "ollama pull llama3.2:1b\n")
        result_text.insert("end", "ollama run llama3.2:1b\n")

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
    result_text.insert("end", f"Seçilen Sağlık Profili: {profile.upper()}\n\n")
    result_text.insert("end", f"Uygun yemek sayısı: {counts.get('UYGUN', 0)}\n")
    result_text.insert("end", f"Dikkatli tüketilecek yemek sayısı: {counts.get('DİKKATLİ', 0)}\n")
    result_text.insert("end", f"Önerilmeyen yemek sayısı: {counts.get('ÖNERİLMEZ', 0)}\n")

    result_text.insert("end", "\nKural Tabanlı Genel Öneri:\n")

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

    threading.Thread(target=run_ollama_thread, args=(menu, profile), daemon=True).start()

def clipboard_analyze(event=None):
    try:
        copied = root.clipboard_get()

        if copied.strip() == "":
            messagebox.showwarning("Uyarı", "Panoda metin bulunamadı.")
            return

        text_box.delete("1.0", "end")
        text_box.insert("1.0", copied)
        root.after(100, analyze)

    except Exception:
        messagebox.showwarning("Uyarı", "Önce menü metnini seçip Ctrl+C yapınız.")

def clear_all():
    text_box.delete("1.0", "end")
    result_text.delete("1.0", "end")
    canvas.delete("all")
    for row in tree.get_children():
        tree.delete(row)

def sample_menu():
    text_box.delete("1.0", "end")
    text_box.insert(
        "1.0",
        "Izgara Tavuk, Pilav, Baklava, Ayran, Kola, Salata, Mercimek Çorbası, Patates Kızartması, Balık, Yoğurt"
    )

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1120x760")
root.configure(bg="#f4f6f9")

title = tk.Label(
    root,
    text=APP_TITLE,
    font=("Arial", 24, "bold"),
    bg="#f4f6f9",
    fg="#1B2631"
)
title.pack(pady=15)

info = tk.Label(
    root,
    text="Menüyü yazın veya dışarıdan kopyalayıp uygulama açıkken F8 tuşuna basın. Sistem Ollama ile AI destekli analiz üretir.",
    font=("Arial", 11),
    bg="#f4f6f9",
    fg="#34495E"
)
info.pack()

profile_box = ttk.Combobox(
    root,
    values=["diyabet", "tansiyon", "diyet"],
    state="readonly",
    width=30
)
profile_box.set("diyabet")
profile_box.pack(pady=10)

text_box = tk.Text(root, height=7, width=110, font=("Arial", 11))
text_box.pack(pady=5)
sample_menu()

button_frame = tk.Frame(root, bg="#f4f6f9")
button_frame.pack(pady=10)

analyze_button = tk.Button(
    button_frame,
    text="Analiz Et",
    command=analyze,
    font=("Arial", 12, "bold"),
    bg="#2E86C1",
    fg="white",
    padx=25,
    pady=8
)
analyze_button.pack(side="left", padx=8)

sample_button = tk.Button(
    button_frame,
    text="Örnek Menü",
    command=sample_menu,
    font=("Arial", 11),
    bg="#27AE60",
    fg="white",
    padx=20,
    pady=8
)
sample_button.pack(side="left", padx=8)

clear_button = tk.Button(
    button_frame,
    text="Temizle",
    command=clear_all,
    font=("Arial", 11),
    bg="#C0392B",
    fg="white",
    padx=20,
    pady=8
)
clear_button.pack(side="left", padx=8)

middle_frame = tk.Frame(root, bg="#f4f6f9")
middle_frame.pack(fill="both", expand=True, padx=20)

tree = ttk.Treeview(middle_frame, columns=("Yemek", "Durum"), show="headings", height=13)
tree.heading("Yemek", text="Yemek")
tree.heading("Durum", text="Durum")
tree.column("Yemek", width=360)
tree.column("Durum", width=160)
tree.pack(side="left", fill="both", expand=True, padx=10)

canvas = tk.Canvas(middle_frame, width=440, height=290, bg="white", highlightbackground="#BDC3C7")
canvas.pack(side="right", padx=10)

result_text = tk.Text(root, height=11, width=125, font=("Arial", 10))
result_text.pack(pady=15)

root.bind("<F8>", clipboard_analyze)

analyze()

root.mainloop()
