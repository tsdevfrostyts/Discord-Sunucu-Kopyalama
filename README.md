# Sunucu Kopyalama

Windows 10/11 (64-bit) için Discord sunucularının **rol, kategori, kanal ve rol bazlı kanal izinlerini** aktarmaya yardımcı olan açık kaynaklı masaüstü uygulaması.

[![XERJ Corpus Hub contributor](https://hub.xerj.org/contributors/tsdevfrostyts/badge.svg)](https://hub.xerj.org/contributors/tsdevfrostyts)

**XERJ katkı profili:** [DevFrosty](https://hub.xerj.org/contributors/tsdevfrostyts)

## İndirme

**Güncel sürüm: v1.0.7** · [Tüm sürümleri ve indirmeleri aç](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases)

| Dosya | Ne zaman kullanılmalı? |
|---|---|
| [Bot sürümü – Sunucu-Kopyalama_v1.0.7_Bot.exe](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases/download/v1.0.7/Sunucu-Kopyalama_v1.0.7_Bot.exe) | **Önerilen.** Ayrı bir Discord botu ile çalışır. |
| [Kullanıcı sürümü – Sunucu-Kopyalama_v1.0.7_Kullanici.exe](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/releases/download/v1.0.7/Sunucu-Kopyalama_v1.0.7_Kullanici.exe) | Kişisel kullanıcı token’i kullanır. Discord'un self-bot kurallarına aykırı olduğu için önerilmez; hesabınız kısıtlanabilir veya kapatılabilir. |

**Normal kullanım için Bot sürümünü seçin.** İndirilen EXE tek başına çalışır; son kullanıcıların Python, Git, Node.js veya npm kurması gerekmez. Dosyayı indirin ve açın. Kaynak koddan çalıştırmak veya kendi EXE dosyanızı üretmek istiyorsanız aşağıdaki CMD kurulumunu izleyin.

## CMD üzerinden kurulum (kaynak kod)

Bu proje Python ile yazılmıştır. Kurulum için **Python 3.14** ve depoyu indirmek için **Git** gerekir. Node.js ve npm bu projede kullanılmaz.

### 1. Python ve Git'i yükleyin

Windows Komut İstemi'ni (CMD) açın. Bilgisayarınızda `winget` varsa aşağıdaki komutları çalıştırın:

```cmd
winget install --id Python.Python.3.14 -e
winget install --id Git.Git -e
```

Kurulum bittikten sonra CMD penceresini kapatıp yeniden açın. Sürümleri kontrol edin:

```cmd
python --version
git --version
```

Python sürümü `3.14.x` olmalıdır. `winget` komutu bulunamıyorsa Windows'taki **App Installer / Uygulama Yükleyicisi** bileşenini Microsoft Store üzerinden yükleyin. Python veya Git yeni kurulduysa PATH değişikliklerinin uygulanması için yeni bir CMD penceresi açın.

### 2. Depoyu indirin ve sanal ortamı hazırlayın

Aşağıdaki komutları CMD'de sırayla çalıştırın. İlk `cd` komutu depoyu kullanıcı klasörünüze indirir; farklı bir klasör tercih ediyorsanız önce o klasöre geçebilirsiniz.

```cmd
cd /d "%USERPROFILE%"
git clone https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama.git
cd Discord-Sunucu-Kopyalama
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Uygulamayı başlatın

```cmd
.venv\Scripts\python.exe app.py --bot-mode
```

Kaynak kod doğrudan `app.py` ile çalıştırıldığında varsayılan olarak Kullanıcı modunu açar. Yukarıdaki `--bot-mode` parametresi güvenli ve önerilen Bot modunu seçer. Sanal ortamı etkinleştirmeniz gerekmez; komutlar proje içindeki Python ortamını doğrudan kullanır. Böylece bilgisayarınızdaki diğer Python projelerinin paketleri etkilenmez.

### İsteğe bağlı: EXE dosyalarını kendiniz oluşturun

Proje kök klasöründeyken CMD'de çalıştırın:

```cmd
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

`build.ps1` gerekli sanal ortamı ve bağımlılıkları hazırlar, otomatik testleri çalıştırır, ardından Kullanıcı ve Bot EXE dosyalarını ayrı ayrı üretir ve paketlenmiş uygulamaları kontrol eder. Çıktılar `dist` klasörüne yazılır. Derleme için Python 3.14 ve internet bağlantısı gerekir.

## Botu Discord'a hazırlama

Bot sürümünü kullanmak için kendi Discord uygulamanızı oluşturmanız gerekir:

1. [Discord Developer Portal](https://discord.com/developers/applications) üzerinden **New Application** ile uygulama oluşturun ve **Bot** bölümünden bot ekleyin.
2. **Bot** bölümündeki token'i alın. Token'i kimseyle paylaşmayın ve README'ye, ekran görüntüsüne ya da komut satırına yazmayın.
3. **OAuth2 → URL Generator** bölümünde `bot` kapsamını seçerek bot davet bağlantısını oluşturun. Botu hem kaynak hem hedef sunucuya ekleyin.
4. **Kaynak sunucuda:** Botun kopyalanacak bütün kategori ve kanalları görebilmesi gerekir (`View Channel`).
5. **Hedef sunucuda:** Botun `Administrator` yetkisi olmalıdır. Ayrıca botun en üst rolünü, değiştirilmesini istediğiniz hedef rollerin üzerine taşıyın. Discord rol hiyerarşisi nedeniyle botun en üst rolüyle aynı veya daha yukarıda olan hedef roller korunur; bot bu rolleri silemez veya düzenleyemez.

Bot token'i uygulamada maskeli gösterilir. Bot sürümünde token'in başına `Bot ` yazmak isteğe bağlıdır; uygulama gerekli yetkilendirme biçimini kendisi ekler.

## Kullanım

1. Uygulamanın Bot sürümünü açın ve bot token'ini girin.
2. Discord'da **Kullanıcı Ayarları → Gelişmiş → Geliştirici Modu** seçeneğini etkinleştirin. Kaynak ve hedef sunucuya sağ tıklayıp **Sunucu Kimliğini Kopyala** seçeneğiyle iki sunucunun ID'sini alın.
3. **Kaynak sunucu ID** alanına kopyalanacak sunucunun, **Hedef sunucu ID** alanına yapının aktarılacağı sunucunun ID'sini girin. İki ID aynı olamaz; bot iki sunucuda da üye olmalıdır.
4. **Sunucuları incele** adımıyla önizlemeyi oluşturun. Sunucu adlarını, silinmesi/oluşturulması beklenen rol ve kanal sayılarını ve uyarıları kontrol edin.
5. Her şey doğruysa **Hedefi sil ve kopyala** düğmesiyle aktarımı başlatın. İşlem sürerken uygulamayı kapatmayın; durdurma veya hata durumunda daha önce tamamlanan değişiklikler geri alınmaz.

## Neler aktarılır?

| Öğe | Davranış |
|---|---|
| Roller | Rol adı ve ana rengi aktarılır. Genel rol izinleri, entegrasyon bağlantıları ve diğer rol ayarları aktarılmaz. |
| Kategoriler | İsimleri ve sıraları aktarılır. |
| Metin ve ses kanalları | Kanal adı, türü, kategori bağlantısı ve sıralaması aktarılır. |
| Kanal izinleri | Yalnızca **rollere verilmiş kanal izinleri** aktarılır. Önce tüm kanallar oluşturulur ve sıralanır; izinler daha sonra uygulanır. |
| Forum kanalları | Forum kanalı olarak oluşturulur; forum etiketleri ve ek forum ayarları aktarılmaz. |
| Duyuru ve medya kanalları | Normal metin kanalına dönüştürülür. |
| Sahne kanalları | Normal ses kanalına dönüştürülür. |

**Aktarılmayanlar:** Mesajlar, üyeler, kişiye özel kanal izinleri, genel rol yetkileri, emojiler, sunucu ayarları ve kural/moderasyon kanalı atamaları. Discord'un desteklemediği `20` kanal türü ve bu kanala bağlı alt kanallar atlanır. Uygulama Discord'un API ve sunucu limitlerini aşmaya çalışmaz.

## Önemli: hedef sunucuda değişiklik yapılır

Kopyalama, hedef sunucudaki silinebilir mevcut kanal ve rolleri kaldırmayı dener; ardından kaynak yapısını oluşturur. **Silinen bir kanalın mesajları da silinir ve bu uygulama mesajları yedeklemez.** İşlemi başlatmadan önce hedef sunucunun doğru olduğunu önizlemede mutlaka kontrol edin. Başlatma düğmesinden sonra ikinci bir onay penceresi gösterilmez.

- Botun yönetemediği yüksek/eşit seviyedeki hedef roller, bot hesabına atanmış roller ve Discord tarafından yönetilen roller korunur.
- Bazı kanallar Discord'un sunucu özellikleri veya izinleri nedeniyle silinemeyebilir. Bu durumda işlem günlüğünde `SİLİNEMEDİ` uyarısı gösterilir; uygulama kalan adımlara devam edebilir.
- Discord `429` istek sınırı bildirdiğinde uygulama uzun süre otomatik beklemek yerine işlemi durdurur. Bildirilen süre dolmadan yeniden denemeyin.
- İptal, ağ kesintisi veya API hatası daha önce tamamlanmış silme/oluşturma adımlarını geri almaz. Kısmi aktarım oluşabilir; hedef sunucuyu Discord'da kontrol edin.

## Yerel yedekler

Aktarım öncesinde kaynak ve hedef sunucu yapısının JSON yedeği oluşturulur. Yedekler:

```text
%LOCALAPPDATA%\SunucuKopyalayici\backups
```

Klasörü uygulamadaki **Yapı yedeklerini aç** düğmesiyle de açabilirsiniz. Yedekler rol/kanal isimleri, kimlikleri ve izin bilgileri gibi sunucu yapı verilerini içerir. **Mesajları, üyeleri veya silinen içeriği kurtarmaz; otomatik geri yükleme özelliği değildir.** Paylaşmadan önce içeriğini inceleyin.

## Gizlilik ve güvenlik

- Uygulama telemetri, reklam veya geliştiriciye analiz verisi gönderme işlevi içermez.
- Token yalnızca uygulama belleğinde tutulur; diske veya işlem günlüğüne yazılmaz. Discord API isteklerinde doğrudan `discord.com` adresine gönderilir. Başarılı aktarım tamamlandığında veya uygulama kapatıldığında temizlenir.
- Yerel JSON yedekleri bilgisayarınızda kalır. Bunlar sunucu kimlikleri, rol/kanal yapısı ve izin bilgileri içerebildiği için herkese açık paylaşılmamalıdır.
- Açık kaynak olması veya bir antivirüs taramasının temiz çıkması tek başına güvenlik garantisi değildir. Kaynak kodunu inceleyebilir ve yalnızca resmi GitHub Releases sayfasından indirme yapabilirsiniz.

### Windows SmartScreen veya antivirüs uyarıları

Uygulama Python ile yazılır ve PyInstaller kullanılarak tek EXE halinde paketlenir. PyInstaller tek dosya uygulamaları çalışırken bazı bileşenleri Windows geçici klasöründeki `_MEI*` dizinine çıkarabilir; bu paketleme davranışı bazı güvenlik ürünlerinin sezgisel kurallarıyla eşleşebilir. Projenin yayın derlemesinde UPX kullanılmaz. Bununla birlikte bu bilgi, herhangi bir antivirüs uyarısının kesinlikle yanlış olduğunu kanıtlamaz.

Mevcut yayın iş akışında Windows'un güvenilir bir sertifika otoritesi tarafından doğrulanmış kod imzası adımı bulunmaz. Bu nedenle Windows yayıncıyı doğrulayamayabilir veya SmartScreen uyarısı gösterebilir. **Uyarıyı aşmak için Windows Defender'ı kapatmanız, antivirüs korumasını devre dışı bırakmanız veya kök sertifika yüklemeniz istenmez.** Emin değilseniz dosyayı çalıştırmayın.

[PyInstaller: tek dosyalı uygulamanın çalışma şekli](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works) · [Microsoft: SmartScreen itibar sistemi](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)

[22 Ekim 2026 tarihli VirusTotal bağlantısı](https://www.virustotal.com/gui/file/b9c54eead0fea243b368639011d29ff5e5dbafe5241ce958bf526e023d947737/detection) **v1.0.1** dosyasına aittir; güncel v1.0.7 EXE dosyası için tarama sonucu olarak değerlendirilmemelidir.

## Sürüm notları

- **[v1.0.7](docs/releases/RELEASE_NOTES_v1.0.7.md):** Botun rol hiyerarşisi nedeniyle yönetemediği hedef roller güvenli biçimde korunur; diğer aktarım adımları devam eder.
- **[v1.0.6](docs/releases/RELEASE_NOTES_v1.0.6.md):** Kullanıcı ve Bot için iki ayrı EXE, bot token doğrulaması ve bot yetki kontrolleri.
- **[v1.0.5](docs/releases/RELEASE_NOTES_v1.0.5.md):** İstek sınırı ve kanal oluşturma sırasına ilişkin düzeltmeler.
- **[v1.0.4](docs/releases/RELEASE_NOTES_v1.0.4.md):** Hedefte hesaba atanmış rollerin korunması.
- **[v1.0.3](docs/releases/RELEASE_NOTES_v1.0.3.md):** Kanal izinleriyle ilgili Discord API `50013` hatası için düzeltmeler.
- **[v1.0.2](docs/releases/RELEASE_NOTES_v1.0.2.md):** Desteklenmeyen kanal türü `20` ve bağlı kanalların güvenli biçimde atlanması.

## Test ve doğrulama

[v1.0.7 Windows yayın iş akışı](https://github.com/tsdevfrostyts/Discord-Sunucu-Kopyalama/actions/runs/43334308649) başarıyla tamamlandı. İş akışı `test_copier` ve `test_ui` testlerini çalıştırır; iki EXE'yi ayrı ayrı derler, sürüm bilgilerini ve paketlenmiş arayüz/kimlik doğrulama modunu kontrol eder. Testler sahte Discord API yanıtlarıyla yapılır; bu, her olası gerçek sunucu yapılandırmasında canlı aktarımın test edildiği anlamına gelmez.

## Depo yapısı

- `app.py`: masaüstü uygulamasının giriş noktası ve arayüz akışı.
- `copier.py`: Discord API bağlantısı, önizleme, aktarım ve doğrulama işlemleri.
- `modern_ui.py` ve `assets/`: arayüz bileşenleri ve görsel dosyalar.
- `docs/releases/`: sürüm geçmişi ve her sürümün değişiklik notları.
- `packaging/`: Kullanıcı ve Bot EXE dosyalarının Windows sürüm bilgileri.
- `test_copier.py` ve `test_ui.py`: otomatik aktarım ve arayüz testleri.
- `build.ps1`: test, Windows EXE derleme ve paket öz denetim adımları.

## Lisans ve üçüncü taraf bileşenler

Proje [MIT lisansı](LICENSE) altındadır. Arayüz ve diğer bileşenlerin lisansları [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasında listelenir. Bu proje Discord tarafından desteklenmez veya onaylanmaz.
