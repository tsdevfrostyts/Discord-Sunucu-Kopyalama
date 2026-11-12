# Sunucu Kopyalama v1.0.6

## İndirilebilir dosyalar

- `Sunucu-Kopyalama_v1.0.6_Kullanıcı.exe` — mevcut kullanıcı-token sürümü.
- `Sunucu-Kopyalama_v1.0.6_Bot.exe` — Discord bot token’iyle çalışan sürüm.

## Değişiklikler

- Uygulama dosya adına göre mod seçer. `_Kullanıcı.exe` ham kullanıcı token’ini; `_Bot.exe` `Authorization: Bot <token>` biçimini kullanır. Bot sürümünde token alanına `Bot ` ön eki yazmak isteğe bağlıdır.
- Bot sürümü bot hesabı doğrulamasını, kaynak/hedef sunucu erişimini ve hedefte Administrator yetkisini kontrol eder.
- Botun ve kullanıcı sürümündeki işlemi yapan hesabın atanmış rolleri silinmez. Rol hiyerarşisi yönetilmesi gereken rollerin üstünde değilse işlem herhangi bir silme yapmadan durur.
- Botun kaynak sunucuda kopyalanacak tüm kanallarda `View Channel` erişimi olmalıdır. Discord’un kanal listeleme API’si 16 Kasım 2026 itibarıyla botun göremediği kanalları sonuçlardan çıkaracak şekilde güncelleniyor.
- Bot sürümünde hedef sunucuda Administrator yetkisi ve silinecek rollerin üzerinde bir bot rolü gerekir. Hedefte botun atanmış rolleri korunur.
- v1.0.5 rate-limit düzeltmeleri korunur: rol/kanal/kategori oluşturma ve silme istekleri arasında 1,5 saniye aralık, başarılı `Reset-After` başlığında gereksiz küresel beklemenin önlenmesi ve gerçek 429 yanıtında uzun beklemeden güvenli durma.
- Her iki EXE ayrı metadata ve self-check ile doğrulanır.

## Güvenlik ve Discord politikası

Bot token’ini gizli tutun ve kimseyle paylaşmayın. Açığa çıkarsa Developer Portal’dan sıfırlayın. Kullanıcı token’iyle otomasyon Discord’un self-bot politikasına aykırıdır; Bot sürümünü kullanın.

## Doğrulama

Windows yayın iş akışı testleri bir kez çalıştırır, iki EXE’yi ayrı ayrı derler, dosya sürüm bilgilerini doğrular ve paketlenmiş uygulamanın kullanıcı/bot modunu kendi dosya adına göre seçtiğini kontrol eder.