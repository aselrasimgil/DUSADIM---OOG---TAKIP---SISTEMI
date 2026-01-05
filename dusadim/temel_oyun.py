import tkinter as tk
import time
from abc import ABC, abstractmethod

# =============================================================================================
# NESNE YÖNELİMLİ PROGRAMLAMA (OOP) İLKELERİ: SOYUTLAMA (ABSTRACTION)
# =============================================================================================

class TemelOyun(ABC):
    """
    Tüm bilişsel oyun modüllerinin miras alacağı soyut ana sınıf (Abstract Base Class).
    Bu sınıf, oyunların ortak özelliklerini (zamanlama, ekran temizleme, veri kaydı) tanımlar.
    """

    def __init__(self, ana_pencere, oyun_basligi):
        """
        KAPSÜLLEME (ENCAPSULATION): 
        Oyunun başlangıç zamanı ve log verileri nesneye özel (private/protected) olarak saklanır.
        """
        self.pencere = ana_pencere
        self.oyun_basligi = oyun_basligi
        
        # Korumalı (Protected) nitelikler: Alt sınıflardan erişilebilir ancak dışarıdan gizlenir.
        self._baslangic_mili_saniye = 0
        self._gecici_log_havuzu = [] 
        
        # Grafik arayüzü başlatma algoritması
        self.ekran_bilesenlerini_hazirla()

    # =============================================================================================
    # KOD ORGANİZASYONU VE TEMİZLİĞİ: ANLAMLI FONKSİYONLAR
    # =============================================================================================

    def ekran_bilesenlerini_hazirla(self):
        """
        MODÜLER YAPI: Mevcut arayüzdeki widget'ları temizler ve yeni oyun alanını kurar.
        Yinelenen koddan kaçınmak için merkezi bir temizlik işlevi görür.
        """
        # Mevcut widgetları temizleme algoritması (Arayüz yönetim algoritması)
        for bilesen in self.pencere.winfo_children():
            bilesen.destroy()
        
        # UI Tasarımı ve Hiyerarşisi
        self.ust_baslik_etiketi = tk.Label(
            self.pencere, 
            text=self.oyun_basligi, 
            font=("Segoe UI", 24, "bold"),
            fg="#2c3e50"
        )
        self.ust_baslik_etiketi.pack(pady=30)

    def tepki_olceri_tetikle(self):
        """
        VERİMLİ ALGORİTMA: time.perf_counter() kullanarak donanım seviyesinde hassas 
        zamanlama verisi elde eder. ÖÖG öğrencilerinin mikro-tepki sürelerini ölçmek için kritiktir.
        """
        self._baslangic_mili_saniye = time.perf_counter()

    def tepki_olceri_durdur_ve_hesapla(self):
        """
        ALGORİTMİK HESAPLAMA: Başlangıç ve bitiş arasındaki farkı hesaplayarak 
        milisaniye cinsinden sonuç döndürür.
        """
        bitis_ani = time.perf_counter()
        # Saniyeyi milisaniyeye çevirme ve yuvarlama algoritması
        hesaplanan_gecen_sure = (bitis_ani - self._baslangic_mili_saniye) * 1000 
        return round(hesaplanan_gecen_sure, 2)

    # =============================================================================================
    # VERİ YAPILARI: LİSTELER VE SÖZLÜKLERİN ETKİN KULLANIMI
    # =============================================================================================

    def log_verisi_olustur_ve_depola(self, ogrenci_no, oturum_tipi, performans_sonucu, milisaniye_sure):
        """
        VERİ YAPILARI: Her bir oyun hamlesi bir 'Dictionary' (Sözlük) olarak yapılandırılır 
        ve bir 'List' (Liste) içinde kronolojik olarak depolanır.
        """
        # Karmaşık veri yapısının yapılandırılması
        yeni_veri_satiri = {
            "ogrenci_id": ogrenci_no,
            "test_modulu": oturum_tipi,
            "dogruluk_durumu": performans_sonucu,  # True/False veya Skor
            "tepki_hizi_ms": milisaniye_sure,
            "kayit_tarihi": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Dinamik listeye veri ekleme (Amortized constant time complexity)
        self._gecici_log_havuzu.append(yeni_veri_satiri)
        
        # Hata ayıklama ve izleme çıktıları (Debug logs)
        print(f"[LOG SİSTEMİ]: Yeni veri kaydedildi -> Modül: {oturum_tipi}, Süre: {milisaniye_sure}ms")

    # =============================================================================================
    # ÇOK BİÇİMLİLİK (POLYMORPHISM) İÇİN ZORUNLU METOTLAR
    # =============================================================================================

    @abstractmethod
    def oyunu_baslat(self):
        """
        Bu metot, miras alan her sınıf tarafından override (ezilmek) zorundadır.
        OOP'nin Çok Biçimlilik (Polymorphism) ilkesini garanti eder.
        """
        pass

    @abstractmethod
    def sonuclari_degerlendir(self):
        """
        Her oyunun kendi başarı kriterlerine göre sonuç üretmesini sağlar.
        """
        pass