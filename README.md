# DUSADIM---OOG---TAKIP---SISTEMI
ÖÖG öğrencileri için Python tabanlı, milisaniye hassasiyetli dikkat ve performans takip sistemi. (Python/Pygame/Pandas)

# GİRİŞ VE HAKKIMDA

Merhaba! Ben Asel Rasimgil. Ankara Üniversitesi, Bilgisayar ve Öğretim Teknolojileri Öğretmenliği (BÖTE) bölümü 2. sınıf öğrencisiyim. Bu proje, özel eğitim ihtiyacı olan öğrencilerin bilişsel süreçlerini dijital ortamda desteklemek ve bu süreçleri öğretmenler için veriye dayalı hale getirmek amacıyla hazırladığım bir "Eğitsel Performans Takip" çalışmasıdır.

Özel Öğrenme Güçlüğü (ÖÖG) yaşayan öğrencilerin dikkat ve odaklanma sürelerini ölçmek, geleneksel yöntemlerle oldukça zordur. Bu projeyle, oyunlaştırma (gamification) ve hassas zamanlama algoritmalarını birleştirerek öğrencinin gelişimini milisaniye hassasiyetinde takip etmeyi hedefledim.

# PROJE ÖZETİ

"DüşAdım", Python ve Pygame kütüphaneleri kullanılarak geliştirilmiş, 3 farklı ana ölçüm modülünden ve bir yönetici analiz portalından oluşan bir performans takip sistemidir. Yazılım, öğrencinin oyun sırasındaki tepki hızlarını ölçer, SQLite veritabanında saklar ve Pandas/Matplotlib kütüphaneleriyle bu verileri akademik gelişim grafiklerine dönüştürür.

# OYUN MODÜLLERİ VE BİLİŞSEL KAZANIMLAR

| Oyun Modülü | Bilişsel Odak | Akademik Kazanım |
| :--- | :--- | :--- |
| **Farklı Nesneyi Bul** | Görsel Dikkat & Ayırt Etme | Odaklanma hızı ve görsel tarama becerisi ölçümü. |
| **Hafıza Lambaları** | Kısa Süreli Bellek | Görsel dizilimleri hatırlama ve çalışma belleği takibi. |
| **Dizi Tamamlama** | Mantıksal Akıl Yürütme | Örüntü tanıma ve problem çözme hızı analizi. |

# TEKNİK VE MİMARİ ÖZELLİKLER

Programlama Dili: Python 3.x

Kütüphane: Pygame

Veri Analizi: Pandas & Matplotlib (Otomatik raporlama sistemi)

Veritabanı: SQLite3 (Kalıcı ve güvenli performans kaydı)

OOP Mimari: Oyun(ABC) soyut ana sınıfı üzerinden kalıtım (inheritance), kapsülleme (encapsulation) ve soyutlama (abstraction) prensipleri uygulanmıştır.

Algoritma: Milisaniye hassasiyetinde çalışan tepki süresi ölçüm ve loglama algoritması.

# KURULUM VE BAŞLATMA

### 1. Projeyi Yerel Bilgisayara Yükleme
Projeyi kendi bilgisayarınıza indirmek için terminale şu komutu yazın:
```bash
 git clone https://github.com/kullanici_adin/DusAdim.git
```
# 2. Gerekli Kütüphanelerin Yüklenmesi

```bash
pip install pygame pandas matplotlib
```

### 3. Oyunun Yüklü Olduğu Klasöre Girme
Terminal veya CMD ekranında projenin bulunduğu klasöre geçiş yapın:
```bash
cd DusAdim
```

### 4. Uygulamayı Başlatma

```bash
py ana_ekran.py
```

Geliştirici: Asel Rasimgil

Kurum: Ankara Üniversitesi, Bilgisayar ve Öğretim Teknolojileri Öğretmenliği (BÖTE) Bölümü








