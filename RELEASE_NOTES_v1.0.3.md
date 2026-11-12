# Sunucu Kopyalama v1.0.3

## Düzeltmeler

- Kanal oluşturma isteği toplu `permission_overwrites` nedeniyle Discord `50013` döndürürse güvenli geri dönüş uygulanır.
- Kanal önce @everyone için `VIEW_CHANNEL` reddiyle gizli oluşturulur; ardından rol izinleri tek tek uygulanır.
- Bir rol izni reddedilirse kopyalama durmaz; diğer kanallar oluşturulmaya devam eder.
- Bir veya daha fazla izin uygulanamazsa güvenlik amacıyla geçici @everyone gizlilik engeli kaldırılmaz; kullanıcıya işlem günlüğünde bildirilir.
- Kanal oluşturma veya sıralama aşamalarındaki hatalar kanal adı/türüyle daha açık raporlanır.
- Önizleme sayaçları artık tür 20 nedeniyle atlanacak kanalları kopyalanacak kanal sayısına katmaz.

## Doğrulama

- İki yeni kanal izni regresyon testi eklendi.
- Windows release iş akışı tüm otomatik testleri, EXE sürüm bilgilerini ve paketlenmiş GUI öz denetimini çalıştırır.
- EXE yalnızca bu kontroller başarılı olduğunda GitHub Release'e yüklenir.
