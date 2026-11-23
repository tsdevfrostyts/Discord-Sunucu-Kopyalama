# Sunucu Kopyalama v1.0.4

## Kritik düzeltme: Yönetici rolü korunuyor

- Hedef sunucuda oturum açmış hesaba atanmış tüm roller artık kopyalama öncesinde belirlenir ve silme listesinden çıkarılır.
- Özellikle sunucu sahibi olmayan ve Yönetici (Administrator) yetkisini bir rolden alan hesaplarda, bu rol kopyalama sürerken silinmez.
- Böylece hedef kanallar temizlendikten ve kopyalanan roller oluşturulduktan sonra kanal/kategori oluşturma aşamasında hesabın `MANAGE_CHANNELS` veya `MANAGE_ROLES` yetkisini kaybetmesi engellenir.
- Önizlemede korunacak roller uyarı olarak gösterilir; işlem günlüğünde her rol `KORUNDU` olarak işaretlenir.
- Önizleme ile kopyalama arasında hesaba atanmış roller değişirse hiçbir silme işlemi yapılmadan işlem durdurulur.
- Son doğrulama, hedefte korunması gereken bu rolleri de beklenen yapı içinde sayar.

## Önceki düzeltmeler

- v1.0.3'te eklenen güvenli kanal izni geri dönüşü korunur. Discord toplu izinleri reddederse kanal @everyone için gizli oluşturulup rol izinleri ayrı uygulanır.
- Başarısız rol izinleri diğer kanalların oluşturulmasını durdurmaz ve güvenlik için gizlilik engeli korunur.

## Doğrulama

- Admin rolünün kopyalama sırasında silinmesi halinde MANAGE_ROLES kalıp MANAGE_CHANNELS kaybolduğu senaryo izin denetimli bir sahte Discord API ile test edilir.
- Sunucu sahibi olmayan, yönetici rolü atanmış hesabın kategori ve metin/ses kanalı oluşturması regresyon testleriyle doğrulanır.
- Windows release iş akışı tüm çekirdek/arayüz testlerini, EXE sürüm bilgilerini ve paketlenmiş GUI öz denetimini çalıştırır.
- EXE yalnızca bu kontroller başarılı olduğunda GitHub Release'e yüklenir.
