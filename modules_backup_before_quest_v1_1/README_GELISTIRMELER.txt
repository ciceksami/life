AVATAR LIFE #2017 — GELİŞTİRİLMİŞ SİSTEMLER
=============================================

Bu paket önceki hata düzeltmelerinin tamamını içerir ve üstüne şu geliştirmeleri ekler:

• user_rating.py
  - Aktivite TOP 10 artık boş dönmüyor.
  - Mevcut rpt puanını kullanarak en aktif 10 oyuncuyu döndürüyor.
  - Eksik Redis değerleri güvenli.

• statistics.py
  - stat.urlnv artık boşa gitmiyor.
  - Oyuncunun son 100 URL yönlendirmesini Redis'te uid:<id>:urlnav altında kaydeder.

• mail.py
  - Gelen kutusu Redis'ten okunabilir hale getirildi.
  - Sunucu tarafında add_system_mail() yardımcı fonksiyonu eklendi.
  - SWF'de doğrulanmamış gönder/sil komutları uydurulmadı.

• social_request.py
  - Redis tabanlı sosyal istek saklama/okuma altyapısı eklendi.
  - add_request() yardımcı fonksiyonu eklendi.
  - Mevcut gtit/gtrq komutları korunuyor.

• passport.py
  - Achievement/trophy değerleri artık Redis'te varsa gerçek değerleri döndürüyor.
  - Veri yoksa eski davranışla 0/default değerler kullanılıyor.

• support.py
  - Discord ikonunun doğrudan PNG URL'si ayarlandı.
  - Avatar Life #2017 Discord bağlantısı korunuyor.

• reward_service.py (YENİ)
  - 7 günlük günlük ödül altyapısı.
  - Günlük ödül aynı gün ikinci kez alınamaz.
  - Seri gün takibi.
  - YENIDEN2017 ve AVATARLIFE örnek promosyon kodları.
  - Promosyon kodu oyuncu başına tek kullanım.
  - Altın/gümüş/enerji Redis bakiyelerine güvenli ekleme.
  - SWF'nin promosyon/günlük ödül paket adı henüz doğrulanmadığı için istemciye
    sahte komut bağlanmadı. Bu dosya server/web/admin tarafından çağrılmaya hazırdır.

ÖNCEKİ DÜZELTMELER DE PAKETTE:
• relations.py negatif progress karşılaştırması düzeltildi.
• component.py ban Redis anahtarı ve komut parametre kontrolleri düzeltildi.
• house.py send paket biçimi düzeltildi.
• inventory.py / shop.py negatif veya sıfır adet koruması.
• location.py gereksiz Redis sorgusu temizlendi.
• user_rating.py None/int korumaları.
• billing.py negatif/sıfır miktar koruması.

KURULUM
-------
cd ~/avatariapvp
cp -a modules modules_backup_before_features

ZIP içindeki .py dosyalarını ~/avatariapvp/modules/ klasörüne yükle.

Kontrol:
python3 -m compileall -q modules

Ardından oyun sunucusunu normal kullandığın yöntemle yeniden başlat.

ÖNEMLİ:
Tüm Python dosyaları AST + compileall kontrolünden başarıyla geçti.
İstemcinin bilinmeyen paket isimlerini tahmin etmedim; böylece mevcut SWF'yi
bozacak sahte protokol eklenmedi.
