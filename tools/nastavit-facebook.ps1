$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Repo = 'petrkotab666/nasekadan'
$GraphVersion = 'v25.0'

function Pause-End {
    Write-Host ''
    Read-Host 'Stiskněte Enter pro ukončení'
}

function Read-SecureText([string]$Prompt) {
    $secure = Read-Host $Prompt -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

try {
    Write-Host '============================================================' -ForegroundColor Cyan
    Write-Host ' NAŠE KADAŇ - TRVALÉ PROPOJENÍ FACEBOOK STRÁNKY' -ForegroundColor Cyan
    Write-Host '============================================================' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Budete potřebovat vlastní aplikaci na developers.facebook.com.' -ForegroundColor Yellow
    Write-Host 'Uživatelský token musí obsahovat oprávnění:'
    Write-Host 'pages_show_list, pages_read_engagement a pages_manage_posts'
    Write-Host ''

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw 'Chybí GitHub CLI (gh). Nainstalujte jej z https://cli.github.com/ a přihlaste se příkazem gh auth login.'
    }

    gh auth status 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Nejprve proběhne přihlášení ke GitHubu.' -ForegroundColor Yellow
        gh auth login
        if ($LASTEXITCODE -ne 0) { throw 'Přihlášení ke GitHubu se nezdařilo.' }
    }

    $appId = (Read-Host 'Meta App ID').Trim()
    if ([string]::IsNullOrWhiteSpace($appId)) { throw 'App ID nebylo zadáno.' }
    $appSecret = Read-SecureText 'Meta App Secret'
    if ([string]::IsNullOrWhiteSpace($appSecret)) { throw 'App Secret nebyl zadán.' }
    $shortUserToken = Read-SecureText 'Krátkodobý Facebook User Access Token'
    if ([string]::IsNullOrWhiteSpace($shortUserToken)) { throw 'User Access Token nebyl zadán.' }

    Write-Host ''
    Write-Host 'Vyměňuji krátkodobý token za dlouhodobý uživatelský token…' -ForegroundColor Cyan
    $exchangeUrl = 'https://graph.facebook.com/{0}/oauth/access_token?grant_type=fb_exchange_token&client_id={1}&client_secret={2}&fb_exchange_token={3}' -f `
        $GraphVersion,
        [uri]::EscapeDataString($appId),
        [uri]::EscapeDataString($appSecret),
        [uri]::EscapeDataString($shortUserToken)
    try {
        $exchange = Invoke-RestMethod -Method Get -Uri $exchangeUrl -TimeoutSec 45
    }
    catch {
        throw "Výměna tokenu se nezdařila. Zkontrolujte, že token pochází ze stejné Meta aplikace jako App ID: $($_.Exception.Message)"
    }
    $longUserToken = [string]$exchange.access_token
    if ([string]::IsNullOrWhiteSpace($longUserToken)) {
        throw 'Meta nevrátila dlouhodobý uživatelský token.'
    }

    $accountsUrl = 'https://graph.facebook.com/{0}/me/accounts?fields=name,access_token,tasks&limit=100&access_token={1}' -f `
        $GraphVersion,
        [uri]::EscapeDataString($longUserToken)
    try {
        $response = Invoke-RestMethod -Method Get -Uri $accountsUrl -TimeoutSec 45
    }
    catch {
        throw "Facebook stránky se nepodařilo načíst: $($_.Exception.Message)"
    }

    $pages = @($response.data)
    if ($pages.Count -eq 0) {
        throw 'Facebook nevrátil žádnou stránku, kterou tento účet spravuje.'
    }

    Write-Host ''
    Write-Host 'Dostupné Facebook stránky:' -ForegroundColor Cyan
    for ($i = 0; $i -lt $pages.Count; $i++) {
        $tasks = @($pages[$i].tasks) -join ', '
        Write-Host ("[{0}] {1} (ID {2})" -f ($i + 1), $pages[$i].name, $pages[$i].id)
        Write-Host ("    oprávnění: {0}" -f $tasks) -ForegroundColor DarkGray
    }

    do {
        $choiceRaw = Read-Host 'Zadejte číslo stránky Naše Kadaň'
        $choice = 0
        [void][int]::TryParse($choiceRaw, [ref]$choice)
    } while ($choice -lt 1 -or $choice -gt $pages.Count)

    $page = $pages[$choice - 1]
    $pageId = [string]$page.id
    $pageToken = [string]$page.access_token
    if ([string]::IsNullOrWhiteSpace($pageToken)) {
        throw 'Facebook nevrátil Page Access Token.'
    }

    $taskText = (@($page.tasks) -join ' ').ToUpperInvariant()
    if ($taskText -notmatch 'CREATE_CONTENT|MANAGE|FULL_CONTROL') {
        throw 'Vybraný účet nemá pro stránku oprávnění vytvářet obsah nebo plnou správu.'
    }

    $verifyUrl = 'https://graph.facebook.com/{0}/{1}?fields=id,name&access_token={2}' -f `
        $GraphVersion,
        [uri]::EscapeDataString($pageId),
        [uri]::EscapeDataString($pageToken)
    $verified = Invoke-RestMethod -Method Get -Uri $verifyUrl -TimeoutSec 45
    if ([string]$verified.id -ne $pageId) {
        throw 'Ověření Page Access Tokenu selhalo.'
    }

    $appAccessToken = "$appId|$appSecret"
    $debugUrl = 'https://graph.facebook.com/{0}/debug_token?input_token={1}&access_token={2}' -f `
        $GraphVersion,
        [uri]::EscapeDataString($pageToken),
        [uri]::EscapeDataString($appAccessToken)
    $debug = Invoke-RestMethod -Method Get -Uri $debugUrl -TimeoutSec 45
    if ($debug.data.is_valid -ne $true) {
        throw 'Meta označila Page Access Token jako neplatný.'
    }

    $expiryText = 'Meta neuvedla pevné datum vypršení.'
    $expiresAt = [long]($debug.data.expires_at)
    if ($expiresAt -gt 0) {
        $expiry = [DateTimeOffset]::FromUnixTimeSeconds($expiresAt).ToLocalTime()
        $expiryText = "Platnost tokenu do: $($expiry.ToString('dd. MM. yyyy HH:mm zzz'))"
        if ($expiry -lt [DateTimeOffset]::Now.AddDays(30)) {
            throw "Vygenerovaný token má příliš krátkou platnost. $expiryText"
        }
    }

    Write-Host ''
    Write-Host "Ukládám zabezpečené údaje pro stránku: $($verified.name)" -ForegroundColor Cyan
    $pageId | gh secret set FACEBOOK_PAGE_ID --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_PAGE_ID.' }
    $pageToken | gh secret set FACEBOOK_PAGE_ACCESS_TOKEN --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_PAGE_ACCESS_TOKEN.' }
    $appSecret | gh secret set FACEBOOK_APP_SECRET --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_APP_SECRET.' }
    gh variable set FACEBOOK_APP_ID --body $appId --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_APP_ID.' }
    gh variable set FACEBOOK_GRAPH_VERSION --body $GraphVersion --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_GRAPH_VERSION.' }
    gh variable set FACEBOOK_PAGE_KEY --body 'nasekadan' --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_PAGE_KEY.' }

    Write-Host ''
    Write-Host 'PROPOJENÍ JE HOTOVÉ.' -ForegroundColor Green
    Write-Host "Facebook stránka: $($verified.name)"
    Write-Host "Page ID: $pageId"
    Write-Host $expiryText
    Write-Host 'Token a App Secret byly uloženy jako zašifrované GitHub Secrets.'
    Write-Host ''

    $test = Read-Host 'Spustit nyní Facebook automat a zpracovat čekající frontu? (A/N)'
    if ($test -match '^[AaYy]') {
        gh workflow run publish-facebook.yml --repo $Repo
        if ($LASTEXITCODE -ne 0) { throw 'Facebook workflow se nepodařilo spustit.' }
        Write-Host 'Automat byl spuštěn. Stav otevřete zde:' -ForegroundColor Green
        Write-Host "https://github.com/$Repo/actions/workflows/publish-facebook.yml"
        Start-Process "https://github.com/$Repo/actions/workflows/publish-facebook.yml"
    }
}
catch {
    Write-Host ''
    Write-Host "CHYBA: $($_.Exception.Message)" -ForegroundColor Red
    Pause-End
    exit 1
}

Pause-End
