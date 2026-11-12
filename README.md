# Sunucu Kopyalama

Windows için açık kaynak, animasyonlu Discord sunucu yapısı kopyalama uygulaması.

**Kullanıcı sürümü:** [Sunucu-Kopyalama_v1.0.6_Kullanıcı.exe](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases/download/v1.0.6/Sunucu-Kopyalama_v1.0.6_Kullan%C4%B1c%C4%B1.exe)

**Bot sürümü:** [Sunucu-Kopyalama_v1.0.6_Bot.exe](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases/download/v1.0.6/Sunucu-Kopyalama_v1.0.6_Bot.exe) · [Tüm sürümler](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases)

## v1.0.6

v1.0.6 iki ayrı EXE üretir: kullanıcı token’li mevcut bağlantı ve resmi Discord Bot token’li bağlantı. Bot sürümünde Authorization başlığı `Bot` şemasıyla gönderilir; botun iki sunucuda da bulunması, kaynakta tüm kanalları görebilmesi ve hedefte Administrator yetkisi ile yeterli rol hiyerarşisine sahip olması doğrulanır. Botun atanmış rolleri silinmez. v1.0.5’in 1,5 saniyelik oluşturma/silme aralığı, izinleri son aşamada uygulama ve 429’da beklemeden durma davranışı korunur. [v1.0.6 sürüm notları](RELEASE_NOTES_v1.0.6.md).

> **Önerilen yöntem Bot sürümüdür.** Kullanıcı token’ini otomasyonda kullanmak Discord’un self-bot kurallarına aykırıdır ve hesabın kapatılmasına neden olabilir.

## Önceki sürüm: v1.0.4

Hedefte hesaba atanmış rollerin silinmesi engellenir; böylece yönetici yetkisi sağlayan rol korunur. Ayrıntılar için [v1.0.4 sürüm notlarına](RELEASE_NOTES_v1.0.4.md) bakın.

## Önceki sürüm: v1.0.2

Tür 20 kanal türü ve bağlı alt kanallar desteklenmeyen olarak atlanır. Ayrıntılar için [v1.0.2 sürüm notlarına](RELEASE_NOTES_v1.0.2.md) bakın.

## Gizlilik

Uygulama tamamen bilgisayarınızda çalışır. Geliştiriciye hiçbir bilgi veya telemetri göndermez; analiz, reklam veya harici veri toplama servisi içermez. İşlemleri gerçekleştirmek için internet üzerinden **doğrudan Discord API’sine** bağlanır; seçilen sürümün kullanıcı veya bot token’i yalnızca bu API’ye gönderilir.

Token uygulama tarafından diske veya işlem günlüğüne yazılmaz. Önizleme, hata ve iptal sonrasında tekrar denemek için bellekte tutulur; kopyalama doğrulanarak tamamlandığında veya uygulama kapatıldığında temizlenir. Kaynak/hedef sunucu yapıları yerel JSON yedeğine yazılır; bu dosyalar sunucu/rol/kanal kimlikleri ve izin bilgileri içerir. Yedekleri paylaşmadan önce inceleyin.

## Kapsam

- Roller: isim ve ana renk.
- Kategoriler ve kanallar: isim, sıralama, kategori ilişkisi ve rollere göre kanal izinleri.
- Ses kanalları ses, forum kanalları forum olarak oluşturulur. Forum etiketleri ve ek ayarlar kopyalanmaz.
- Duyuru ve medya kanalları normal metin; sahne kanalları normal ses kanalına dönüştürülür.
- Mesajlar, üyeler, üyelere özel izinler, genel rol yetkileri, emojiler ve sunucu ayarları kopyalanmaz. Kural/moderasyon kanalı atanmaz.

Forum oluşturma Discord’un hedef sunucudaki özellik ve API kısıtlarına bağlıdır; uygulama bunları aşmaz.

## VirusTotal ve Windows uyarıları neden görülebilir?

