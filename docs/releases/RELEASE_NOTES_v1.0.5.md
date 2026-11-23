# Sunucu Kopyalama v1.0.5

## Değişiklikler

- Her rol/kanal/kategori oluşturma ve silme isteği arasında 1,5 saniye bulunur.
- Başarılı yanıttaki `X-RateLimit-Reset-After` değeri artık uygulamanın tüm API isteklerini küresel olarak bekletmez.
- Gerçek HTTP 429 yanıtında uzun bekleme boyunca arayüz kilitlenmez; işlem durdurulur ve Discord'un bildirdiği bekleme süresi gösterilir. Otomatik tekrar deneme yapılmaz.
- Kategoriler ve kanallar ilk oluşturulurken `permission_overwrites` gönderilmez. Tüm yapılar oluşturulup sıralandıktan sonra rol izinleri ayrı API istekleriyle uygulanır.
- Özel kanalların izinleri son aşamada uygulandığı için geçici varsayılan görünürlük riski önizlemede uyarı olarak belirtilir.

## Doğrulama

Windows yayın iş akışı `build.ps1` içindeki aktarım testlerini, GUI testlerini, EXE sürüm metadata kontrolünü ve paketlenmiş GUI öz denetimini çalıştırır.