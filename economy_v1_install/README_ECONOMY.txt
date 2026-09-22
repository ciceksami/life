AVATAR LIFE #2017 — ECONOMY v1
================================

YAPILANLAR

1. PUBLIC SINIRSIZ GOLD KAPATILDI
   Eski billing.py, const.FREE_GOLD açık olduğunda b.chkprchs paketinden gelen
   pack miktarını doğrudan oyuncunun Gold bakiyesine ekliyordu.

   Yeni sürümde normal/public hesaplar bu kaynaktan Gold ALAMAZ.

2. ADMIN / TEST HESAPLARI AYRI TUTULDU
   role >= 5 olan hesaplar test/staff hesabı kabul edilir.
   const.FREE_GOLD = True ise yalnızca bu hesaplar eski test Gold özelliğini
   kullanabilir.

   Sunucundaki admin rol eşiği farklıysa billing.py içindeki:
       FREE_GOLD_MIN_ROLE = 5
   değerini değiştir.

3. GOLD -> SILVER DEĞİŞİMİ GÜVENLİ HALE GETİRİLDİ
   - Negatif miktar engellendi.
   - 0 miktarı engellendi.
   - Geçersiz paketler engellendi.
   - Yetersiz Gold kontrolü korunuyor.
   - Redis güncellemesi pipeline ile birlikte yapılıyor.
   - Oran: 1 Gold = 100 Silver.

4. EKONOMİ AYAR DOSYASI EKLENDİ
   economy.py gelecek görev sisteminin ödül ayarlarını merkezi tutar.

   Hazırlanan kategoriler:
   - Başlangıç görevleri
   - Günlük görevler
   - Haftalık görevler
   - Tek ödül için güvenlik limitleri

5. ÖNEMLİ
   Bu paket henüz görev sistemini oyuncuya açmaz.
   Yalnızca sınırsız public Gold kaynağını kapatır ve görev ekonomisinin
   temel ayarlarını hazırlar.

KURULUM

Mevcut dosyayı yedekle:
    cd ~/avatariapvp
    cp modules/billing.py modules/billing.py.before_economy

billing.py dosyasını:
    ~/avatariapvp/modules/billing.py
konumuna koy.

economy.py dosyasını:
    ~/avatariapvp/modules/economy.py
konumuna koy.

Kontrol:
    cd ~/avatariapvp
    python3 -m py_compile modules/billing.py modules/economy.py

Ardından oyun sunucunu normal yöntemle yeniden başlat.

PUBLIC TEST
Normal oyuncuyla Gold satın alma/free-gold işlemini dene.
Bakiye artmamalı.

ADMIN TEST
role >= 5 hesap + const.FREE_GOLD=True durumunda test özelliği çalışmaya devam eder.
