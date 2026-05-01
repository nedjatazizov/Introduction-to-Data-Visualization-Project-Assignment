import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import Counter
import threading
from datetime import datetime
import os

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
        "good": ["ızgara tavuk", "salata", "ayran", "yoğurt", "yogurt", "balık", "balik", "sebze", "çorba", "corba"]
    },
    "tansiyon": {
        "bad": ["turşu", "tursu", "sucuk", "salam", "sosis", "cips", "kola", "burger", "fast food"],
        "good": ["salata", "ızgara tavuk", "balık", "balik", "sebze", "yoğurt", "yogurt", "ayran"]
    },
    "diyet": {
        "bad": ["baklava", "tatlı", "tatli", "pasta", "kola", "patates", "hamburger", "pizza", "kızartma", "kizartma"],
        "good": ["salata", "ızgara tavuk", "balık", "balik", "yoğurt", "yogurt", "sebze", "çorba", "corba"]
    }
}

history = []
last_report = ""


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
        return "Requests yüklü değil. CMD açıp şu komutu çalıştırın: python -m pip install requests"

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
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        data = response.json()
        return data.get("response", "Ollama cevap üretmedi.")
    except Exception:
        return (
            "Ollama bağlantısı kurulamadı.\n\n"
            "Çözüm:\n"
            "1. Ollama kurulu olmalı.\n"
            "2. CMD açıp şu komutu çalıştır:\n"
            "   ollama pull llama3.2:1b\n"
            "3. Sonra tekrar 'Ollama ile Analiz Et' butonuna bas."
        )


def draw_chart(counts):
    canvas.delete("all")

    labels = ["UYGUN", "DİKKATLİ", "ÖNERİLMEZ"]
    colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
    values = [counts.get(label, 0) for label in labels]
    max_value = max(values) if max(values) > 0 else 1

    canvas.create_text(230, 30, text="Menü Risk Dağılımı", font=("Arial", 15, "bold"), fill=theme["fg"])

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
        canvas.create_text(x1 + 40, y1 - 14, text=str(value), font=("Arial", 12, "bold"), fill=theme["fg"])
        canvas.create_text(x1 + 40, y_base + 20, text=label, font=("Arial", 9, "bold"), fill=theme["fg"])


def create_report_text(profile, foods, statuses, counts):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    report = ""
    report += "AKILLI RESTORAN MENÜ ÖNERİ SİSTEMİ\n"
    report += "=" * 45 + "\n"
    report += f"Tarih: {now}\n"
    report += f"Seçilen Sağlık Profili: {profile.upper()}\n\n"

    report += "MENÜ ANALİZ SONUÇLARI\n"
    report += "-" * 45 + "\n"

    for food, status in zip(foods, statuses):
        report += f"{food} -> {status}\n"

    report += "\nÖZET\n"
    report += "-" * 45 + "\n"
    report += f"Uygun yemek sayısı: {counts.get('UYGUN', 0)}\n"
    report += f"Dikkatli tüketilecek yemek sayısı: {counts.get('DİKKATLİ', 0)}\n"
    report += f"Önerilmeyen yemek sayısı: {counts.get('ÖNERİLMEZ', 0)}\n\n"

    report += "GENEL ÖNERİ\n"
    report += "-" * 45 + "\n"

    if profile == "diyabet":
        report += "Diyabet profili için tatlı, kola, pilav ve yüksek karbonhidratlı yiyeceklerden kaçınılmalıdır.\n"
        report += "Izgara tavuk, salata, yoğurt, sebze ve balık gibi seçenekler daha uygundur.\n"
    elif profile == "tansiyon":
        report += "Tansiyon profili için tuzlu, işlenmiş ve paketli gıdalardan uzak durulmalıdır.\n"
        report += "Salata, balık, sebze ve yoğurt gibi seçenekler daha uygundur.\n"
    elif profile == "diyet":
        report += "Diyet profili için kızartma, tatlı ve gazlı içeceklerden kaçınılmalıdır.\n"
        report += "Protein ve sebze ağırlıklı düşük kalorili seçenekler tercih edilmelidir.\n"

    report += "\nNot: Bu uygulama eğitim amaçlıdır. Tıbbi tavsiye yerine geçmez.\n"

    return report


def analyze_without_ai():
    global last_report

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

    last_report = create_report_text(profile, foods, statuses, counts)

    result_text.delete("1.0", "end")
    result_text.insert("end", last_report)

    add_history(profile, menu)
    status_label.config(text="Kural tabanlı analiz tamamlandı.")

    return menu, profile