Uygulama Python ile yazılır ve PyInstaller kullanılarak tek EXE olarak paketlenir. Açılışta gerekli Python/Tcl/Tk kitaplıkları, temalar ve fontlar Windows'un geçici klasöründeki `_MEI*` dizinine açılır; `python314.dll` uygulama sürecine yüklenir. Bu gerçek paketleme davranışı, genel “PE dosyası oluşturma” ve “Python olmayan süreçte Python yükleme” kurallarıyla eşleşebilir. `obfuscated` etiketi tek başına özel bir kod gizleme yöntemi kullanıldığını kanıtlamaz; bu projede ek obfuscator veya UPX kullanılmıyor. Gereksiz toplu paketleme kaldırıldı; 43 ham Python ve 7 paket metadata dosyası artık çalışma sırasında açılmıyor.

Kaynak incelemesinde uygulamanın kök sertifika eklediği, otomatik başlatma kurduğu veya geliştiriciye bilgi gönderdiği bir kod yolu bulunmadı. Eski sandbox raporundaki sertifika deposu uyarısının kesin süreç ve kayıt yolu erişilebilen özetten doğrulanamadı. Bu yüzden bu uyarıyı kesin olarak “yanlış alarm” diye kapatmıyoruz. Python'un işletim sistemi sürümü sorgusu da bazı ortamlarda `cmd /c ver` komutuna düşebilir; bu uygulamanın uzaktan komut aldığı anlamına gelmez.

