import sqlite3
import os

# =============================================================================================
# VERİTABANI YÖNETİCİSİ - KAPSÜLLEME (ENCAPSULATION)
# =============================================================================================

class VeriTabaniYoneticisi:
    """
    OOP İLKESİ: Kapsülleme. 
    Veritabanı yolu private yapılmış ve dış müdahalelere kapatılmıştır.
    """
    def __init__(self, veritabani_adi="dusadim_final_V30.db"):
        self.__veritabani_yolu = veritabani_adi
        self.__tablolari_yapilandir()

    def __tablolari_yapilandir(self):
        """Private Metot: Veri yapılarını yönergeye uygun oluşturur."""
        try:
            with sqlite3.connect(self.__veritabani_yolu) as baglanti:
                imlec = baglanti.cursor()
                # Kullanıcılar Tablosu
                imlec.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, 
                                sifre TEXT, rol TEXT, sinif TEXT, sube TEXT)''')
                # Performans Tablosu (7 Kritik Sütun + ID/Tarih)
                imlec.execute('''CREATE TABLE IF NOT EXISTS performans 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, 
                                sinif TEXT, oyun TEXT, dogru INTEGER, yanlis INTEGER, 
                                ort_tepki REAL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                baglanti.commit()
        except sqlite3.Error as e:
            print(f"VT Yapılandırma Hatası: {e}")

    def performans_kaydet(self, ad, soyad, sinif, oyun, dogru, yanlis, tepki):
        """
        KOD ORGANİZASYONU: Anlamlı değişken isimleri ile veri kaydı.
        Oyun sınıfları bu metodu çağırarak 7 parametreli veriyi işler.
        """
        try:
            with sqlite3.connect(self.__veritabani_yolu) as baglanti:
                imlec = baglanti.cursor()
                imlec.execute("""INSERT INTO performans 
                                (ad, soyad, sinif, oyun, dogru, yanlis, ort_tepki) 
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (ad.capitalize(), soyad.upper(), sinif, oyun, dogru, yanlis, tepki))
                baglanti.commit()
        except sqlite3.Error as e:
            print(f"Veri Kayıt Hatası: {e}")

    def kullanici_ekle(self, ad, soyad, sifre, rol, sinif, sube):
        """Yeni kullanıcı kayıt algoritması."""
        with sqlite3.connect(self.__veritabani_yolu) as baglanti:
            imlec = baglanti.cursor()
            imlec.execute("SELECT * FROM kullanicilar WHERE ad=? AND soyad=?", (ad, soyad))
            if imlec.fetchone(): return False
            imlec.execute("INSERT INTO kullanicilar (ad, soyad, sifre, rol, sinif, sube) VALUES (?,?,?,?,?,?)",
                           (ad, soyad, sifre, rol, sinif, sube))
            baglanti.commit()
            return True

    def giris_kontrol(self, ad, soyad, sifre, rol):
        """Kimlik doğrulama algoritması."""
        with sqlite3.connect(self.__veritabani_yolu) as baglanti:
            imlec = baglanti.cursor()
            imlec.execute("SELECT * FROM kullanicilar WHERE ad=? AND soyad=? AND sifre=? AND rol=?", 
                           (ad, soyad, sifre, rol))
            return imlec.fetchone()

    @property
    def db_yolu(self):
        """Property: Veritabanı yoluna kontrollü erişim."""
        return self.__veritabani_yolu