# Sunucu Kopyalama v1.0.2

## Düzeltmeler

- Tür 20 artık kaynak önizlemesini durdurmaz.
- Tür 20, Discord'un belgelenmiş kanal türleri arasında bulunmadığından metin/ses türüne tahminî olarak dönüştürülmez.
- Tür 20 kanalı ve ona bağlı alt kanallar kopyalamadan atlanır; önizlemede uyarı ve işlem günlüğünde kayıt gösterilir.
- Diğer desteklenen kanallar normal aktarım ve son doğrulama adımlarından geçer.
- Yerel yapı yedeği atlanan kanalların ham kaynak kayıtlarını korur.

## Doğrulama

- Bir yeni regresyon testi eklendi (v1.0.1'de 43 test vardı).
- Windows release iş akışı testleri, EXE sürüm bilgilerini ve paketlenmiş GUI öz denetimini çalıştırır.
- EXE yalnızca bu kontroller başarılı olduğunda GitHub Release'e yüklenir.