def run_ai_analysis(menu, profile):
    global last_report

    ai_button.config(state="disabled")
    status_label.config(text="Ollama AI yorumu hazırlanıyor...")

    result_text.insert("end", "\n\n==============================\n")
    result_text.insert("end", "       OLLAMA AI YORUMU\n")
    result_text.insert("end", "==============================\n\n")
    result_text.insert("end", "Yanıt bekleniyor...\n\n")

    ai_answer = ask_ollama(menu, profile)

    result_text.insert("end", ai_answer)
    last_report = result_text.get("1.0", "end")

    status_label.config(text="Ollama AI analizi tamamlandı.")
    ai_button.config(state="normal")


def analyze_with_ai():
    menu, profile = analyze_without_ai()
    if menu is None:
        return

    thread = threading.Thread(target=run_ai_analysis, args=(menu, profile), daemon=True)
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


def save_txt():
    content = result_text.get("1.0", "end").strip()

    if not content:
        messagebox.showwarning("Uyarı", "Kaydedilecek analiz bulunamadı.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text File", "*.txt")],
        title="Analizi TXT olarak kaydet"
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        messagebox.showinfo("Başarılı", "Analiz TXT olarak kaydedildi.")


def save_pdf():
    content = result_text.get("1.0", "end").strip()

    if not content:
        messagebox.showwarning("Uyarı", "PDF oluşturmak için önce analiz yapınız.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF File", "*.pdf")],
        title="PDF olarak kaydet"
    )

    if not file_path:
        return

    create_simple_pdf(file_path, content)
    messagebox.showinfo("Başarılı", "PDF dosyası oluşturuldu.")


