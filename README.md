# Akıllı Restoran Menü Öneri Sistemi

Bu proje, restoran menülerindeki yemekleri kullanıcının sağlık profiline göre analiz eden, Python ve Ollama destekli bir masaüstü uygulamasıdır.

## About

Projemizin genel yapısı şu şekildedir: Kullanıcı restoran menüsündeki yemek listesini seçer, kopyalar ve ardından uygulama açıkken F8 tuşuna basar. Sistem seçilen menüyü analiz ederek kullanıcının sağlık profiline göre hangi yemeklerin uygun, dikkatli tüketilmesi gereken veya önerilmez olduğunu listeler.

Bu proje, kural tabanlı analiz ile Ollama yapay zekâ yorumunu birleştirerek daha kapsamlı bir menü değerlendirme sistemi sunar.

## Projenin Amacı

Bu projenin amacı; diyabet, tansiyon ve diyet gibi farklı sağlık profillerine sahip kullanıcıların restoranlarda daha bilinçli yemek seçimi yapmasına yardımcı olmaktır.

Uygulama, restoran menüsündeki yemekleri analiz eder ve kullanıcının seçtiği sağlık profiline göre öneriler üretir.

## Kullanılan Teknolojiler

- Python
- Tkinter
- ttk
- Canvas
- Counter
- Requests
- Ollama
- Llama 3.2 1B modeli

## Temel Özellikler

- Sağlık profili seçimi
- Restoran menüsü analizi
- Uygun / Dikkatli / Önerilmez sınıflandırması
- F8 tuşu ile hızlı analiz
- Grafiksel menü risk dağılımı
- Ollama ile yapay zekâ destekli yorum
- Masaüstü kullanıcı arayüzü
- Örnek menü ve temizleme butonları

## Desteklenen Sağlık Profilleri

- Diyabet
- Tansiyon
- Diyet

## Sistem Nasıl Çalışır?

Uygulama iki farklı analiz yöntemi kullanır.

### 1. Kural Tabanlı Analiz

Program, menüdeki yemekleri önceden belirlenen anahtar kelimelerle karşılaştırır. Örneğin diyabet profili için tatlı, kola, pilav ve yüksek karbonhidratlı yiyecekler riskli olarak sınıflandırılır.

Yemekler üç gruba ayrılır:

- UYGUN
- DİKKATLİ
- ÖNERİLMEZ

### 2. Ollama AI Analizi

Menü metni ve seçilen sağlık profili Ollama API üzerinden yerel yapay zekâ modeline gönderilir. Model, menüyü yorumlar ve kullanıcıya Türkçe açıklamalı öneri üretir.

Kullanılan model:

```bash
llama3.2:1b

## Proje Özelliklerinin Gelişmiş Seviyesi

Bu proje, klasik veri görselleştirme projelerinden farklı olarak:

- Gerçek zamanlı kullanıcı etkileşimi sağlar
- F8 ile metin yakalama (event-driven sistem)
- Kural tabanlı veri analizi
- Grafiksel veri görselleştirme (Canvas)
- Ollama ile yerel yapay zekâ entegrasyonu
- Çok katmanlı analiz (rule-based + AI-based)

Bu yönüyle proje, hem veri analizi hem de yapay zekâ entegrasyonunu birleştiren hibrit bir sistemdir.
