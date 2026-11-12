$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python ortamı oluşturulamadı.' }
}

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Bağımlılıklar kurulamadı.' }

& $python -m unittest -q test_copier test_ui
if ($LASTEXITCODE -ne 0) { throw 'Testler başarısız.' }

$variants = @(
    [pscustomobject]@{
        Mode = 'user'
        Name = 'Sunucu-Kopyalama_v1.0.6_Kullanıcı'
        VersionFile = 'version_info_user.txt'
        Description = 'Discord sunucu yapısı kopyalama - Kullanıcı sürümü'
    },
    [pscustomobject]@{
        Mode = 'bot'
        Name = 'Sunucu-Kopyalama_v1.0.6_Bot'
        VersionFile = 'version_info_bot.txt'
        Description = 'Discord sunucu yapısı kopyalama - Bot sürümü'
    }
)

foreach ($variant in $variants) {
    & $python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --add-data 'assets;assets' --add-data 'THIRD_PARTY_NOTICES.md;.' --add-data 'LICENSE;.' --icon assets/app.ico --version-file $variant.VersionFile --name $variant.Name app.py
    if ($LASTEXITCODE -ne 0) { throw "EXE derlenemedi: $($variant.Name)" }

    $exeName = "$($variant.Name).exe"
    $exe = Join-Path $PSScriptRoot "dist\$exeName"
    if (-not (Test-Path -LiteralPath $exe)) { throw "EXE bulunamadı: $exe" }

    $info = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($exe)
    if ($info.ProductName -ne 'Sunucu Kopyalama' -or
        $info.FileVersion -ne '1.0.6.0' -or
        $info.ProductVersion -ne '1.0.6.0' -or
        $info.OriginalFilename -ne $exeName -or
        $info.FileDescription -ne $variant.Description -or
        $info.CompanyName -ne 'DevFrosty' -or
        [string]::IsNullOrWhiteSpace($info.LegalCopyright) -or
        [string]::IsNullOrWhiteSpace($info.Language)) {
        throw "EXE sürüm bilgileri eksik veya yanlış: $exeName"
    }

    $report = Join-Path $PSScriptRoot "build\$($variant.Name)-self-check.json"
    $process = Start-Process -FilePath $exe -ArgumentList @('--self-check', '--report', ('"{0}"' -f $report)) -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Paketlenmiş uygulama kontrolü başarısız: $exeName" }

    $check = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
    if ($check.auth_mode -ne $variant.Mode -or $check.gui -ne 'ok' -or $check.network -ne 'not used') {
        throw "Paketlenmiş uygulama yanlış kimlik doğrulama modunda açıldı: $exeName"
    }

    Write-Output "Hazır: $exe"
}
