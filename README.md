# 🍽️ Akıllı Restoran Menü Öneri Sistemi (AI Destekli)

Bu proje, restoran menülerini kullanıcıların sağlık durumuna göre analiz eden, grafiksel çıktı üreten ve Ollama üzerinden yerel yapay zekâ ile yorum sağlayan gelişmiş bir masaüstü uygulamasıdır.

---

## 📌 About

Projemizin genel yapısı şu şekildedir:

Kullanıcı herhangi bir restoran menüsünü seçer ve kopyalar.  
Ardından uygulama açıkken **F8 tuşuna basarak** menüyü otomatik olarak sisteme aktarır.  

Sistem:

- Menü verisini analiz eder  
- Sağlık profiline göre sınıflandırır  
- Grafiksel sonuç üretir  
- Yapay zekâ ile yorum oluşturur  

---

## 🎯 Projenin Amacı

Bu projenin amacı:

- Kullanıcıların restoranlarda daha bilinçli seçim yapmasını sağlamak  
- Sağlık durumuna göre yemek önerisi sunmak  
- Veri analizi ve yapay zekâyı bir araya getirmek  

---

## 🧠 Kullanılan Teknolojiler

- Python
- Tkinter (GUI)
- Canvas (Grafik)
- Requests (API)
- Ollama (Local AI)
- Llama 3.2 1B Model

---

## ⚙️ Sistem Mimarisi

Uygulama 2 ana analiz katmanından oluşur:

### 1️⃣ Kural Tabanlı Analiz

Menüdeki yemekler, önceden belirlenen sağlık kurallarına göre analiz edilir.

Örnek:

- Diyabet → şekerli ve karbonhidratlı yiyecekler riskli
- Tansiyon → tuzlu ve işlenmiş gıdalar riskli
- Diyet → yüksek kalorili yiyecekler riskli

Sonuçlar:

- UYGUN
- DİKKATLİ
- ÖNERİLMEZ

---

### 2️⃣ Yapay Zekâ Analizi (Ollama)

Menü metni Ollama API üzerinden yerel modele gönderilir.

Model:

```bash
llama3.2:1b
