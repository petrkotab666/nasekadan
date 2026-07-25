$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Repo = 'petrkotab666/nasekadan'
$GraphVersion = 'v25.0'

function Pause-End {
    Write-Host ''
    Read-Host 'Stiskněte Enter pro ukončení'
}

try {
    Write-Host '============================================================' -ForegroundColor Cyan
    Write-Host ' NAŠE KADAŇ - PROPOJENÍ FACEBOOK STRÁNKY' -ForegroundColor Cyan
    Write-Host '============================================================' -ForegroundColor Cyan
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

    Write-Host 'Vložte uživatelský Facebook access token s oprávněními:' -ForegroundColor Yellow
    Write-Host 'pages_show_list, pages_read_engagement a pages_manage_posts'
    $secure = Read-Host 'Facebook User Access Token' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $userToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
    if ([string]::IsNullOrWhiteSpace($userToken)) { throw 'Token nebyl zadán.' }

    $encodedToken = [uri]::EscapeDataString($userToken)
    $url = "https://graph.facebook.com/$GraphVersion/me/accounts?fields=name,access_token,tasks&access_token=$encodedToken"
    try {
        $response = Invoke-RestMethod -Method Get -Uri $url -TimeoutSec 45
    }
    catch {
        throw "Facebook token se nepodařilo ověřit: $($_.Exception.Message)"
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
    if ([string]::IsNullOrWhiteSpace($pageToken)) { throw 'Facebook nevrátil Page Access Token.' }

    $taskText = (@($page.tasks) -join ' ').ToUpperInvariant()
    if ($taskText -notmatch 'CREATE_CONTENT|MANAGE|FULL_CONTROL') {
        Write-Host 'VAROVÁNÍ: Účet zřejmě nemá oprávnění vytvářet obsah na vybrané stránce.' -ForegroundColor Yellow
    }

    $verifyUrl = "https://graph.facebook.com/$GraphVersion/$pageId`?fields=id,name&access_token=$([uri]::EscapeDataString($pageToken))"
    $verified = Invoke-RestMethod -Method Get -Uri $verifyUrl -TimeoutSec 45
    if ([string]$verified.id -ne $pageId) { throw 'Ověření Page Access Tokenu selhalo.' }

    Write-Host ''
    Write-Host "Ukládám zabezpečené údaje pro stránku: $($verified.name)" -ForegroundColor Cyan
    $pageId | gh secret set FACEBOOK_PAGE_ID --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_PAGE_ID.' }
    $pageToken | gh secret set FACEBOOK_PAGE_ACCESS_TOKEN --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_PAGE_ACCESS_TOKEN.' }
    gh variable set FACEBOOK_GRAPH_VERSION --body $GraphVersion --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw 'Nepodařilo se uložit FACEBOOK_GRAPH_VERSION.' }

    Write-Host ''
    Write-Host 'PROPOJENÍ JE HOTOVÉ.' -ForegroundColor Green
    Write-Host "Facebook stránka: $($verified.name)"
    Write-Host "Page ID: $pageId"
    Write-Host 'Token byl uložen jako zašifrovaný GitHub secret a zde se už nevypisuje.'
    Write-Host ''

    $test = Read-Host 'Spustit zkušební publikování článku petice-nemocnice-kadan.html? (A/N)'
    if ($test -match '^[AaYy]') {
        gh workflow run publish-facebook.yml --repo $Repo -f article_path=clanky/petice-nemocnice-kadan.html
        if ($LASTEXITCODE -ne 0) { throw 'Zkušební workflow se nepodařilo spustit.' }
        Write-Host 'Zkušební publikování bylo spuštěno. Stav otevřete přes:' -ForegroundColor Green
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
