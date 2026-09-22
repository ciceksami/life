# Avatar Life Sami Can Çavuş / SON SÜRÜM 2026 TR 
Avatar Life, kendi avataria sunucunuzu kurmanızı sağlar.

# Güncellemeler 22.09.2026
- Chat Dekor Özelliği eklendi.
- Hatalar giderildi.
- Meslek Kıyafet Hataları ( Baston Foto Makinesi vs. Hatası ) Fixlendi.

# VDS - VPS Üzerine Kurulum
- apt-get update
- apt-get upgrade
- apt install python3-pip
- apt-get install redis-server
- systemctl enable redis-server.service
- git clone https://github.com/ciceksami/life
- "avatariapvp-tr" dosyasının içindeki "web.ini" yi kendi sunucunuza göre güncelleyin.
- pip3 install --user -r requirements.txt  oyun gereksimilerini indirin.
- Uzak Masaüstü Bağlantısından makinanızda terminal açıp "cd avatariapvp-tr" yazıp python3 web.py yazın.
- Yeni bir terminal açıp yine cd avatariapvp-tr yazıp python3 server yazıp sunucuyu başlatın.

# XRDP Kurulumu (Uzak Masaüstü Erişimi Sağlar)
- sudo apt update
- sudo apt install xfce4 xfce4-goodies xorg dbus-x11 x11-xserver-utils
- sudo apt install xrdp 
- sudo systemctl status xrdp
- xrdp.service - xrdp daemon
   Loaded: loaded (/lib/systemd/system/xrdp.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2019-07-28 22:40:53 UTC; 4min 21s ago
     Docs: man:xrdp(8)
           man:xrdp.ini(5)
- sudo adduser xrdp ssl-cert  
- sudo systemctl restart xrdp

# Panele Erişim
- Putty'i açın.
- Giriş yapın.
- cd "oyun dosyalarının bulunduğu klasör" (örn: cd ava)
- redis-server yazın.
- redis-cli yazın.
- Aşağıdaki komutları yazabilirsiniz.

# Oyunda Yetki Verme
- Gizli Adminlik verme (R) = set uid:ID:role 5
- Adminlik verme (A) = set uid:ID:role 4
- Baş Moderatörlük verme (M) = set uid:ID:role 3
- Moderatörlük verme (M) = set uid:ID:role 2
- Uyarı Yetkisi verme (M) = set uid:ID:role 1
- Normal Oyuncu (P) = set uid:ID:role 0

# İmaj - Konfor - Seviye - İsim Değiştirme Komutları
- İmaj Verme: set uid:ID:crt {miktar}
- Konfor verme: set uid:ID:hrt {miktar}
- Level verme (exp): set uid:ID:exp {exp miktar}
- İsim değiştirme: lset uid:ID:appearance 0 "Koyulacak İsim"

# Oyun İçi Ayarlar
- Oyuncu banlama: !ban ID 
- Oyuncu susturma (muteleme): !mute ID süre (dk)
- Ban Kaldırma: !unban ID
- Oyuncu Hesabı Sıfırlama: !reset ID
- Oyuncu mute kaldırma: !mute ID 0 (dk)
- Oyuncu Hesap Sıfırlama: !reset ID
 
 # Üyeleri Sıfırlama
 - Putty açın.
 - cd {oyun dosyalarının olduğu klasörün adı} (örn: cd ava)
 - redis-server yazın.
 - redis-cli FLUSHDB yazın.



