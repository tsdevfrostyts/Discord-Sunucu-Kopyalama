# Sunucu Kopyalama v1.0.7

## Değişiklikler

- Botun en üst rolüyle aynı veya daha yüksek konumdaki, botun yönetemediği hedef roller otomatik olarak korunur.
- Hiyerarşi dışında kalan rollerin hiçbiri silinmez, düzenlenmez veya rol sıralaması isteğiyle değiştirilmez.
- Birden fazla yüksek rol varsa tamamı isimleriyle önizlemede listelenir ve aktarım günlüğünde `KORUNDU` olarak gösterilir.
- Korunan roller yüzünden aktarım durmaz; silinebilir roller, yeni kaynak rolleri, kategoriler, kanallar ve izinler için diğer adımlar devam eder.
- Botun hiyerarşisi yeni rollerin kaynak sırasına göre güvenle sıralanmasına yetmiyorsa yeni roller Discord'un varsayılan sıralamasında bırakılır. Mevcut hedef roller toplu rol sıralama isteğine dahil edilmez.
- Son doğrulama korunan yüksek rollerin hâlâ mevcut ve temel özelliklerinin değişmemiş olduğunu kontrol eder.
- Kullanıcı sürümündeki önceki rol hiyerarşisi reddi korunur.

## Güvenlik davranışı

Korunan yüksek rollerin ad, izin, renk ve diğer temel özellikleri değişmeden kalmalıdır. Uygulama bu rollere DELETE veya PATCH isteği göndermez. Hedef sunucuda rol/kanal sınırları aşılırsa işlem, kısmi değişiklikleri büyütmeden hata verir.

## Önceki sürüm özellikleri

v1.0.6'daki ayrı Kullanıcı ve Bot EXE dosyaları, Bot token doğrulaması, botun hedefte Administrator yetkisi kontrolü ve v1.0.5 rate-limit/kanal oluşturma sırası düzeltmeleri korunur.

## Doğrulama

Windows yayın iş akışı birim/arayüz testlerini çalıştırır, Kullanıcı ve Bot EXE dosyalarını ayrı ayrı üretir, sürüm metadata bilgilerini ve paketlenmiş mod seçimlerini doğrular.