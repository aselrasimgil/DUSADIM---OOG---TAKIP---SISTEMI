import pygame
import random
import time
import os
import math
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

# =============================================================================================
# 1. BÖLÜM: GÖRSEL MOTOR VE ATMOSFER SİSTEMLERİ (OOP: ENCAPSULATION - KAPSÜLLEME)
# =============================================================================================

class Yildiz:
    def __init__(self, ekran_genisligi, ekran_yuksekligi):
        self.__x_koordinati = random.randint(0, ekran_genisligi)
        self.__y_koordinati = random.randint(0, ekran_yuksekligi)
        self.__boyut = random.randint(1, 2)
        self.__isik_faz_degeri = random.uniform(0, math.pi * 2)
        self.__isik_degisim_hizi = random.uniform(0.005, 0.015) 

    def guncelle_ve_ciz(self, hedef_yuzey):
        self.__isik_faz_degeri += self.__isik_degisim_hizi
        hesaplanan_alfa = int(150 + 105 * math.sin(self.__isik_faz_degeri))
        yildiz_katmani = pygame.Surface((self.__boyut * 2, self.__boyut * 2), pygame.SRCALPHA)
        pygame.draw.circle(yildiz_katmani, (255, 255, 255), (self.__boyut, self.__boyut), self.__boyut)
        yildiz_katmani.set_alpha(hesaplanan_alfa)
        hedef_yuzey.blit(yildiz_katmani, (self.__x_koordinati, self.__y_koordinati))

