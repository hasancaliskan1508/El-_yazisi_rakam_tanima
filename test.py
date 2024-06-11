# -*- coding: latin-1 -*-

import cv2
import numpy as np
import tkinter
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import os

class Boya(object):
    
    VARSAYILAN_KALEM_BOYUTU = 23.0
    VARSAYILAN_RENK = 'white'
    messagebox.showinfo("Rehber", "Merhaba! Lutfen 0 ile 9 arasinda tek basamakli bir rakam cizin.\n Eger rakami dogru yazmadinizsa, (Temizle) dugmesine basarak tekrar deneyebilirsiniz.\n Yazmayi bitirdikten sonra, (Yazilan rakamin taninmasi) dugmesine tiklayin.")
    
    def __init__(self):
        
        self.kok = Tk()
        self.kok.title("El Yazisi Rakam Tanima")
        
        self.kalem_dugmesi = Button(self.kok, text='Kalem', command=self.kalemi_kullan)
        self.kalem_dugmesi.grid(row=1, column=0)

        self.temizle_dugmesi = Button(self.kok, text='Temizle', command=self.temizle)
        self.temizle_dugmesi.grid(row=1, column=1)
        
        self.tanima_dugmesi = Button(self.kok, text='Yazilan rakamin taninmasi', command=self.Tanima)
        self.tanima_dugmesi.grid(row=1, column=2)
        
        self.resim_yukle_dugmesi = Button(self.kok, text='Resim Yukle ve Tani', command=self.resim_yukle_ve_tani)
        self.resim_yukle_dugmesi.grid(row=1, column=3)
        
        self.boyut_secme_dugmesi = Scale(self.kok, from_=23, to=23)
        self.boyut_secme_dugmesi.grid(row=2, column=1)

        self.c = Canvas(self.kok, bg='black', width=400, height=400)
        self.c.grid(row=2, columnspan=5)

        self.kurulum()
        
        self.hucreler2 = np.loadtxt("egitim_data.csv", delimiter=",")
        self.hucreler2 = np.array(self.hucreler2, dtype=np.float32)
        
        self.hedefler = np.loadtxt("egitim_hedefleri.csv", delimiter=",")
        self.hedefler = np.array(self.hedefler, dtype=np.float32)
        
        self.kok.mainloop()

    def kurulum(self):
        self.eski_x = None
        self.eski_y = None
        self.cizgi_genisligi = self.boyut_secme_dugmesi.get()
        self.renk = self.VARSAYILAN_RENK
        self.silgi_modu = False
        self.aktif_dugme = self.kalem_dugmesi
        self.c.bind('<B1-Motion>', self.boyama)
        self.c.bind('<ButtonRelease-1>', self.sifirla)

    def kalemi_kullan(self):
        self.aktif_dugme = self.kalem_dugmesi
        
    def temizle(self):
        self.c.delete("all")
        self.kurulum()
    
    def resim_isleme_ve_tanima(self, resim):
        resim = resim.resize((20, 20), Image.BICUBIC)
        test_rakamlar = np.array(resim.convert('L'))
        test_rakamlar[0:1,:] = 0
        test_rakamlar[19:,:] = 0
        test_rakamlar[:,0:1] = 0
        test_rakamlar[:,19:] = 0
        
        test_hucreleri_duz = test_rakamlar.flatten()
        test_hucreleri_duz = np.array(test_hucreleri_duz, dtype=np.float32)
        test_hucreleri_duz = test_hucreleri_duz.reshape(1, -1)
        
        knn = cv2.ml.KNearest_create()
        knn.train(self.hucreler2, cv2.ml.ROW_SAMPLE, self.hedefler)
        
        ret, sonuc, komsular, mesafe = knn.findNearest(test_hucreleri_duz, k=5)
        return int(sonuc[0][0]), test_hucreleri_duz

    def resim_yukle_ve_tani(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
        if dosya_yolu:
            try:
                resim = Image.open(dosya_yolu)
                taninan_rakam, test_hucreleri_duz = self.resim_isleme_ve_tanima(resim)
                self.sonuc_tanimla(taninan_rakam, test_hucreleri_duz)
            except Exception as e:
                messagebox.showerror("Hata", f"Resim iþlenirken bir hata oluþtu: {e}")

    def Tanima(self):
        try:
            self.kok.update()
            x = self.kok.winfo_rootx() + self.c.winfo_x()
            y = self.kok.winfo_rooty() + self.c.winfo_y()
            x1 = x + self.c.winfo_width()
            y1 = y + self.c.winfo_height()

            resim = ImageGrab.grab(bbox=(x, y, x1, y1))

            taninan_rakam, test_hucreleri_duz = self.resim_isleme_ve_tanima(resim)
            
            self.sonuc_tanimla(taninan_rakam, test_hucreleri_duz)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Goruntu verileri islenirken bir hata olustu: {e}")

    def sonuc_tanimla(self, taninan_rakam, test_hucreleri_duz):
        onay = messagebox.askyesnocancel("Sonuc", f"Tespit edilen rakam: {taninan_rakam}\n Bu rakami dogru tanidim mi?")
        if onay is None:
            return  # Kullanýcý iptal etti
        
        if onay:
            self.hucreler2 = np.vstack([self.hucreler2, test_hucreleri_duz])
            np.savetxt("egitim_data.csv", self.hucreler2, delimiter=",", fmt="%f")
            
            sonuc = np.array([taninan_rakam], dtype=np.float32)
            self.hedefler = np.hstack([self.hedefler, sonuc])
            np.savetxt("egitim_hedefleri.csv", self.hedefler, delimiter=",", fmt="%f")
            
            messagebox.showinfo("Iyi haber!", "Harika! :) \n Bu rakami gelecekteki el yazisi tanima icin kaydettim.")
            self.temizle()
            
        else:
            dogru_rakam_tekrar = tkinter.Toplevel(self.kok)
            dogru_rakam_tekrar.title('Dogru rakam neydi? :(')
            dogru_rakam_tekrar.geometry('470x200')
            
            lbl_dogru_rakam = tkinter.Label(dogru_rakam_tekrar, text='Hatasizlik icin ozur dilerim! \n Hangi rakami yazdiniz? \n Lutfen yazin ve TAMAM\'a tiklayin. \n')
            lbl_dogru_rakam.pack()
            
            kullanici_rakam = tkinter.Entry(dogru_rakam_tekrar)
            kullanici_rakam.pack()
            
            def tamam():
                rakam = kullanici_rakam.get()
                
                if not rakam.isdigit() or int(rakam) not in range(10):
                    lbl_dogru_rakam.configure(text="\n Lutfen 0-9 arasinda bir rakam yazin! \n", fg="red")
                    return
                
                self.hucreler2 = np.vstack([self.hucreler2, test_hucreleri_duz])
                np.savetxt("egitim_data.csv", self.hucreler2, delimiter=",", fmt="%f")
                
                rakam = np.array([int(rakam)], dtype=np.float32)
                self.hedefler = np.hstack([self.hedefler, rakam])
                np.savetxt("egitim_hedefleri.csv", self.hedefler, delimiter=",", fmt="%f")
                
                messagebox.showinfo("Tesekkürler!", "Tesekkürler! \n Bu rakami gelecekteki el yazisi tanima icin kaydettim.")
                dogru_rakam_tekrar.destroy()
                self.temizle()
                 
            btn_tamam = tkinter.Button(dogru_rakam_tekrar, text='TAMAM', command=tamam)
            btn_tamam.pack()

    def aktif_dugmeyi_aktifle(self, bir_dugme, silgi_modu=False):
        self.aktif_dugme.config(relief=RAISED)
        bir_dugme.config(relief=SUNKEN)
        self.aktif_dugme = bir_dugme
        self.silgi_modu = silgi_modu

    def boyama(self, event):
        self.cizgi_genisligi = self.boyut_secme_dugmesi.get()
        boya_rengi = 'black' if self.silgi_modu else self.renk
        if self.eski_x and self.eski_y:
            self.c.create_line(self.eski_x, self.eski_y, event.x, event.y,
                               width=self.cizgi_genisligi, fill=boya_rengi,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.eski_x = event.x
        self.eski_y = event.y

    def sifirla(self, event):
        self.eski_x, self.eski_y = None, None


if __name__ == '__main__':
    Boya()