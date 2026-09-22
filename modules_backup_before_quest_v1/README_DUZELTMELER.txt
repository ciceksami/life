AVATAR LIFE #2017 - MODÜL DÜZELTME PAKETİ
============================================

Bu paket, bu konuşmada yüklediğin Python modüllerinin tamamını içerir.
Amaç: istemci protokolünü tahmin ederek yeni komutlar uydurmak yerine,
tespit edilebilen gerçek hata ve güvenlik/kararlılık sorunlarını düzeltmek.

YAPILAN ANA DÜZELTMELER
- support.py: Discord/support icon URL doğrudan PNG adresine çevrildi.
- relations.py: negatif ilişki ilerlemesini engelleyen min_value karşılaştırma hatası düzeltildi; eksik action/link verisine koruma eklendi.
- component.py: ban Redis anahtarı düzeltildi; !ban/!unban/!reset/!mute/!ssm hatalı parametrelerde sunucuyu düşürmeyecek hale getirildi; mute süre metni düzeltildi.
- house.py: h.ioinfo paketinin diğer send çağrılarıyla uyumsuz gönderim biçimi düzeltildi.
- location.py: None kontrolü temizlendi ve rpt değeri için gereksiz ikinci Redis sorgusu kaldırıldı.
- user_rating.py: boş uids/crt Redis değerlerinde int(None) hatası engellendi.
- shop.py: sıfır/negatif/geçersiz adet engellendi; eksik gold/silver alanları güvenli işlendi.
- inventory.py: negatif/sıfır satış adedi engellenerek ekonomi suistimali kapatıldı.
- billing.py: mevcut amnt alanı kullanılıyorsa negatif/sıfır miktar koruması eklendi (protokol değiştirilmedi).

KORUNAN DOSYALAR
----------------
Diğer modüller de ZIP içindedir. Açık bir hata tespit edilmediyse davranışları
değiştirilmedi. Özellikle mail.py, location_game.py, competition.py,
social_request.py ve statistics.py gibi boş/iskelet cevaplar veren modüllere
istemcinin beklediği paket yapısı doğrulanmadan rastgele özellik eklenmedi.
Bu sayede mevcut SWF ile uyumluluğu bozma riski azaltıldı.

KURULUM
-------
1) Önce mevcut modules klasörünü yedekle:
   cd ~/avatariapvp
   cp -a modules modules_backup_before_fix

2) ZIP içindeki .py dosyalarını ~/avatariapvp/modules/ içine yükle.

3) Sözdizimi kontrolü:
   cd ~/avatariapvp
   python3 -m compileall -q modules

4) Oyun sunucusunu kullandığın mevcut yöntemle yeniden başlat.

NOT
---
Paket içindeki tüm Python dosyaları AST parse + compileall kontrolünden geçti.
Bu, sözdizimi hatası olmadığını doğrular; canlı sunucu/SWF entegrasyonunun
tam testi sunucu çalışırken yapılmalıdır.
