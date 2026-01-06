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
# KOD ORGANİZASYONU: Proje mantığı (Logic) ve Görsel Arayüz (UI) birbirinden ayrılmıştır.
# Bu modüler yapı, kodun okunabilirliğini artırarak 'Clean Code' standartlarını sağlar.
try:
    from oyunlar import EvrenselArkaPlan, FarkliNesneyiBul, HafizaLambalari, DiziTamamlama
except ImportError:
    print("SİSTEM HATASI: 'oyunlar.py' modülü bulunamadı!")
    sys.exit()

# =============================================================================================
# 2. BÖLÜM: VERİTABANI YÖNETİM SİSTEMİ (OOP: ENCAPSULATION - KAPSÜLLEME)
# =============================================================================================
class VeriTabaniSistemi:
    """
    KAPSÜLLEME (ENCAPSULATION): Veritabanı dosya yolu private (__) niteliklerle 
    gizlenerek veri güvenliği ve bütünlüğü sağlanmıştır.
    """
    def __init__(self):
        self.__veritabani_dosya_yolu = "dusadim_final_V100.db"
        self.__veritabani_tablo_yapilarini_yapilandir()

    def __veritabani_tablo_yapilarini_yapilandir(self):
        """VERİ YAPILARI: SQL tabloları, ÖÖG analizi için normalize edilmiş yapıda kurulur."""
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti_objesi:
                imlec = baglanti_objesi.cursor()
                imlec.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                ad TEXT NOT NULL, soyad TEXT NOT NULL, 
                                sifre TEXT NOT NULL, rol TEXT NOT NULL, 
                                sinif TEXT, sube TEXT)''')
                
                imlec.execute('''CREATE TABLE IF NOT EXISTS performans 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                ad TEXT, soyad TEXT, sinif TEXT, oyun TEXT, 
                                dogru INTEGER, yanlis INTEGER, tepki_suresi REAL, 
                                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                baglanti_objesi.commit()
        except sqlite3.Error as e:
            print(f"SQL Hatası: {e}")

    def performans_kaydet(self, ad, soyad, sinif, oyun, dogru, yanlis, sure):
        """Dinamik Veri İşleme: Oyun modüllerinden gelen verileri SQL'e aktarır."""
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                sql = "INSERT INTO performans (ad, soyad, sinif, oyun, dogru, yanlis, tepki_suresi) VALUES (?,?,?,?,?,?,?)"
                imlec.execute(sql, (ad.capitalize(), soyad.upper(), sinif, oyun, dogru, yanlis, sure))
                baglanti.commit()
        except sqlite3.Error as e:
            print(f"Kayıt Hatası: {e}")

    def kullanici_kayit_islemi(self, ad, soyad, sifre, rol, sinif="N/A", sube="N/A"):
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                imlec.execute("SELECT * FROM kullanicilar WHERE ad=? AND soyad=?", (ad, soyad))
                if imlec.fetchone(): return False
                imlec.execute("INSERT INTO kullanicilar (ad, soyad, sifre, rol, sinif, sube) VALUES (?,?,?,?,?,?)", 
                               (ad, soyad, sifre, rol, sinif, sube))
                baglanti.commit()
                return True
        except sqlite3.Error: return False

    def kullanici_dogrulama(self, ad, soyad, sifre, rol):
        try:
            with sqlite3.connect(self.__veritabani_dosya_yolu) as baglanti:
                imlec = baglanti.cursor()
                imlec.execute("SELECT * FROM kullanicilar WHERE ad=? AND soyad=? AND sifre=? AND rol=?", (ad, soyad, sifre, rol))
                return imlec.fetchone()
        except sqlite3.Error: return None

