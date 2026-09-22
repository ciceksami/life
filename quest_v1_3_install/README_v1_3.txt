Avatar Life Quest System v1.3 SAFE PURCHASE PATCH

Kaynak: kullanıcının current_working_shop_files.zip içindeki çalışan dosyaları.

Güvenli değişiklik:
- avatar.py: 3 satın alma akışında mevcut başarı client.send cevabından SONRA Quest purchase +1.
- furniture.py: mevcut ntf.inv/ntf.res cevaplarından SONRA Quest purchase +1.
- Tüm yeni Quest çağrıları try/except içinde. Quest hatası mağaza akışına geri yayılmaz.
- buy_clothes_suit yalnızca to_buy doluysa +1 sayar.
- shop.py mevcut çalışan haliyle korunmuştur.

Önerilen kurulum: sadece avatar.py ve furniture.py dosyalarını modules/ içine kopyalayın.
