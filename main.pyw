import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import threading

APP_TITLE = "Akıllı Restoran Menü Öneri Sistemi"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

try:
    import requests
except ImportError:
    requests = None


RULES = {
    "diyabet": {
        "bad": ["baklava", "kola", "tatlı", "pasta", "şeker", "seker", "pilav", "makarna", "patates", "pizza", "hamburger"],
        "good": ["ızgara tavuk", "izgara tavuk", "salata", "ayran", "yoğurt", "yogurt", "balık", "balik", "sebze", "çorba", "corba"]
    },
    "tansiyon": {
        "bad": ["turşu", "tursu", "sucuk", "salam", "sosis", "cips", "kola", "burger", "fast food"],
        "good": ["salata", "ızgara tavuk", "izgara tavuk", "balık", "balik", "sebze", "yoğurt", "yogurt", "ayran"]
    },
    "diyet": {
        "bad": ["baklava", "tatlı", "tatli", "pasta", "kola", "patates", "hamburger", "pizza", "kızartma", "kizartma"],
        "good": ["salata", "ızgara tavuk", "izgara tavuk", "balık", "balik", "yoğurt", "yogurt", "sebze", "çorba", "corba"]
    }
}


def split_menu(text):
    text = text.replace("\n", ",")
    return [item.strip() for item in text.split(",") if item.strip()]


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
    if requests is None:
        return (
            "Requests kütüphanesi yüklü değil.\n"
            "Terminal/CMD açıp şu komutu çalıştır:\n"
            "pip install requests"
        )

    prompt = f"""
Sen sağlık odaklı restoran menüsü analiz asistanısın.

Kullanıcı profili: {profile}

Restoran menüsü:
{menu}

Görev:
- Menüdeki yemekleri sağlık profiline göre değerlendir.
- UYGUN, DİKKATLİ ve ÖNERİLMEZ başlıkları altında ayır.
- Kısa, anlaşılır ve Türkçe cevap ver.
- En mantıklı yemek seçimini öner.
- Cevabın sonunda bunun tıbbi tavsiye olmadığını belirt.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=45
        )

        if response.status_code != 200:
            return (
                "Ollama bağlantısı kuruldu ancak model cevap vermedi.\n"
                f"Hata kodu: {response.status_code}\n"
                "Terminalde şu komutu çalıştır:\n"
                "ollama pull llama3.2:1b"
            )

        data = response.json()
        return data.get("response", "Ollama cevap üretmedi.")

    except Exception:
        return (
            "Ollama bağlantısı kurulamadı.\n\n"
            "Çözüm:\n"
            "1. Ollama kurulu olmalı.\n"
            "2. Terminal/CMD aç.\n"
            "3. Şu komutu çalıştır:\n"
            "   ollama pull llama3.2:1b\n"
            "4. Sonra uygulamada tekrar Analiz Et butonuna bas."
        )


def draw_chart(counts):
    canvas.delete("all")

    labels = ["UYGUN", "DİKKATLİ", "ÖNERİLMEZ"]
    colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
    values = [counts.get(label, 0) for label in labels]
    max_value = max(values) if max(values) > 0 else 1

    canvas.create_text(
        230, 30,
        text="Menü Risk Dağılımı",
        font=("Arial", 15, "bold"),
        fill="#1B2631"
    )

    x_start = 65
    y_base = 245
    bar_width = 80
    gap = 50

    for i, label in enumerate(labels):
        value = values[i]
        height = int((value / max_value) * 145)

        x1 = x_start + i * (bar_width + gap)
        y1 = y_base - height
        x2 = x1 + bar_width
        y2 = y_base

        canvas.create_rectangle(x1, y1, x2, y2, fill=colors[i], outline="")
        canvas.create_text(x1 + 40, y1 - 14, text=str(value), font=("Arial", 12, "bold"))
        canvas.create_text(x1 + 40, y_base + 20, text=label, font=("Arial", 9, "bold"))


def write_rules_result(menu, profile, counts):
    result_text.delete("1.0", "end")

    result_text.insert("end", f"Seçilen Sağlık Profili: {profile.upper()}\n\n")
    result_text.insert("end", "Kural Tabanlı Analiz Sonucu:\n")
    result_text.insert("end", f"Uygun yemek sayısı: {counts.get('UYGUN', 0)}\n")
    result_text.insert("end", f"Dikkatli tüketilecek yemek sayısı: {counts.get('DİKKATLİ', 0)}\n")
    result_text.insert("end", f"Önerilmeyen yemek sayısı: {counts.get('ÖNERİLMEZ', 0)}\n\n")

    result_text.insert("end", "Genel Öneri:\n")

    if profile == "diyabet":
        result_text.insert("end", "Diyabet profili için tatlı, kola, pilav ve yüksek karbonhidratlı yiyeceklerden kaçınılmalıdır.\n")
        result_text.insert("end", "Izgara tavuk, salata, yoğurt, sebze ve balık gibi seçenekler daha uygundur.\n")
    elif profile == "tansiyon":
        result_text.insert("end", "Tansiyon profili için tuzlu, işlenmiş ve paketli gıdalardan uzak durulmalıdır.\n")
        result_text.insert("end", "Salata, balık, sebze ve yoğurt gibi seçenekler daha uygundur.\n")
    elif profile == "diyet":
        result_text.insert("end", "Diyet profili için kızartma, tatlı ve gazlı içeceklerden kaçınılmalıdır.\n")
        result_text.insert("end", "Protein ve sebze ağırlıklı düşük kalorili seçenekler tercih edilmelidir.\n")

    result_text.insert("end", "\nNot: Bu uygulama eğitim amaçlıdır. Tıbbi tavsiye yerine geçmez.\n")


def run_ai_analysis(menu, profile):
    ai_button.config(state="disabled")
    status_label.config(text="Ollama AI yorumu hazırlanıyor...")

    result_text.insert("end", "\n\n--- Ollama AI Yorumu ---\n")
    result_text.insert("end", "Yanıt bekleniyor...\n")

    ai_answer = ask_ollama(menu, profile)

    result_text.insert("end", "\n")
    result_text.insert("end", ai_answer)
    result_text.insert("end", "\n")

    status_label.config(text="Analiz tamamlandı.")
    ai_button.config(state="normal")


def analyze_without_ai():
    for row in tree.get_children():
        tree.delete(row)

    menu = text_box.get("1.0", "end").strip()
    profile = profile_box.get()

    if not menu:
        messagebox.showwarning("Uyarı", "Lütfen menü giriniz.")
        return None, None

    foods = split_menu(menu)
    statuses = []

    for food in foods:
        status = analyze_item(food, profile)
        statuses.append(status)
        tree.insert("", "end", values=(food, status))

    counts = Counter(statuses)
    draw_chart(counts)
    write_rules_result(menu, profile, counts)
    status_label.config(text="Kural tabanlı analiz tamamlandı.")

    return menu, profile


def analyze_with_ai():
    menu, profile = analyze_without_ai()

    if menu is None:
        return

    thread = threading.Thread(
        target=run_ai_analysis,
        args=(menu, profile),
        daemon=True
    )
    thread.start()


def clipboard_analyze(event=None):
    try:
        copied = root.clipboard_get()

        if copied.strip() == "":
            messagebox.showwarning("Uyarı", "Panoda metin bulunamadı.")
            return

        text_box.delete("1.0", "end")
        text_box.insert("1.0", copied)

        root.after(100, analyze_with_ai)

    except Exception:
        messagebox.showwarning("Uyarı", "Önce menü metnini seçip Ctrl+C yapınız.")


def sample_menu():
    text_box.delete("1.0", "end")
    text_box.insert(
        "1.0",
        "Izgara Tavuk, Pilav, Baklava, Ayran, Kola, Salata, Mercimek Çorbası, Patates Kızartması, Balık, Yoğurt"
    )


def clear_all():
    text_box.delete("1.0", "end")
    result_text.delete("1.0", "end")
    canvas.delete("all")
    for row in tree.get_children():
        tree.delete(row)
    status_label.config(text="Temizlendi.")


root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1160x780")
root.configure(bg="#f4f6f9")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", font=("Arial", 10), rowheight=28)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

title = tk.Label(
    root,
    text=APP_TITLE,
    font=("Arial", 24, "bold"),
    bg="#f4f6f9",
    fg="#1B2631"
)
title.pack(pady=(16, 5))

subtitle = tk.Label(
    root,
    text="F8 ile seçili menüyü analiz eder, grafik üretir ve Ollama ile yapay zekâ destekli yorum oluşturur.",
    font=("Arial", 11),
    bg="#f4f6f9",
    fg="#34495E"
)
subtitle.pack(pady=(0, 10))

top_frame = tk.Frame(root, bg="#f4f6f9")
top_frame.pack(pady=5)

tk.Label(
    top_frame,
    text="Sağlık Profili:",
    font=("Arial", 11, "bold"),
    bg="#f4f6f9",
    fg="#1B2631"
).pack(side="left", padx=8)

profile_box = ttk.Combobox(
    top_frame,
    values=["diyabet", "tansiyon", "diyet"],
    state="readonly",
    width=28
)
profile_box.set("diyabet")
profile_box.pack(side="left", padx=8)

text_box = tk.Text(root, height=7, width=115, font=("Arial", 11), relief="solid", borderwidth=1)
text_box.pack(pady=10)
sample_menu()

button_frame = tk.Frame(root, bg="#f4f6f9")
button_frame.pack(pady=5)

rule_button = tk.Button(
    button_frame,
    text="Sadece Kural Analizi",
    command=analyze_without_ai,
    font=("Arial", 11, "bold"),
    bg="#27AE60",
    fg="white",
    padx=18,
    pady=8
)
rule_button.pack(side="left", padx=8)

ai_button = tk.Button(
    button_frame,
    text="Ollama ile Analiz Et",
    command=analyze_with_ai,
    font=("Arial", 11, "bold"),
    bg="#2E86C1",
    fg="white",
    padx=18,
    pady=8
)
ai_button.pack(side="left", padx=8)

sample_button = tk.Button(
    button_frame,
    text="Örnek Menü",
    command=sample_menu,
    font=("Arial", 11),
    bg="#8E44AD",
    fg="white",
    padx=18,
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
    padx=18,
    pady=8
)
clear_button.pack(side="left", padx=8)

status_label = tk.Label(
    root,
    text="Hazır. Menü girip analiz başlatabilirsiniz.",
    font=("Arial", 10, "bold"),
    bg="#f4f6f9",
    fg="#2C3E50"
)
status_label.pack(pady=5)

middle_frame = tk.Frame(root, bg="#f4f6f9")
middle_frame.pack(fill="both", expand=True, padx=20, pady=5)

tree = ttk.Treeview(middle_frame, columns=("Yemek", "Durum"), show="headings", height=13)
tree.heading("Yemek", text="Yemek")
tree.heading("Durum", text="Durum")
tree.column("Yemek", width=390)
tree.column("Durum", width=170)
tree.pack(side="left", fill="both", expand=True, padx=(0, 12))

canvas = tk.Canvas(
    middle_frame,
    width=460,
    height=300,
    bg="white",
    highlightbackground="#BDC3C7",
    highlightthickness=1
)
canvas.pack(side="right", padx=(12, 0))

result_text = tk.Text(root, height=12, width=128, font=("Arial", 10), relief="solid", borderwidth=1)
result_text.pack(pady=12)

root.bind("<F8>", clipboard_analyze)

root.mainloop()