# =============================================================================================
# 3. BÖLÜM: ANA PORTAL YÖNETİMİ (OOP: COMPOSITION - BİLEŞİM)
# =============================================================================================
class DusAdimPortal:
    """
    BİLEŞİM (COMPOSITION): Portal sınıfı, Veritabanı nesnesini içsel bir bileşen olarak 
    yöneterek nesne yönelimli hiyerarşiyi uygular.
    """
    def __init__(self):
        self.__vt_motoru = VeriTabaniSistemi() 
        self.pencere = tk.Tk()
        self.pencere.title("DüşAdım Portal")
        self.pencere.geometry("900x750")
        self.pencere.resizable(False, False)
        # VERİ YAPISI: Parçacık animasyonu için dinamik liste kullanımı.
        self.yildiz_parcacik_havuzu = [] 
        self.arayuz_bilesenlerini_kur()

    def arayuz_bilesenlerini_kur(self):
        for widget in self.pencere.winfo_children(): widget.destroy()
        self.canvas_alani = tk.Canvas(self.pencere, width=900, height=750, bg="#090A0F", highlightthickness=0)
        self.canvas_alani.pack(fill="both", expand=True)
        self.__dinamik_yildiz_parcaciklari_olustur(150)
        self.canvas_alani.create_text(450, 80, text="DÜŞADIM PORTAL", font=("Segoe UI", 35, "bold"), fill="white")
        self.__panel_arayuzunu_ciz(280, "#2980b9", "ÖĞRENCİ PORTALI", "Ogrenci")
        self.__panel_arayuzunu_ciz(620, "#27ae60", "ÖĞRETMEN PANELİ", "Ogretmen")
        self.__arkaplan_animasyonunu_yurut()

    def __panel_arayuzunu_ciz(self, x, renk, baslik, mod):
        cerceve = tk.Frame(self.pencere, bg="white", highlightthickness=3, highlightbackground=renk)
        self.canvas_alani.create_window(x, 430, window=cerceve, width=320, height=380)
        tk.Label(cerceve, text=baslik, font=("Arial", 16, "bold"), bg="white", fg=renk).pack(pady=20)
        ikon = "👤" if mod=="Ogrenci" else "👨‍🏫"
        tk.Label(cerceve, text=ikon, font=("Arial", 50), bg="white").pack(pady=10)
        tk.Button(cerceve, text="KAYIT OL", bg="#ecf0f1", width=18, font=("Arial", 10, "bold"), command=lambda: self.form_ac(f"{mod}_Kayit")).pack(pady=10)
        tk.Button(cerceve, text="GİRİŞ YAP", bg=renk, fg="white", width=18, font=("Arial", 10, "bold"), command=lambda: self.form_ac(f"{mod}_Giris")).pack(pady=5)

    def __dinamik_yildiz_parcaciklari_olustur(self, n):
        for _ in range(n):
            x = random.randint(0, 900); y = random.randint(0, 750); hiz = random.uniform(0.1, 0.3)
            yid = self.canvas_alani.create_oval(x, y, x+2, y+2, fill="white", outline="")
            self.yildiz_parcacik_havuzu.append([yid, x, y, hiz])

    def __arkaplan_animasyonunu_yurut(self):
        for yildiz in self.yildiz_parcacik_havuzu:
            yildiz[2] -= yildiz[3]
            if yildiz[2] < -5: yildiz[2] = 755
            self.canvas_alani.coords(yildiz[0], yildiz[1], yildiz[2], yildiz[1]+2, yildiz[2]+2)
        self.pencere.after(30, self.__arkaplan_animasyonunu_yurut)

    def form_ac(self, mod_tipi):
        f_pencere = tk.Toplevel(self.pencere); f_pencere.geometry("420x600"); f_pencere.grab_set()
        giris_sozlugu = {}
        alanlar = ["Ad", "Soyad", "Şifre"]
        if "Kayit" in mod_tipi and "Ogrenci" in mod_tipi: alanlar += ["Sınıf", "Şube"]
        for alan in alanlar:
            tk.Label(f_pencere, text=f"{alan.upper()}:", font=("Arial", 9, "bold")).pack(pady=5)
            if alan == "Sınıf":
                box = ttk.Combobox(f_pencere, values=["Okul Öncesi", "1. Sınıf", "2. Sınıf"], state="readonly"); box.set("1. Sınıf")
            elif alan == "Şube":
                box = ttk.Combobox(f_pencere, values=["A", "B", "C", "D"], state="readonly"); box.set("A")
            else:
                box = tk.Entry(f_pencere, font=("Arial", 12), show="*" if alan=="Şifre" else "")
            box.pack(pady=5, padx=50, fill="x"); giris_sozlugu[alan] = box
        tk.Button(f_pencere, text="DEVAM ET", bg="#e67e22", fg="white", font=("Arial", 11, "bold"), command=lambda: self.portal_kontrol(mod_tipi, giris_sozlugu, f_pencere)).pack(pady=30)

    def portal_kontrol(self, mod, veri_dict, win):
        ad = veri_dict["Ad"].get().strip().capitalize(); soy = veri_dict["Soyad"].get().strip().upper(); sif = veri_dict["Şifre"].get().strip()
        sin = veri_dict["Sınıf"].get() if "Sınıf" in veri_dict else "N/A"
        sub = veri_dict["Şube"].get() if "Şube" in veri_dict else "N/A"
        rol = "Ogrenci" if "Ogrenci" in mod else "Ogretmen"
        if not ad or not soy or not sif: messagebox.showwarning("Eksik", "Doldurun!"); return
        if "Kayit" in mod:
            if self.__vt_motoru.kullanici_kayit_islemi(ad, soy, sif, rol, sin, sub): messagebox.showinfo("OK", "Kayıt Başarılı."); win.destroy()
            else: messagebox.showerror("Hata", "Mevcut!")
        else:
            u = self.__vt_motoru.kullanici_dogrulama(ad, soy, sif, rol)
            if u:
                win.destroy()
                if rol == "Ogrenci":
                    self.aktif_kullanici = {"ad": ad, "soyad": soy, "sinif": u[5], "sube": u[6]}
                    self.pygame_portalini_baslat()
                else: self.ogretmen_paneli(ad, soy)
            else: messagebox.showerror("Hata", "Yanlış Bilgi!")

    def ogretmen_paneli(self, ad, soy):
        p = tk.Toplevel(self.pencere); p.geometry("600x550")
        tk.Label(p, text=f"Sayın {ad} {soy}", font=("Arial", 14, "bold")).pack(pady=20)
        e_ad = tk.Entry(p, justify='center'); e_ad.insert(0, "Öğrenci Adı"); e_ad.pack(pady=5, padx=100, fill="x")
        e_so = tk.Entry(p, justify='center'); e_so.insert(0, "Öğrenci Soyadı"); e_so.pack(pady=5, padx=100, fill="x")
        tk.Button(p, text="ANALİZ GÖSTER", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), command=lambda: self.analiz_yap(e_ad.get(), e_so.get())).pack(pady=30)

    def analiz_yap(self, a, s):
        try:
            with sqlite3.connect("dusadim_final_V100.db") as bag:
                df = pd.read_sql_query(f"SELECT * FROM performans WHERE ad='{a.capitalize()}' AND soyad='{s.upper()}'", bag)
            
            if df.empty: 
                messagebox.showinfo("Bilgi", "Kayıt bulunamadı."); return
            
            plt.figure(figsize=(12, 6))
            
            # --- SOL GRAFİK: HIZ ANALİZİ (GÜNCELLENEN KISIM) ---
            plt.subplot(1, 2, 1)
            # Her oyunu benzersiz bir renk ve isimle grafiğe ekler
            for oyun_adi in df['oyun'].unique():
                oyun_df = df[df['oyun'] == oyun_adi]
                plt.plot(oyun_df.index + 1, oyun_df['tepki_suresi'], marker='o', linewidth=2, label=oyun_adi)
            
            plt.title(f"{a.capitalize()} - Bilişsel Hız Analizi")
            plt.xlabel("Oturum Sayısı")
            plt.ylabel("Tepki Süresi (ms)")
            plt.legend() # Sağ üstteki "Hangi renk hangi oyun" kutusu
            plt.grid(True, linestyle='--', alpha=0.6) # Arka plana yardımcı çizgiler ekler
            
            # --- SAĞ GRAFİK: BAŞARI ORANI ---
            plt.subplot(1, 2, 2)
            plt.pie([df['dogru'].sum(), df['yanlis'].sum()], labels=['Başarı', 'Hata'], 
                    autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=140)
            plt.title("Kümülatif Başarı Oranı")
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e: 
            messagebox.showerror("Analiz Hatası", f"Veri işlenemedi: {e}")

    # =============================================================================================
    # 4. BÖLÜM: OYUN SEÇİM MENÜSÜ (OOP: POLYMORPHISM - ÇOK BİÇİMLİLİK)
    # =============================================================================================
    def pygame_portalini_baslat(self):
        """
        ÇOK BİÇİMLİLİK (POLYMORPHISM): Farklı oyun nesneleri, ortak metot yapıları ile 
        çağrılarak sistemde esneklik sağlanmıştır.
        """
        self.pencere.withdraw(); pygame.init()
        ekran = pygame.display.set_mode((1000, 700))
        arkaplan = EvrenselArkaPlan(1000, 700)
        font_b = pygame.font.SysFont("Segoe UI", 40, bold=True)
        
        while True:
            arkaplan.ciz(ekran, mod="KOYU")
            t = font_b.render(f"Hoş Geldin, {self.aktif_kullanici['ad'].upper()}", True, (255, 255, 255))
            ekran.blit(t, (500 - t.get_width()//2, 80))
            
            # --- RENKLİ BUTONLAR (ORİJİNAL RENK PALETİNE SADIK KALINDI) ---
            b_alanlari = [pygame.Rect(300, 180, 400, 80), pygame.Rect(300, 280, 400, 80), pygame.Rect(300, 380, 400, 80)]
            b_renkleri = [(41, 128, 185), (142, 68, 173), (211, 84, 0)] # Mavi, Mor, Turuncu
            names = ["1. FARKLI NESNEYİ BUL", "2. HAFIZA LAMBALARI", "3. DİZİ TAMAMLAMA"]
            
            for i, rect in enumerate(b_alanlari):
                pygame.draw.rect(ekran, b_renkleri[i], rect, border_radius=20)
                pygame.draw.rect(ekran, (255, 255, 255), rect, 3, border_radius=20)
                txt = pygame.font.SysFont("Segoe UI", 26, bold=True).render(names[i], True, (255, 255, 255))
                ekran.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            
            # --- ANA MENÜYE DÖN BUTONU (YEŞİL) ---
            btn_exit = pygame.Rect(400, 520, 200, 50)
            pygame.draw.rect(ekran, (39, 174, 96), btn_exit, border_radius=15)
            pygame.draw.rect(ekran, (255, 255, 255), btn_exit, 2, border_radius=15)
            txt_ex = pygame.font.SysFont("Segoe UI", 18, bold=True).render("ANA MENÜYE DÖN", True, (255, 255, 255))
            ekran.blit(txt_ex, (btn_exit.centerx-txt_ex.get_width()//2, btn_exit.centery-txt_ex.get_height()//2))

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if b_alanlari[0].collidepoint(ev.pos): FarkliNesneyiBul(ekran, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    if b_alanlari[1].collidepoint(ev.pos): HafizaLambalari(ekran, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    if b_alanlari[2].collidepoint(ev.pos): DiziTamamlama(ekran, self.__vt_motoru, self.aktif_kullanici["sinif"], self.aktif_kullanici).calistir()
                    if btn_exit.collidepoint(ev.pos): 
                        pygame.quit(); self.pencere.deiconify(); self.arayuz_bilesenlerini_kur(); return
            
            pygame.display.flip(); pygame.time.Clock().tick(60)

if __name__ == "__main__":
    app = DusAdimPortal()
    app.pencere.mainloop()