def create_simple_pdf(path, text):
    safe_text = text.replace("(", "[").replace(")", "]")
    lines = safe_text.split("\n")

    pdf_lines = []
    y = 800

    pdf_lines.append("%PDF-1.4\n")
    pdf_lines.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    pdf_lines.append("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    pdf_lines.append("3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n")

    content = "BT\n/F1 10 Tf\n"
    for line in lines[:45]:
        content += f"50 {y} Td ({line}) Tj\n"
        content += f"-50 -16 Td\n"
        y -= 16
    content += "ET"

    pdf_lines.append(f"4 0 obj << /Length {len(content)} >> stream\n{content}\nendstream endobj\n")
    pdf_lines.append("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    xref_pos = sum(len(x.encode("latin-1", errors="ignore")) for x in pdf_lines)
    pdf_lines.append("xref\n0 6\n0000000000 65535 f \n")
    pdf_lines.append("0000000010 00000 n \n")
    pdf_lines.append("0000000060 00000 n \n")
    pdf_lines.append("0000000120 00000 n \n")
    pdf_lines.append("0000000250 00000 n \n")
    pdf_lines.append("0000000400 00000 n \n")
    pdf_lines.append(f"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF")

    with open(path, "wb") as file:
        file.write("".join(pdf_lines).encode("latin-1", errors="ignore"))


def add_history(profile, menu):
    now = datetime.now().strftime("%H:%M:%S")
    short_menu = menu[:45] + "..." if len(menu) > 45 else menu
    item = f"{now} | {profile.upper()} | {short_menu}"

    history.append((profile, menu))
    history_list.insert("end", item)


def load_history(event=None):
    selection = history_list.curselection()
    if not selection:
        return

    index = selection[0]
    profile, menu = history[index]

    profile_box.set(profile)
    text_box.delete("1.0", "end")
    text_box.insert("1.0", menu)


def toggle_theme():
    if theme["mode"] == "light":
        set_dark_theme()
    else:
        set_light_theme()


def apply_theme():
    root.configure(bg=theme["bg"])
    title.configure(bg=theme["bg"], fg=theme["fg"])
    subtitle.configure(bg=theme["bg"], fg=theme["fg"])
    top_frame.configure(bg=theme["bg"])
    button_frame.configure(bg=theme["bg"])
    middle_frame.configure(bg=theme["bg"])
    side_frame.configure(bg=theme["bg"])
    status_label.configure(bg=theme["bg"], fg=theme["fg"])

    for widget in top_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])

    text_box.configure(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    result_text.configure(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    history_list.configure(bg=theme["input_bg"], fg=theme["fg"])
    canvas.configure(bg=theme["canvas_bg"])


def set_dark_theme():
    theme.update({
        "mode": "dark",
        "bg": "#1e1e1e",
        "fg": "#f5f5f5",
        "input_bg": "#2b2b2b",
        "canvas_bg": "#2b2b2b"
    })
    apply_theme()


def set_light_theme():
    theme.update({
        "mode": "light",
        "bg": "#f4f6f9",
        "fg": "#1B2631",
        "input_bg": "white",
        "canvas_bg": "white"
    })
    apply_theme()


theme = {
    "mode": "light",
    "bg": "#f4f6f9",
    "fg": "#1B2631",
    "input_bg": "white",
    "canvas_bg": "white"
}


root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1280x850")
root.configure(bg=theme["bg"])

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", font=("Arial", 10), rowheight=28)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

title = tk.Label(root, text=APP_TITLE, font=("Arial", 24, "bold"), bg=theme["bg"], fg=theme["fg"])
title.pack(pady=(14, 4))

subtitle = tk.Label(
    root,
    text="F8 ile menü analizi, grafik, Ollama AI yorumu, PDF/TXT çıktı, karanlık tema ve kullanıcı geçmişi.",
    font=("Arial", 11),
    bg=theme["bg"],
    fg=theme["fg"]
)
subtitle.pack(pady=(0, 10))

top_frame = tk.Frame(root, bg=theme["bg"])
top_frame.pack(pady=4)

tk.Label(top_frame, text="Sağlık Profili:", font=("Arial", 11, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(side="left", padx=8)

profile_box = ttk.Combobox(top_frame, values=["diyabet", "tansiyon", "diyet"], state="readonly", width=28)
profile_box.set("diyabet")
profile_box.pack(side="left", padx=8)

theme_button = tk.Button(top_frame, text="Karanlık / Açık Tema", command=toggle_theme, bg="#34495E", fg="white", padx=14)
theme_button.pack(side="left", padx=8)

text_box = tk.Text(root, height=6, width=125, font=("Arial", 11), relief="solid", borderwidth=1)
text_box.pack(pady=8)
sample_menu()

button_frame = tk.Frame(root, bg=theme["bg"])
button_frame.pack(pady=5)

tk.Button(button_frame, text="Sadece Kural Analizi", command=analyze_without_ai, font=("Arial", 11, "bold"), bg="#27AE60", fg="white", padx=15, pady=7).pack(side="left", padx=5)
ai_button = tk.Button(button_frame, text="Ollama ile Analiz Et", command=analyze_with_ai, font=("Arial", 11, "bold"), bg="#2E86C1", fg="white", padx=15, pady=7)
ai_button.pack(side="left", padx=5)
tk.Button(button_frame, text="Örnek Menü", command=sample_menu, font=("Arial", 11), bg="#8E44AD", fg="white", padx=15, pady=7).pack(side="left", padx=5)
tk.Button(button_frame, text="TXT Kaydet", command=save_txt, font=("Arial", 11), bg="#F39C12", fg="white", padx=15, pady=7).pack(side="left", padx=5)
tk.Button(button_frame, text="PDF Çıktı Al", command=save_pdf, font=("Arial", 11), bg="#D35400", fg="white", padx=15, pady=7).pack(side="left", padx=5)
tk.Button(button_frame, text="Temizle", command=clear_all, font=("Arial", 11), bg="#C0392B", fg="white", padx=15, pady=7).pack(side="left", padx=5)

status_label = tk.Label(root, text="Hazır. Menü girip analiz başlatabilirsiniz.", font=("Arial", 10, "bold"), bg=theme["bg"], fg=theme["fg"])
status_label.pack(pady=4)

middle_frame = tk.Frame(root, bg=theme["bg"])
middle_frame.pack(fill="both", expand=True, padx=18, pady=5)

tree = ttk.Treeview(middle_frame, columns=("Yemek", "Durum"), show="headings", height=12)
tree.heading("Yemek", text="Yemek")
tree.heading("Durum", text="Durum")
tree.column("Yemek", width=330)
tree.column("Durum", width=140)
tree.pack(side="left", fill="both", expand=True, padx=(0, 10))

canvas = tk.Canvas(middle_frame, width=460, height=300, bg=theme["canvas_bg"], highlightbackground="#BDC3C7", highlightthickness=1)
canvas.pack(side="left", padx=10)

side_frame = tk.Frame(middle_frame, bg=theme["bg"])
side_frame.pack(side="right", fill="y", padx=(10, 0))

tk.Label(side_frame, text="Kullanıcı Geçmişi", font=("Arial", 12, "bold"), bg=theme["bg"], fg=theme["fg"]).pack(pady=(0, 5))

history_list = tk.Listbox(side_frame, width=38, height=14, font=("Arial", 9))
history_list.pack(fill="y")
history_list.bind("<<ListboxSelect>>", load_history)

result_text = tk.Text(root, height=12, width=140, font=("Arial", 10), relief="solid", borderwidth=1)
result_text.pack(pady=10)

root.bind("<F8>", clipboard_analyze)

apply_theme()
root.mainloop()