class KayanYildiz:
    def __init__(self, genislik, yukseklik):
        self.__limiti_W = genislik
        self.__limiti_H = yukseklik
        self.nesne_niteliklerini_resetle()

    def nesne_niteliklerini_resetle(self):
        self.x_konumu = random.randint(-300, self.__limiti_W // 2)
        self.y_konumu = random.randint(0, self.__limiti_H // 2)
        self.hareket_hizi = random.randint(3, 7)
        self.aktiflik_durumu = False
        self.bekleme_sayaci = random.randint(100, 300)

    def hareket_yurut_ve_ciz(self, hedef_yuzey):
        if not self.aktiflik_durumu:
            self.bekleme_sayaci -= 1
            if self.bekleme_sayaci <= 0:
                self.aktiflik_durumu = True
        else:
            self.x_konumu += self.hareket_hizi
            self.y_konumu += self.hareket_hizi * 0.4
            for i in range(12):
                iz_alfa = int(180 * (1 - i / 12))
                iz_objesi = pygame.Surface((2, 2), pygame.SRCALPHA)
                pygame.draw.circle(iz_objesi, (255, 255, 255, iz_alfa), (1, 1), 1)
                hedef_yuzey.blit(iz_objesi, (int(self.x_konumu - i * 2), int(self.y_konumu - i * 0.8)))
            
            if self.x_konumu > self.__limiti_W or self.y_konumu > self.__limiti_H:
                self.nesne_niteliklerini_resetle()

class EvrenselArkaPlan:
    def __init__(self, W, H):
        self.genislik = W
        self.yukseklik = H
        self.statik_yildiz_havuzu = [Yildiz(W, H) for _ in range(140)]
        self.dinamik_kayan_yildizlar = [KayanYildiz(W, H) for _ in range(3)]
        self.bej_arka_plan_kaplamasi = None
        yol = os.path.join("gorseller", "arka_plan.png")
        if os.path.exists(yol):
            self.bej_arka_plan_kaplamasi = pygame.transform.scale(pygame.image.load(yol).convert(), (W, H))

    def ciz(self, hedef_ekran, mod="KOYU"):
        if mod == "KOYU":
            hedef_ekran.fill((15, 20, 35))
            for yildiz_obj in self.statik_yildiz_havuzu:
                yildiz_obj.guncelle_ve_ciz(hedef_ekran)
            for kayan_obj in self.dinamik_kayan_yildizlar:
                kayan_obj.hareket_yurut_ve_ciz(hedef_ekran)
        elif self.bej_arka_plan_kaplamasi:
            hedef_ekran.blit(self.bej_arka_plan_kaplamasi, (0, 0))
        else:
            hedef_ekran.fill((240, 240, 230))

# =============================================================================================
# 2. BÖLÜM: SOYUT OYUN MOTORU (OOP: ABSTRACTION & INHERITANCE)
# =============================================================================================

class Oyun(ABC):
    def __init__(self, ekran, veritabani, sinif_bilgisi, ogrenci_verisi):
        self.ekran = ekran
        self.vt = veritabani
        self.sinif = sinif_bilgisi
        self.ogrenci = ogrenci_verisi
        self.pencere_W, self.pencere_H = ekran.get_size()
        self.fps_motoru = pygame.time.Clock()
        self.oyun_aktif_durumu = True
        self.mevcut_durum_etiketi = "INTRO_FADE"
        self.toplam_dogru_sayaci = 0
        self.toplam_yanlis_sayaci = 0
        self.hesaplanan_basari_puani = 0
        self.bitis_ani_toplam_sure = 0
        self.final_sesi_calindi_mi = False
        self.font_hud_mini = pygame.font.SysFont("Arial", 18, bold=True)
        self.ana_menuye_donus_butonu = pygame.Rect(self.pencere_W // 2 - 150, 520, 300, 70)
        pygame.mixer.init()
        self.ses_dogru_bildirim = self.__medya_yukle("ding_sesi.mp3")
        self.ses_yanlis_bildirim = self.__medya_yukle("yanlis_ses.mp3")
        self.ses_oyun_sonu = self.__medya_yukle("oyun_bitiris.mp3")
        self.ses_talimat_hafiza = self.__medya_yukle("hafiza_oyun.mp3")
        self.ses_talimat_nesne = self.__medya_yukle("farkli_nesne.mp3")
        self.ses_talimat_dizi = self.__medya_yukle("dizi_oyunu.mp3")

    def __medya_yukle(self, dosya):
        p = os.path.join("sesler", dosya)
        return pygame.mixer.Sound(p) if os.path.exists(p) else None

    @abstractmethod
    def soru_hazirla(self): pass

    @abstractmethod
    def calistir(self): pass

# =============================================================================================
# 3. BÖLÜM: OYUN 1 - FARKLI NESNEYİ BUL (FIXED)
# =============================================================================================

class FarkliNesneyiBul(Oyun):
    def __init__(self, ekran, vt, sinif, ogrenci):
        super().__init__(ekran, vt, sinif, ogrenci)
        self.mevcut_durum_etiketi = "TALIMAT"
        self.font_arayuz = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_baslik = pygame.font.SysFont("Arial", 45, bold=True)
        self.__gorsel_kaynaklari_hazirla()
        self.soru_indeksi = 0
        self.sayac_rakami = 3
        self.__tepki_sureleri_log_listesi = [] # İsim sabitlendi
        self.soru_havuzu = [
            {"n": "kedi.png", "f": "beneksiz_kedi.png"}, {"n": "ev.png", "f": "farkli_ev.png"},
            {"n": "kus.png", "f": "farkli_kus.png"}, {"n": "mor_kulaklik.png", "f": "farkli_kulaklik.png"},
            {"n": "kelebek.png", "f": "farkli_kelebek.png"}, {"n": "koltuk.png", "f": "farkli_koltuk.png"},
            {"n": "yaprak.png", "f": "farkli_yaprak.png"}
        ]
        self.soru_hazirla()

    def __gorsel_kaynaklari_hazirla(self):
        try:
            self.tema_img = pygame.transform.scale(pygame.image.load("gorseller/tema.png"), (self.pencere_W, self.pencere_H))
            self.cerceve_img = pygame.transform.scale(pygame.image.load("gorseller/cerceve.png"), (130, 130))
            self.bar_img = pygame.transform.scale(pygame.image.load("gorseller/ilerleme cubugu.png"), (80, 450))
        except: self.tema_img = self.cerceve_img = self.bar_img = None

    def soru_hazirla(self):
        self.izgara_nesne_listesi = []
        paket = self.soru_havuzu[self.soru_indeksi]
        target_idx = random.randint(0, 15)
        for i in range(16):
            r = pygame.Rect(135 + (i%4)*145, 125 + (i//4)*145, 130, 130)
            file = paket["f"] if i == target_idx else paket["n"]
            img = pygame.transform.scale(pygame.image.load(os.path.join("gorseller", file)).convert_alpha(), (100, 100))
            self.izgara_nesne_listesi.append({"rect": r, "target": (i == target_idx), "img": img})
        self.__soru_baslama_ani = time.time() # İsim sabitlendi

    def calistir(self):
        o_bas, s_gunc = 0, 0
        while self.oyun_aktif_durumu:
            self.ekran.fill((30, 30, 30))
            if self.tema_img: self.ekran.blit(self.tema_img, (0, 0))
            su_an = time.time()
            if self.mevcut_durum_etiketi == "GAME":
                gecen_sn = int(su_an - o_bas)
                self.ekran.blit(self.font_hud_mini.render(f"Skor: {self.hesaplanan_basari_puani}", True, (255,255,255)), (15, 15))
                self.ekran.blit(self.font_hud_mini.render(f"Süre: {gecen_sn}s", True, (255,255,255)), (15, 45))
                self.ekran.blit(self.font_hud_mini.render(f"Tur: {self.soru_indeksi + 1}/7", True, (255,255,255)), (15, 75))
            for olay_v in pygame.event.get():
                if olay_v.type == pygame.QUIT: self.oyun_aktif_durumu = False
                if olay_v.type == pygame.MOUSEBUTTONDOWN:
                    if self.mevcut_durum_etiketi == "TALIMAT": self.mevcut_durum_etiketi = "SAYAC"; s_gunc = su_an
                    elif self.mevcut_durum_etiketi == "BITIS":
                        if self.ana_menuye_donus_butonu.collidepoint(olay_v.pos): self.oyun_aktif_durumu = False
                    elif self.mevcut_durum_etiketi == "GAME":
                        for n in self.izgara_nesne_listesi:
                            if n["rect"].collidepoint(olay_v.pos):
                                if n["target"]:
                                    if self.ses_dogru_bildirim: self.ses_dogru_bildirim.play()
                                    self.toplam_dogru_sayaci += 1; self.hesaplanan_basari_puani += 14
                                    self.__tepki_sureleri_log_listesi.append((su_an - self.__soru_baslama_ani) * 1000)
                                    self.soru_indeksi += 1
                                    if self.soru_indeksi < 7: self.soru_hazirla()
                                    else: 
                                        self.bitis_ani_toplam_sure = int(su_an - o_bas)
                                        self.mevcut_durum_etiketi = "BITIS"; self.bitir()
                                else:
                                    if self.ses_yanlis_bildirim: self.ses_yanlis_bildirim.play()
                                    self.toplam_yanlis_sayaci += 1; self.hesaplanan_basari_puani = max(0, self.hesaplanan_basari_puani - 10)
            if self.mevcut_durum_etiketi == "TALIMAT": self.__karartma_render("FARKLI NESNEYİ BUL", "BAŞLAMAK İÇİN TIKLAYIN")
            elif self.mevcut_durum_etiketi == "SAYAC":
                txt = self.font_baslik.render(str(self.sayac_rakami), True, (255, 255, 255))
                self.ekran.blit(txt, (self.pencere_W//2-txt.get_width()//2, self.pencere_H//2))
                if su_an - s_gunc >= 1: self.sayac_rakami -= 1; s_gunc = su_an
                if self.sayac_rakami == 0: self.mevcut_durum_etiketi = "GAME"; o_bas = su_an; self.ses_talimat_nesne.play() if self.ses_talimat_nesne else None
            elif self.mevcut_durum_etiketi == "GAME":
                for n_v in self.izgara_nesne_listesi:
                    if self.cerceve_img: self.ekran.blit(self.cerceve_img, n_v["rect"])
                    self.ekran.blit(n_v["img"], (n_v["rect"].x + 15, n_v["rect"].y + 15))
            elif self.mevcut_durum_etiketi == "BITIS": self.__finish_render()
            pygame.display.flip(); self.fps_motoru.tick(60)

    def __karartma_render(self, t1, t2):
        s = pygame.Surface((self.pencere_W, self.pencere_H), pygame.SRCALPHA); s.fill((0, 0, 0, 180)); self.ekran.blit(s, (0, 0))
        y1 = self.font_baslik.render(t1, True, (255, 255, 255)); y2 = self.font_arayuz.render(t2, True, (255, 255, 0))
        self.ekran.blit(y1, (self.pencere_W//2-y1.get_width()//2, 300)); self.ekran.blit(y2, (self.pencere_W//2-y2.get_width()//2, 450))

    def __finish_render(self):
        if self.ses_oyun_sonu and not self.final_sesi_calindi_mi: self.ses_oyun_sonu.play(); self.final_sesi_calindi_mi = True
        ov = pygame.Surface((self.pencere_W, self.pencere_H), pygame.SRCALPHA); ov.fill((0, 0, 0, 220)); self.ekran.blit(ov, (0, 0))
        self.__txt_merkez("OYUN BİTTİ!", self.font_baslik, (255, 215, 0), 160)
        self.__txt_merkez(f"Doğru: {self.toplam_dogru_sayaci} | Yanlış: {self.toplam_yanlis_sayaci}", self.font_arayuz, (255, 255, 255), 260)
        self.__txt_merkez(f"Süre: {self.bitis_ani_toplam_sure} sn | Skor: {self.hesaplanan_basari_puani}", self.font_arayuz, (255, 255, 255), 320)
        pygame.draw.rect(self.ekran, (41, 128, 185), self.ana_menuye_donus_butonu, border_radius=15)
        bt = self.font_arayuz.render("ANA MENÜYE DÖN", True, (255, 255, 255))
        self.ekran.blit(bt, (self.ana_menuye_donus_butonu.centerx-bt.get_width()//2, self.ana_menuye_donus_butonu.centery-bt.get_height()//2))

    def __txt_merkez(self, m, f, r, y):
        s = f.render(m, True, r); self.ekran.blit(s, (self.pencere_W//2-s.get_width()//2, y))

    def bitir(self):
        ort = sum(self.__tepki_sureleri_log_listesi)/len(self.__tepki_sureleri_log_listesi) if self.__tepki_sureleri_log_listesi else 0
        self.vt.performans_kaydet(self.ogrenci["ad"], self.ogrenci["soyad"], self.sinif, "Farklı Nesne", self.toplam_dogru_sayaci, self.toplam_yanlis_sayaci, ort)

# =============================================================================================
# 4. BÖLÜM: OYUN 2 - HAFIZA LAMBALARI (FIXED)
# =============================================================================================

class HafizaLambalari(Oyun):
    def __init__(self, ekran, vt, sinif, ogrenci):
        super().__init__(ekran, vt, sinif, ogrenci)
        self.font_arayuz_v = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_dev_v = pygame.font.SysFont("Arial", 65, bold=True)
        self.arkaplan_yoneticisi = EvrenselArkaPlan(self.pencere_W, self.pencere_H)
        self.daire_nesne_listesi_v = [] 
        self.__lamba_konfigurasyonu_kur()
        self.hedef_dizi, self.oyuncu_listesi, self.__logs = [], [], []
        self.aktif_tur_no, self.geri_sayim_rakami = -1, 3
        self.izleme_idx, self.parlama_ms, self.feedback_msg = 0, 0, ""
        self.intro_alpha, self.intro_y = 0, self.pencere_H // 2
        self.tebrik_sozleri = ["Harika! Süpersin!", "Muhteşem!", "Böyle Devam!", "Başardın!"]
        self.soru_hazirla()

    def __lamba_konfigurasyonu_kur(self):
        res = ["yesil_daire.png", "kirmizi_daire.png", "turuncu_daire.png", "mavi_daire.png"]
        cx, cy = self.pencere_W // 2, self.pencere_H // 2 + 100
        pos = [(cx, cy-140), (cx, cy+140), (cx-140, cy), (cx+140, cy)]
        for i, name in enumerate(res):
            img = pygame.transform.scale(pygame.image.load(f"gorseller/{name}").convert_alpha(), (200, 200))
            self.daire_nesne_listesi_v.append({"img": img, "rect": pygame.Rect(pos[i][0]-100, pos[i][1]-100, 200, 200)})

    def soru_hazirla(self):
        self.aktif_tur_no += 1
        n = 2 if self.aktif_tur_no < 2 else (3 if self.aktif_tur_no < 4 else (4 if self.aktif_tur_no < 6 else 5))
        self.hedef_dizi = [random.randint(0, 3) for _ in range(n)]
        self.oyuncu_listesi, self.izleme_idx, self.parlama_ms = [], 0, 0
        self.__soru_bas_z = time.time()

    def calistir(self):
        s_z, t_id, t_son, o_bas = 0, -1, 0, 0 # s_z eklendi Unbound önlemek için
        while self.oyun_aktif_durumu:
            simdi_ms = pygame.time.get_ticks()
            su_an_sn = time.time()
            self.arkaplan_yoneticisi.ciz(self.ekran, mod="BEJ") 
            g_sn = int(su_an_sn - o_bas) if o_bas > 0 else 0
            self.ekran.blit(self.font_hud_mini.render(f"Skor: {self.hesaplanan_basari_puani}", True, (30,30,30)), (15, 15))
            self.ekran.blit(self.font_hud_mini.render(f"Süre: {g_sn}s", True, (30,30,30)), (15, 40))
            self.ekran.blit(self.font_hud_mini.render(f"Tur: {self.aktif_tur_no+1}/7", True, (30,30,30)), (15, 65))
            if self.mevcut_durum_etiketi != "BITIS":
                if self.mevcut_durum_etiketi not in ["INTRO_FADE", "INTRO_MOVE", "SAYAC"]:
                    for d in self.daire_nesne_listesi_v: self.ekran.blit(d["img"], d["rect"])
                    if t_id != -1 and simdi_ms < t_son: self.__isik(self.daire_nesne_listesi_v[t_id]["rect"])
                if self.intro_alpha < 255: self.intro_alpha += 5
                if self.mevcut_durum_etiketi == "INTRO_FADE" and self.intro_alpha >= 255: self.mevcut_durum_etiketi = "INTRO_MOVE"
                elif self.mevcut_durum_etiketi == "INTRO_MOVE":
                    if self.intro_y > 85: self.intro_y -= 4
                    else: 
                        self.mevcut_durum_etiketi = "SAYAC"; s_z = su_an_sn
                        if self.ses_talimat_hafiza: self.ses_talimat_hafiza.play()
                t_surf = self.font_arayuz_v.render("Lambaları Takip Et!", True, (30,30,30))
                t_surf.set_alpha(self.intro_alpha); self.ekran.blit(t_surf, (self.pencere_W//2-t_surf.get_width()//2, self.intro_y))
            if self.mevcut_durum_etiketi == "SAYAC":
                self.__ms_render_v("HAZIR!", self.font_arayuz_v, (52, 152, 219), 250)
                num = self.font_dev_v.render(str(self.geri_sayim_rakami), True, (230, 126, 34))
                self.ekran.blit(num, (self.pencere_W//2-num.get_width()//2, self.pencere_H//2))
                if su_an_sn - s_z >= 1: self.geri_sayim_rakami -= 1; s_z = su_an_sn
                if self.geri_sayim_rakami <= 0: self.mevcut_durum_etiketi = "BEKLEME"; s_z = su_an_sn; o_bas = su_an_sn
            elif self.mevcut_durum_etiketi == "BEKLEME" and su_an_sn - s_z > 1.2: self.mevcut_durum_etiketi = "IZLEME"
            elif self.mevcut_durum_etiketi == "IZLEME":
                if self.izleme_idx < len(self.hedef_dizi):
                    hid = self.hedef_dizi[self.izleme_idx]
                    if self.parlama_ms == 0: self.parlama_ms = simdi_ms
                    if simdi_ms - self.parlama_ms < 800: self.__isik(self.daire_nesne_listesi_v[hid]["rect"])
                    elif simdi_ms - self.parlama_ms > 1100: self.izleme_idx += 1; self.parlama_ms = simdi_ms
                else: self.mevcut_durum_etiketi = "UYGULAMA"
            elif self.mevcut_durum_etiketi == "UYGULAMA":
                msg_u = self.font_arayuz_v.render("Şimdi Sıra Sende!", True, (52, 152, 219)); self.ekran.blit(msg_u, (self.pencere_W//2-msg_u.get_width()//2, 185))
            elif self.mevcut_durum_etiketi == "MESAJ":
                cl = (0, 100, 0) if any(x in self.feedback_msg for x in self.tebrik_sozleri) else (200, 0, 0)
                m = self.font_arayuz_v.render(self.feedback_msg, True, cl); self.ekran.blit(m, (self.pencere_W//2-m.get_width()//2, 175))
                if su_an_sn - s_z > 1.2:
                    if cl == (0, 100, 0):
                        if self.aktif_tur_no + 1 < 7: self.soru_hazirla(); self.mevcut_durum_etiketi = "BEKLEME"; s_z = su_an_sn
                        else: 
                            self.bitis_ani_toplam_sure = int(su_an_sn - o_bas)
                            self.mevcut_durum_etiketi = "BITIS"; self.bitir()
                    else: self.oyuncu_listesi, self.izleme_idx, self.parlama_ms, self.mevcut_durum_etiketi = [], 0, 0, "IZLEME"
            for ev_v in pygame.event.get():
                if ev_v.type == pygame.QUIT: self.oyun_aktif_durumu = False
                if ev_v.type == pygame.MOUSEBUTTONDOWN:
                    if self.mevcut_durum_etiketi == "BITIS" and self.ana_menuye_donus_butonu.collidepoint(ev_v.pos): self.oyun_aktif_durumu = False
                    elif self.mevcut_durum_etiketi == "UYGULAMA":
                        for idx, lamba_m in enumerate(self.daire_nesne_listesi_v):
                            if lamba_m["rect"].collidepoint(ev_v.pos):
                                t_id, t_son = idx, simdi_ms + 400; self.oyuncu_listesi.append(idx)
                                if self.oyuncu_listesi[-1] != self.hedef_dizi[len(self.oyuncu_listesi)-1]:
                                    if self.ses_yanlis_bildirim: self.ses_yanlis_bildirim.play()
                                    self.toplam_yanlis_sayaci += 1; self.feedback_msg, self.mevcut_durum_etiketi, s_z = "Tekrar Dene!", "MESAJ", su_an_sn
                                elif len(self.oyuncu_listesi) == len(self.hedef_dizi):
                                    if self.ses_dogru_bildirim: self.ses_dogru_bildirim.play()
                                    self.toplam_dogru_sayaci += 1; self.hesaplanan_basari_puani += 15
                                    self.__logs.append((time.time() - self.__soru_bas_z)*1000)
                                    self.feedback_msg, self.mevcut_durum_etiketi, s_z = random.choice(self.tebrik_sozleri), "MESAJ", su_an_sn
            if self.mevcut_durum_etiketi == "BITIS": self.__finish_ciz_v2()
            pygame.display.flip(); self.fps_motoru.tick(60)

    def __isik(self, r):
        s = pygame.Surface((r.width, r.height), pygame.SRCALPHA); pygame.draw.circle(s, (255, 255, 255, 180), (r.width//2, r.height//2), r.width//2); self.ekran.blit(s, r)

    def __finish_ciz_v2(self):
        if self.ses_oyun_sonu and not self.final_sesi_calindi_mi: self.ses_oyun_sonu.play(); self.final_sesi_calindi_mi = True
        ov = pygame.Surface((self.pencere_W, self.pencere_H), pygame.SRCALPHA); ov.fill((0, 0, 0, 220)); self.ekran.blit(ov, (0, 0))
        self.__ms_render_v("OYUN TAMAMLANDI!", self.font_dev_v, (255, 215, 0), 160)
        self.__ms_render_v(f"Doğru: {self.toplam_dogru_sayaci} | Yanlış: {self.toplam_yanlis_sayaci}", self.font_arayuz_v, (255, 255, 255), 270)
        self.__ms_render_v(f"Süre: {self.bitis_ani_toplam_sure} sn | Skor: {self.hesaplanan_basari_puani}", self.font_arayuz_v, (255, 255, 255), 320)
        pygame.draw.rect(self.ekran, (39, 174, 96), self.ana_menuye_donus_butonu, border_radius=15)
        bt = self.font_arayuz_v.render("ANA MENÜYE DÖN", True, (255, 255, 255)); self.ekran.blit(bt, (self.ana_menuye_donus_butonu.centerx-bt.get_width()//2, self.ana_menuye_donus_butonu.centery-bt.get_height()//2))

    def __ms_render_v(self, m, f, r, y):
        t = f.render(m, True, r); self.ekran.blit(t, (self.pencere_W // 2 - t.get_width() // 2, y))

    def bitir(self):
        ort = sum(self.__logs)/len(self.__logs) if self.__logs else 0
        self.vt.performans_kaydet(self.ogrenci["ad"], self.ogrenci["soyad"], self.sinif, "Hafıza Lambaları", self.toplam_dogru_sayaci, self.toplam_yanlis_sayaci, ort)

# =============================================================================================
# 5. BÖLÜM: OYUN 3 - DİZİ TAMAMLAMA (FIXED)
# =============================================================================================

class DiziTamamlama(Oyun):
    def __init__(self, ekran, vt, sinif, ogrenci):
        super().__init__(ekran, vt, sinif, ogrenci)
        self.font_arayuz_v = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_baslik_v = pygame.font.SysFont("Arial", 65, bold=True)
        self.ap2_img_yuzeyi_v = None
        y = os.path.join("gorseller", "arka_plan_2.png")
        if os.path.exists(y): self.ap2_img_yuzeyi_v = pygame.transform.scale(pygame.image.load(y).convert(), (self.pencere_W, self.pencere_H))
        self.sekil_bankasi = {}
        names = ["yildiz.png", "yesil_yildiz.png", "mavi_ucgen.png", "kirmizi_kare.png", "yesil_kare.png"]
        for n in names:
            p = os.path.join("gorseller", n)
            if os.path.exists(p): self.sekil_bankasi[n] = pygame.transform.scale(pygame.image.load(p).convert_alpha(), (95, 95))
        self.tur_idx, self.gs_rakami, self.inceleme_sn = 0, 3, 8
        self.fb_text, self.intro_alpha, self.intro_y, self.__logs_sure = "", 0, self.pencere_H // 2, []
        self.tebrik_listesi = ["Harika!", "Süpersin!", "Mükemmel!", "Böyle Devam!", "Çok Başarılı!"]
        self.secenek_key_listesi = []
        self.soru_hazirla()

    def soru_hazirla(self):
        if self.tur_idx > 0: self.mevcut_durum_etiketi = "HAZIR"
        keys = list(self.sekil_bankasi.keys())
        s1, s2 = random.sample(keys, 2)
        if self.tur_idx == 0: self.dizi_verisi = [s1, s2, s1, s2]
        else: self.dizi_verisi = [random.choice(keys) for _ in range(min(5, 4 + self.tur_idx))]
        self.eksik_idx = random.randint(0, len(self.dizi_verisi)-1); self.ans_key = self.dizi_verisi[self.eksik_idx]
        self.secenek_key_listesi = [self.ans_key] + random.sample([x for x in keys if x != self.ans_key], 3); random.shuffle(self.secenek_key_listesi)
        self.__soru_bas_z = time.time()

    def calistir(self):
        s_z, o_bas, study_z = 0, 0, 0
        while self.oyun_aktif_durumu:
            if self.ap2_img_yuzeyi_v: self.ekran.blit(self.ap2_img_yuzeyi_v, (0, 0))
            else: self.ekran.fill((240, 240, 235))
            su_an = time.time()
            g_sn = int(su_an - o_bas) if o_bas > 0 else 0
            self.ekran.blit(self.font_hud_mini.render(f"Skor: {self.hesaplanan_basari_puani}", True, (30,30,30)), (15, 15))
            self.ekran.blit(self.font_hud_mini.render(f"Süre: {g_sn}s", True, (30,30,30)), (15, 40))
            self.ekran.blit(self.font_hud_mini.render(f"Tur: {self.tur_idx+1}/7", True, (30,30,30)), (15, 65))
            if self.intro_alpha < 255: self.intro_alpha += 5
            if self.mevcut_durum_etiketi == "INTRO_FADE" and self.intro_alpha >= 255: self.mevcut_durum_etiketi = "INTRO_MOVE"
            elif self.mevcut_durum_etiketi == "INTRO_MOVE":
                if self.intro_y > 85: self.intro_y -= 4
                else: self.mevcut_durum_etiketi = "SAYAC"; s_z = su_an
            t_i = self.font_arayuz_v.render("Örüntüyü Tamamla!", True, (30,30,30)); t_i.set_alpha(self.intro_alpha); self.ekran.blit(t_i, (self.pencere_W//2-t_i.get_width()//2, self.intro_y))
            if self.mevcut_durum_etiketi == "SAYAC":
                self.__ms_render_et("HAZIR!", self.font_arayuz_v, (52, 152, 219), 250)
                txt = self.font_baslik_v.render(str(self.gs_rakami), True, (230, 126, 34)); self.ekran.blit(txt, (self.pencere_W//2-txt.get_width()//2, self.pencere_H//2))
                if su_an - s_z >= 1: self.gs_rakami -= 1; s_z = su_an
                if self.gs_rakami == 0: self.mevcut_durum_etiketi = "HAZIR"; s_z = su_an; o_bas = su_an; self.ses_talimat_dizi.play() if self.ses_talimat_dizi else None
            elif self.mevcut_durum_etiketi == "HAZIR":
                self.__ms_render_et("HAZIR!", self.font_baslik_v, (52, 152, 219), self.pencere_H//2)
                if su_an - s_z > 1.2: self.mevcut_durum_etiketi = "INCELEME"; study_z = su_an
            elif self.mevcut_durum_etiketi == "INCELEME":
                rem = int(self.inceleme_sn - (su_an - study_z))
                self.__ms_render_et(f"İncele! {max(0, rem)}s", self.font_arayuz_v, (30,30,30), 160); self.__dizi_ciz_motoru(maskeleme=False)
                if rem <= 0: self.mevcut_durum_etiketi = "SORU"; self.soru_ani = su_an
            elif self.mevcut_durum_etiketi == "SORU":
                self.__ms_render_et("Eksik olan şekli seçin!", self.font_arayuz_v, (30,30,30), 160); self.__dizi_ciz_motoru(maskeleme=True)
            elif self.mevcut_durum_etiketi == "MESAJ":
                cl = (0, 100, 0) if any(x in self.fb_text for x in self.tebrik_listesi) else (231, 76, 60); self.__ms_render_et(self.fb_text, self.font_arayuz_v, cl, 160)
                if su_an - s_z > 1.5:
                    if cl == (0, 100, 0):
                        self.tur_idx += 1
                        if self.tur_idx < 7: self.soru_hazirla(); self.mevcut_durum_etiketi = "INCELEME"; study_z = su_an
                        else: 
                            self.bitis_ani_toplam_sure = int(su_an - o_bas)
                            self.mevcut_durum_etiketi = "BITIS"; self.bitir()
                    else: self.mevcut_durum_etiketi = "SORU"
            elif self.mevcut_durum_etiketi == "BITIS": self.__final_render_v()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.oyun_aktif_durumu = False
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.mevcut_durum_etiketi == "BITIS" and self.ana_menuye_donus_butonu.collidepoint(ev.pos): self.oyun_aktif_durumu = False
                    elif self.mevcut_durum_etiketi == "SORU":
                        bx = self.pencere_W//2 - (4*145)//2
                        for i in range(4):
                            r = pygame.Rect(bx + i*145, 480, 115, 115)
                            if r.collidepoint(ev.pos):
                                if self.secenek_key_listesi[i] == self.ans_key:
                                    self.toplam_dogru_sayaci += 1; self.fb_text = random.choice(self.tebrik_listesi); self.hesaplanan_basari_puani += 15
                                    if self.ses_dogru_bildirim: self.ses_dogru_bildirim.play()
                                    self.__logs_sure.append((su_an-self.soru_ani)*1000)
                                else:
                                    self.toplam_yanlis_sayaci += 1; self.fb_text = "Tekrar Dene!"; self.hesaplanan_basari_puani = max(0, self.hesaplanan_basari_puani-10)
                                    if self.ses_yanlis_bildirim: self.ses_yanlis_bildirim.play()
                                self.mevcut_durum_etiketi = "MESAJ"; s_z = su_an
            pygame.display.flip(); self.fps_motoru.tick(60)

    def __dizi_ciz_motoru(self, maskeleme=False):
        bx = self.pencere_W//2 - (len(self.dizi_verisi)*105)//2
        for i, k in enumerate(self.dizi_verisi):
            p = (bx + i*105, 280)
            if maskeleme and i == self.eksik_idx:
                pygame.draw.rect(self.ekran, (200, 200, 200), (p[0], p[1], 95, 95), border_radius=10)
                q_m = self.font_baslik_v.render("?", True, (30,30,30)); self.ekran.blit(q_m, (p[0]+47-q_m.get_width()//2, p[1]+5))
            else: self.ekran.blit(self.sekil_bankasi[k], p)
        if self.mevcut_durum_etiketi == "SORU":
            bx_s = self.pencere_W//2 - (4*145)//2
            for i, key in enumerate(self.secenek_key_listesi):
                rv = pygame.Rect(bx_s + i*145, 480, 115, 115); pygame.draw.rect(self.ekran, (255,255,255), rv, border_radius=15); pygame.draw.rect(self.ekran, (52,152,219), rv, 3, border_radius=15); self.ekran.blit(self.sekil_bankasi[key], (rv.x+10, rv.y+10))

    def bitir(self):
        ort = sum(self.__logs_sure)/len(self.__logs_sure) if self.__logs_sure else 0
        self.vt.performans_kaydet(self.ogrenci["ad"], self.ogrenci["soyad"], self.sinif, "Dizi Tamamlama", self.toplam_dogru_sayaci, self.toplam_yanlis_sayaci, ort)

    def __final_render_v(self):
        if self.ses_oyun_sonu and not self.final_sesi_calindi_mi: self.ses_oyun_sonu.play(); self.final_sesi_calindi_mi = True
        ov = pygame.Surface((self.pencere_W, self.pencere_H), pygame.SRCALPHA); ov.fill((0, 0, 0, 150)); self.ekran.blit(ov, (0, 0))
        self.__ms_render_et("DİZİ TAMAMLANDI!", self.font_baslik_v, (255, 215, 0), 160)
        self.__ms_render_et(f"Doğru: {self.toplam_dogru_sayaci} | Yanlış: {self.toplam_yanlis_sayaci}", self.font_arayuz_v, (255, 255, 255), 270)
        self.__ms_render_et(f"Süre: {self.bitis_ani_toplam_sure} sn | Skor: {self.hesaplanan_basari_puani}", self.font_arayuz_v, (255, 255, 255), 320)
        pygame.draw.rect(self.ekran, (230, 126, 34), self.ana_menuye_donus_butonu, border_radius=15)
        bt = self.font_arayuz_v.render("ANA MENÜYE DÖN", True, (255, 255, 255)); self.ekran.blit(bt, (self.ana_menuye_donus_butonu.centerx-bt.get_width()//2, self.ana_menuye_donus_butonu.centery-bt.get_height()//2))

    def __ms_render_et(self, m, f, r, y):
        t = f.render(m, True, r); self.ekran.blit(t, (self.pencere_W // 2 - t.get_width() // 2, y))

# =============================================================================================
# 6. BÖLÜM: ANALİZ MOTORU (FIXED)
# =============================================================================================

class OgretmenAnalizModulu:
    def __init__(self, veritabani_yolu="dusadim_final_V100.db"):
        self.__db_path = veritabani_yolu

    def rapor_uret_v(self, ad_v, soyad_v):
        try:
            bag = sqlite3.connect(self.__db_path)
            # id yerine id (veya sütun adınız neyse) - id genelde standarttır
            df = pd.read_sql_query(f"SELECT * FROM performans WHERE ad='{ad_v}' AND soyad='{soyad_v}'", bag); bag.close()
            if df.empty: return "İlgili öğrenci için sistemde veri bulunamadı."
            fig, (ax_table, ax_pie) = plt.subplots(2, 1, figsize=(11, 10))
            fig.patch.set_facecolor('#fdfdf2')
            ax_table.axis('off')
            ax_table.set_title(f"Bilişsel Gelişim Raporu: {ad_v} {soyad_v}", fontsize=14, fontweight='bold', pad=20)
            kolonlar = ["ID", "Oyun Modülü", "Doğru", "Hata", "Hız (ms)"]
            tablo_verisi = df[['oyun_adi', 'dogru', 'yanlis', 'tepki_suresi']].tail(10).reset_index().values
            tablo = ax_table.table(cellText=tablo_verisi, colLabels=kolonlar, loc='center', cellLoc='center', colColours=["#3498db"]*5)
            tablo.auto_set_font_size(False); tablo.set_fontsize(10); tablo.scale(1, 1.8)
            labels = ['Başarılı Tepkiler', 'Hatalı Tepkiler']
            sizes = [df['dogru'].sum(), df['yanlis'].sum()]
            colors = ['#27ae60', '#e74c3c']
            ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=(0.05, 0))
            ax_pie.set_title('Genel Dikkat ve Başarı Oranı (%)', fontsize=12, fontweight='bold')
            plt.tight_layout(); plt.show()
        except Exception as e: return f"Analiz motoru hatası: {e}"