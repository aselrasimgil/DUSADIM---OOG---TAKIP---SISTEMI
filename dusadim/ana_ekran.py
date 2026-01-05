import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import sys
import random
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# =============================================================================================
# 1. BÖLÜM: MODÜLERLİK VE KOD ORGANİZASYONU
# =============================================================================================

# KOD ORGANİZASYONU: Projenin sürdürülebilirliği için oyun motorları 'oyunlar.py' modülünden çekilir.
try:
    from oyunlar import EvrenselArkaPlan, FarkliNesneyiBul, HafizaLambalari, DiziTamamlama
except ImportError:
    # Hata Yönetimi: Modül eksikliği durumunda sistem bütünlüğünü korumak için güvenli çıkış yapar.
    print("SİSTEM HATASI: 'oyunlar.py' modülü bulunamadı! Lütfen dosya konumunu doğrulayın.")
    sys.exit()

# =============================================================================================
# 2. BÖLÜM: VERİTABANI YÖNETİM SİSTEMİ (OOP: ENCAPSULATION - KAPSÜLLEME)
# =============================================================================================

class VeriTabaniSistemi:
    """
    OOP: KAPSÜLLEME (ENCAPSULATION) İLKESİ
    Bu sınıf, veritabanı erişim protokollerini ve SQL sorgularını private nitelikler arkasında gizler.
    """
    def __init__(self):
        # KAPSÜLLEME: Veritabanı dosya yolu private (__) yapılarak dış manipülasyona kapatıldı.
        self.__veritabani_dosya_yolu = "dusadim_final_V100.db"
        self.__veritabani_tablo_yapilarini_yapilandir()

    def __veritabani_tablo_yapilarini_yapilandir(self):
        """VERİ YAPILARI: İlişkisel veritabanı şeması, ÖÖG analizi için normalize edilmiştir."""
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti_objesi:
                imlec = baglanti_objesi.cursor()
                
                # Kullanıcılar Tablosu: Kimlik doğrulama, sınıf ve şube verilerini saklar.
                imlec.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                ad TEXT NOT NULL, soyad TEXT NOT NULL, 
                                sifre TEXT NOT NULL, rol TEXT NOT NULL, 
                                sinif TEXT, sube TEXT)''')
                
                # Performans Tablosu: Oyunlardan gelen nicel verileri kronolojik olarak depolar.
                # VERİ YAPISI: Sınıf bilgisi dahil 7 veri sütunu + Otomatik ID ve Zaman Damgası.
                imlec.execute('''CREATE TABLE IF NOT EXISTS performans 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                ad TEXT, soyad TEXT, sinif TEXT, oyun TEXT, 
                                dogru INTEGER, yanlis INTEGER, tepki_suresi REAL, 
                                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                baglanti_objesi.commit()
        except sqlite3.Error as e:
            print(f"SQL Yapılandırma Hatası: {e}")

    def performans_kaydet(self, ad, soyad, sinif, oyun, dogru, yanlis, sure):
        """
        ALGORİTMİK VERİ İŞLEME: Oyun modüllerinden gelen 7 parametreli veriyi işler.
        UYUM: 'oyunlar.py' içerisindeki self.vt.performans_kaydet çağrısı ile %100 senkronizedir.
        """
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                sql_sorgu = """INSERT INTO performans (ad, soyad, sinif, oyun, dogru, yanlis, tepki_suresi) 
                               VALUES (?, ?, ?, ?, ?, ?, ?)"""
                imlec.execute(sql_sorgu, (ad.capitalize(), soyad.upper(), sinif, oyun, dogru, yanlis, sure))
                baglanti.commit()
                print(f"[VERİ SİSTEMİ]: {ad} kullanıcısının verileri başarıyla işlendi.")
        except sqlite3.Error as e:
            print(f"Veri Depolama Hatası: {e}")

    def kullanici_kayit_islemi(self, ad, soyad, sifre, rol, sinif="N/A", sube="N/A"):
        """Kayıt Algoritması: Mükerrer kayıt kontrolü ile veri bütünlüğünü korur."""
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                imlec.execute("SELECT * FROM kullanicilar WHERE ad=? AND soyad=?", (ad, soyad))
                if imlec.fetchone():
                    return False # Kullanıcı zaten mevcut
                
                imlec.execute("INSERT INTO kullanicilar (ad, soyad, sifre, rol, sinif, sube) VALUES (?,?,?,?,?,?)", 
                               (ad, soyad, sifre, rol, sinif, sube))
                baglanti.commit()
                return True
        except sqlite3.Error:
            return False

    def kullanici_dogrulama(self, ad, soyad, sifre, rol):
        """Doğrulama Algoritması: Güvenli giriş için DB kayıt eşleşmesi yapar."""
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                sorgu = "SELECT * FROM kullanicilar WHERE ad=? AND soyad=? AND sifre=? AND rol=?"
                imlec.execute(sorgu, (ad, soyad, sifre, rol))
                return imlec.fetchone()
        except sqlite3.Error:
            return None