**Antivirüs tespiti, dijital imza güveni ve SmartScreen itibarı ayrı değerlendirmelerdir.** Mevcut EXE kendinden imzalıdır; sertifikası bağımsız, Windows'un güvendiği bir otorite tarafından onaylanmamıştır. Bu nedenle “yayıncı doğrulanamadı” veya güvenilmeyen kök uyarısı görülebilir. Zaman damgası yayıncı kimliğini onaylamaz. Kullanıcı sayısının artması bu sertifikayı otomatik olarak güvenilir yapmaz. SmartScreen'in dosya/yayıncı itibarı zamanla değişebilir; belirli bir kullanıcı sayısında veya birkaç hafta içinde onay garantisi yoktur. [Microsoft'un açıklaması](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).

Bir tarama sonucu uygulamanın bütünü için güvenlik garantisi değildir; açık kaynak olması veya imza bulunması da tek başına yeterli değildir. Kaynak kodunu ve [v1.0.1 EXE'nin VirusTotal sonucunu](https://www.virustotal.com/gui/file/b9c54eead0fea243b368639011d29ff5e5dbafe5241ce958bf526e023d947737/detection) birlikte değerlendirebilirsiniz. Uyarıları gidermek için Windows/antivirüs korumalarını kapatmanız veya kök sertifika yüklemeniz istenmez.

22 Ekim 2026 tarihinde v1.0.1 EXE'sinin son taraması **4/70** tespit bildirdi: Bkav Pro, Elastic, Microsoft (`Trojan:Win32/Wacatac.C!ml`) ve SecureAge. Aynı dosyanın yerel Defender taramasında tehdit bulunmadı; motor, bulut ve tanım farklılıkları nedeniyle sonuçlar değişebilir. Bu farklılık dört tespitin yanlış olduğunu kanıtlamaz. VirusTotal ayrıntılarındaki `invalid-signature` etiketinin açıklaması, imza zincirinin güvenilmeyen bir kökte sonlanmasıdır; mevcut kendinden imzalı sertifika için beklenen güven sınırlamasıdır.

Paketleme davranışı için: [PyInstaller'ın tek dosya çalışma açıklaması](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works).

## Kullanım

1. Kullanacağınız EXE’yi açın. Python kurulumu gerekmez.
2. **Bot sürümü:** Discord Developer Portal’da bir uygulama/bot oluşturun. Botu OAuth2 `bot` kapsamıyla hem kaynak hem hedef sunucuya ekleyin. Kaynakta kopyalanacak tüm kanallarda `View Channel` izni; hedefte `Administrator` izni verin. Botun en üst rolünü hedefte silinecek rollerin üstüne taşıyın. Bot token’ini Bot EXE’ye girin; `Bot ` ön eki isteğe bağlıdır.
3. **Kullanıcı sürümü:** Kullanıcı token’iyle giriş yapar; bu yöntem Discord kuralları nedeniyle önerilmez.
4. Kaynak/hedef sunucu ID’lerini girip önizlemeyi inceleyin ve aktarımı başlatın. Bot sürümünde botun atanmış rolleri korunur; rol hiyerarşisi uygun değilse silme başlamadan hata verilir.

**Kopyalama hedefte mevcut rol ve kanalları silmeye çalışır. Kanal silinmesi içindeki mesajları da kaybettirebilir. İkinci onay penceresi yoktur; hedef ID’sini önizlemede kontrol edin.** Yerel yedek yalnızca yapı kaydıdır; otomatik geri yükleme ve mesaj kurtarma sağlamaz. İptal/hata tamamlanmış işlemleri geri almaz.

Yapı yedekleri `%LOCALAPPDATA%\SunucuKopyalayici\backups` altında tutulur; arayüzdeki düğmeyle açılabilir.

Kullanıcı token’iyle otomasyon Discord’un self-bot kurallarınca yasaktır ve hesabınızın kapatılmasına yol açabilir. Bot token’leri de şifre gibi korunmalıdır; kimseyle paylaşmayın. Bir token açığa çıkarsa Discord Developer Portal’dan sıfırlayın.

## Kaynaktan çalıştırma ve EXE oluşturma

Windows 10/11 x64, Python 3.14 ve PowerShell ile:

```powershell
.\build.ps1
```

Bu komut sanal ortamı/bağımlılıkları hazırlar, testleri çalıştırır, `dist/Sunucu-Kopyalama_v1.0.6_Kullanıcı.exe` ve `dist/Sunucu-Kopyalama_v1.0.6_Bot.exe` dosyalarını üretir. Her iki EXE’nin sürüm bilgileri ve paketlenmiş kimlik doğrulama modu ayrı ayrı denetlenir. Derleme bağımlılıklarının kurulumu paket kayıt sistemlerine bağlanır; bu, son kullanıcının EXE çalışma akışından ayrıdır.

Kaynaktan açmak için:

```powershell
.\.venv\Scripts\python.exe app.py
```

## Doğrulama

v1.0.1 için 43 otomatik test (31 çekirdek/aktarım, 12 arayüz) ve paketlenmiş EXE arayüz öz denetimi geçti. v1.0.2'de kanal türü 20 regresyon testi; v1.0.3'te kanal izinleri 50013 geri dönüşü için iki test; v1.0.4'te hesaba atanmış rollerin korunması ve yetki kaybının engellenmesi için regresyon testleri eklendi. Windows release iş akışı testler, EXE sürüm bilgileri ve paketlenmiş arayüz öz denetimi geçmeden sürümü yayımlamaz. Ağ testleri taklit yanıtlarla çalışır. Önceki çalışan çekirdeğin gerçek kopyalama işlemini kullanıcı doğruladı; bu sürümdeki görsel değişiklikler sonrasında tüm canlı Discord senaryoları ayrıca denenmedi.

## Lisans

[MIT](LICENSE). CustomTkinter arayüzü/simgesi ve diğer bileşenlerin lisansları [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasındadır. Discord ile bağlantılı veya Discord tarafından onaylanmış bir ürün değildir.

Derleme notu: gereksiz toplu paket dosyaları kaldırılmıştır; gerekli font/tema ve çalışma zamanı standart PyInstaller hook’larıyla eklenir. UPX kullanılmaz. Dosya ve ürün sürümü 1.0.6.0, dil Türkçe (Türkiye) olarak doldurulur. Antivirüs motorlarının tümü için temiz sonuç garantisi verilmez.