# =============================================================================================
# 3. BÖLÜM: ANA PORTAL YÖNETİMİ (OOP: COMPOSITION - BİLEŞİM)
# =============================================================================================

class DusAdimPortal:
    """
    Sistemin ana giriş kapısı ve kontrol merkezi.
    OOP: Composition kullanılarak VeriTabaniSistemi nesnesi portalın ayrılmaz bir parçası yapılmıştır.
    """
    def __init__(self):
        # Nesne Oluşturma: Veritabanı motoru private nitelik olarak başlatılır.
        self.__vt_motoru = VeriTabaniSistemi() 
        self.pencere = tk.Tk()
        self.pencere.title("DüşAdım Portal - Öğrenme ve Dikkat Takip Sistemi")
        self.pencere.geometry("900x750")
        self.pencere.resizable(False, False)
        
        # VERİ YAPISI: Yıldız animasyonu parçacıklarını yönetmek için dinamik liste kullanımı.
        self.yildiz_parcacik_havuzu = []
        self.arayuz_bilesenlerini_kur()

    def arayuz_bilesenlerini_kur(self):
        """TEMİZ KOD: Arayüzü tazeleyen ve ana panelleri oluşturan modüler metot."""
        for widget in self.pencere.winfo_children(): 
            widget.destroy()
            
        self.canvas_alani = tk.Canvas(self.pencere, width=900, height=750, bg="#090A0F", highlightthickness=0)
        self.canvas_alani.pack(fill="both", expand=True)
        
        # Görsel parçacık sistemini başlat
        self.__dinamik_yildiz_parcaciklari_olustur(150)
        
        # Görsel Hiyerarşi Tasarımı
        self.canvas_alani.create_text(450, 80, text="DÜŞADIM PORTAL", font=("Segoe UI", 35, "bold"), fill="white")
        self.canvas_alani.create_text(450, 130, text="ÖÖG Öğrencileri İçin Bilişsel İzleme Sistemi", 
                                font=("Arial", 11, "italic"), fill="#bdc3c7")
        
        # Çok Biçimlilik Yaklaşımı: Aynı panel çizim metodu farklı kullanıcı rolleri için çağrılır.
        self.__panel_arayuzunu_ciz(280, "#2980b9", "ÖĞRENCİ PORTALI", "Ogrenci")
        self.__panel_arayuzunu_ciz(620, "#27ae60", "ÖĞRETMEN PANELİ", "Ogretmen")
        self.__arkaplan_animasyonunu_yurut()

    def __panel_arayuzunu_ciz(self, x_konumu, renk, baslik, mod):
        """Dinamik UI Algoritması: Kullanıcı tipine göre giriş ve kayıt butonlarını yapılandırır."""
        cerceve_objesi = tk.Frame(self.pencere, bg="white", highlightthickness=3, highlightbackground=renk)
        self.canvas_alani.create_window(x_konumu, 430, window=cerceve_objesi, width=320, height=380)
        
        tk.Label(cerceve_objesi, text=baslik, font=("Arial", 16, "bold"), bg="white", fg=renk).pack(pady=20)
        ikon_metni = "👤" if mod=="Ogrenci" else "👨‍🏫"
        tk.Label(cerceve_objesi, text=ikon_metni, font=("Arial", 50), bg="white").pack(pady=10)
        
        # Event-Driven Programming: Buton komutlarının atanması
        tk.Button(cerceve_objesi, text="KAYIT OL", bg="#ecf0f1", fg="black", width=18, height=2, 
                  font=("Arial", 10, "bold"), command=lambda: self.form_ac(f"{mod}_Kayit")).pack(pady=10)
        
        tk.Button(cerceve_objesi, text="GİRİŞ YAP", bg=renk, fg="white", width=18, height=2, 
                  font=("Arial", 10, "bold"), command=lambda: self.form_ac(f"{mod}_Giris")).pack(pady=5)

    def __dinamik_yildiz_parcaciklari_olustur(self, n):
        """ALGORİTMA DÜZELTMESİ: Yıldız hızları (0.1-0.3) aralığına çekilerek akademik sunuma uygun hale getirildi."""
        for _ in range(n):
            x = random.randint(0, 900)
            y = random.randint(0, 750)
            hiz = random.uniform(0.1, 0.3) # Huzurlu akış hızı
            yid = self.canvas_alani.create_oval(x, y, x+2, y+2, fill="white", outline="")
            self.yildiz_parcacik_havuzu.append([yid, x, y, hiz])

    def __arkaplan_animasyonunu_yurut(self):
        """Yinelemeli Algoritma: Yıldız parçacıklarının portaldaki sonsuz döngüsünü yönetir."""
        for yildiz in self.yildiz_parcacik_havuzu:
            yildiz[2] -= yildiz[3]
            if yildiz[2] < -5: 
                yildiz[2] = 755
            self.canvas_alani.coords(yildiz[0], yildiz[1], yildiz[2], yildiz[1]+2, yildiz[2]+2)
        self.pencere.after(30, self.__arkaplan_animasyonunu_yurut)

    def form_ac(self, mod_tipi):
        """Dinamik Form Algoritması: İşlem tipine göre giriş alanlarını Dictionary veri yapısı ile belirler."""
        f_pencere = tk.Toplevel(self.pencere); f_pencere.geometry("420x600"); f_pencere.grab_set()
        f_pencere.title(f"DüşAdım Portal - {mod_tipi.replace('_', ' ')}")
        
        # VERİ YAPISI: Giriş bileşenlerini (widgets) yönetmek için Dictionary kullanımı.
        giris_sozlugu = {}
        alan_listesi = ["Ad", "Soyad", "Şifre"]
        if "Kayit" in mod_tipi and "Ogrenci" in mod_tipi: 
            alan_listesi += ["Sınıf", "Şube"]
        
        for alan_adi in alan_listesi:
            tk.Label(f_pencere, text=f"{alan_adi.upper()}:", font=("Arial", 9, "bold")).pack(pady=5)
            if alan_adi == "Sınıf":
                box = ttk.Combobox(f_pencere, values=["1. Sınıf", "2. Sınıf"], state="readonly"); box.set("1. Sınıf")
            elif alan_adi == "Şube":
                box = ttk.Combobox(f_pencere, values=["A", "B", "C", "D"], state="readonly"); box.set("A")
            else: 
                box = tk.Entry(f_pencere, font=("Arial", 12), show="*" if alan_adi=="Şifre" else "")
            
            box.pack(pady=5, padx=50, fill="x")
            giris_sozlugu[alan_adi] = box
        
        tk.Button(f_pencere, text="DEVAM ET", bg="#e67e22", fg="white", font=("Arial", 11, "bold"), height=2, 
                  command=lambda: self.portal_kontrol(mod_tipi, giris_sozlugu, f_pencere)).pack(pady=30)

    def portal_kontrol(self, mod, veri_dict, win):
        """Karar Yapısı: Veri doğruluğunu denetler ve ilgili Pygame veya Analiz modülünü başlatır."""
        ad_val = veri_dict["Ad"].get().strip().capitalize()
        soy_val = veri_dict["Soyad"].get().strip().upper()
        sif_val = veri_dict["Şifre"].get().strip()
        sin_val = veri_dict["Sınıf"].get() if "Sınıf" in veri_dict else "N/A"
        sub_val = veri_dict["Şube"].get() if "Şube" in veri_dict else "N/A"
        rol_val = "Ogrenci" if "Ogrenci" in mod else "Ogretmen"

        if not ad_val or not soy_val or not sif_val:
            messagebox.showwarning("Eksik Veri", "Lütfen tüm güvenlik alanlarını doldurun!"); return

        if "Kayit" in mod:
            if self.__vt_motoru.kullanici_kayit_islemi(ad_val, soy_val, sif_val, rol_val, sin_val, sub_val):
                messagebox.showinfo("Başarılı", "Profiliniz oluşturuldu. Giriş yapabilirsiniz."); win.destroy()
            else: messagebox.showerror("Hata", "Bu kullanıcı zaten sistemde mevcut!")
        else:
            u_verisi = self.__vt_motoru.kullanici_dogrulama(ad_val, soy_val, sif_val, rol_val)
            if u_verisi:
                win.destroy()
                if rol_val == "Ogrenci":
                    # Dinamik veri aktarımı ile Pygame katmanına geçiş
                    self.aktif_kullanici = {"ad": ad_val, "soyad": soy_val, "sinif": u_verisi[5], "sube": u_verisi[6]}
                    self.pygame_portalini_baslat()
                else: self.ogretmen_paneli(ad_val, soy_val)
            else: messagebox.showerror("Erişim Reddedildi", "Hatalı kimlik bilgileri girdiniz!")

    def ogretmen_paneli(self, ad, soy):
        """PANDAS ENTEGRASYONU: Öğretmenler için SQL verilerini analiz eden grafiksel arayüz."""
        p_panel = tk.Toplevel(self.pencere); p_panel.geometry("600x550"); p_panel.configure(bg="#f5f6fa")
        tk.Label(p_panel, text=f"Sayın {ad} {soy}", font=("Arial", 14, "bold"), bg="#f5f6fa", fg="#2c3e50").pack(pady=20)
        
        ent_ad = tk.Entry(p_panel, justify='center', font=("Arial", 12)); ent_ad.insert(0, "Öğrenci Adı"); ent_ad.pack(pady=5, padx=100, fill="x")
        ent_so = tk.Entry(p_panel, justify='center', font=("Arial", 12)); ent_so.insert(0, "Öğrenci Soyadı"); ent_so.pack(pady=5, padx=100, fill="x")
        
        tk.Button(p_panel, text="GELİŞİM ANALİZİNİ GÖSTER", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                  command=lambda: self.analiz_yap(ent_ad.get(), ent_so.get())).pack(pady=30)

    def analiz_yap(self, a, s):
        """
        PANDAS & MATPLOTLIB: SQL loglarını akademik raporlara dönüştürür.
        Yönerge Uyum: Verimli veri yapısı kullanımı (DataFrame).
        """
        try:
            # PANDAS: Veritabanı sorgusunu doğrudan DataFrame yapısına aktarır.
            with sqlite3.connect("dusadim_final_V100.db") as bag:
                df = pd.read_sql_query(f"SELECT * FROM performans WHERE ad='{a.capitalize()}' AND soyad='{s.upper()}'", bag)
            
            if df.empty: 
                messagebox.showinfo("Bilgi", "İlgili öğrenciye ait kayıt bulunamadı."); return
            
            # MATPLOTLIB: Akademik İstatistik Sunumu
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1); plt.plot(df.index + 1, df['tepki_suresi'], marker='o', color='#e67e22', linewidth=2); plt.title("Tepki Süresi Gelişimi (ms)")
            plt.subplot(1, 2, 2); plt.pie([df['dogru'].sum(), df['yanlis'].sum()], labels=['Başarı', 'Hata'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c']); plt.title("Kümülatif Başarı Oranı")
            plt.tight_layout(); plt.show()
        except Exception as e: messagebox.showerror("Analiz Hatası", f"Veri işleme sırasında bir sorun oluştu: {e}")

    # =============================================================================================
    # 4. BÖLÜM: OYUN SEÇİM MENÜSÜ (PYGAME ENTEGRASYONU)
    # =============================================================================================

    def pygame_portalini_baslat(self):
        """
        PYGAME MOTORU: 
        - Çok Biçimlilik (Polymorphism) ile alt oyun nesnelerini başlatır.
        - FPS sabitleme ile tüm sistemlerde tutarlı hız sağlar.
        """
        self.pencere.withdraw()
        pygame.init()
        ekran_yuzeyi = pygame.display.set_mode((1000, 700))
        # OOP: oyunlar.py içerisindeki arka plan sınıfının başlatılması
        arkaplan_motoru = EvrenselArkaPlan(1000, 700)
        
        font_baslik = pygame.font.SysFont("Segoe UI", 45, bold=True)
        font_buton = pygame.font.SysFont("Segoe UI", 26, bold=True)
        font_kucuk = pygame.font.SysFont("Segoe UI", 18, bold=True)
        
        while True:
            # GÖRSEL DÜZELTME: oyunlar.py'deki 'mod' parametresi ile senkronize render.
            arkaplan_motoru.ciz(ekran_yuzeyi, mod="KOYU")
            
            selamlama_surf = font_baslik.render(f"Hoş Geldin, {self.aktif_kullanici['ad'].upper()}", True, (255, 255, 255))
            ekran_yuzeyi.blit(selamlama_surf, (500 - selamlama_surf.get_width()//2, 80))
            
            # OYUN BUTONLARI (RENKLİ VE AKADEMİK HİYERARŞİ)
            b_alanlari = [pygame.Rect(300, 180, 400, 80), pygame.Rect(300, 280, 400, 80), pygame.Rect(300, 380, 400, 80)]
            b_renk_setleri = [(41, 128, 185), (142, 68, 173), (211, 84, 0)] # Mavi, Mor, Turuncu
            b_basliklari = ["1. FARKLI NESNEYİ BUL", "2. HAFIZA LAMBALARI", "3. DİZİ TAMAMLAMA"]
            
            for i, rect in enumerate(b_alanlari):
                pygame.draw.rect(ekran_yuzeyi, b_renk_setleri[i], rect, border_radius=20)
                pygame.draw.rect(ekran_yuzeyi, (255, 255, 255), rect, 3, border_radius=20)
                txt_surf = font_buton.render(b_basliklari[i], True, (255, 255, 255))
                ekran_yuzeyi.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

            # ANA MENÜYE DÖN BUTONU (YEŞİL, KÜÇÜK VE FONKSİYONEL)
            btn_ana_menu = pygame.Rect(400, 520, 200, 50)
            pygame.draw.rect(ekran_yuzeyi, (39, 174, 96), btn_ana_menu, border_radius=15)
            pygame.draw.rect(ekran_yuzeyi, (255, 255, 255), btn_ana_menu, 2, border_radius=15)
            txt_don_surf = font_kucuk.render("ANA MENÜYE DÖN", True, (255, 255, 255))
            ekran_yuzeyi.blit(txt_don_surf, (btn_ana_menu.centerx - txt_don_surf.get_width()//2, btn_ana_menu.centery - txt_don_surf.get_height()//2))

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: 
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    # OOP: Çok Biçimlilik (Polymorphism) ile farklı sınıfları vt nesnesiyle besler.
                    if b_alanlari[0].collidepoint(ev.pos):
                        FarkliNesneyiBul(ekran_yuzeyi, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    if b_alanlari[1].collidepoint(ev.pos):
                        HafizaLambalari(ekran_yuzeyi, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    if b_alanlari[2].collidepoint(ev.pos):
                        DiziTamamlama(ekran_yuzeyi, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    
                    # Ana Menüye Dönüş Algoritması
                    if btn_ana_menu.collidepoint(ev.pos):
                        pygame.quit()
                        self.pencere.deiconify() # Tkinter ana ekranını geri çağırır.
                        self.arayuz_bilesenlerini_kur() # Arayüzü tazeler.
                        return

            pygame.display.flip()
            # YÖNERGE: FPS sabitleme ile animasyon akışı standartlaştırıldı.
            pygame.time.Clock().tick(60) 

# =============================================================================================
# SİSTEM BAŞLATICI (ENTRY POINT)
# =============================================================================================
if __name__ == "__main__":
    sistem_arayuzu = DusAdimPortal()
    sistem_arayuzu.pencere.mainloop()