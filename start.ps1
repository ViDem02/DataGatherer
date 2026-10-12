# Starts DataGatherer and opens it in the browser. Only Docker Desktop is needed.
# On the first start it creates .env.docker with random passwords and picks a free port.
# Usage: double-click start.bat, or: powershell -ExecutionPolicy Bypass -File start.ps1 [-NoBrowser]
# Written for Windows PowerShell 5.1, which every Windows 10/11 has.
param([switch]$NoBrowser)

Set-Location -Path $PSScriptRoot
$EnvFile = '.env.docker'

function Write-Step([string]$Text) { Write-Host "`n==> $Text" -ForegroundColor Cyan }

function Stop-WithError([string]$Text) {
    Write-Host "`nERROR: $Text`n" -ForegroundColor Red
    exit 1
}

# Random hexadecimal string with $Bytes bytes of entropy
function New-RandomHex([int]$Bytes) {
    $buffer = New-Object byte[] $Bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buffer)
    return ($buffer | ForEach-Object { $_.ToString('x2') }) -join ''
}

# True when a program already listens on 127.0.0.1:$Port
function Test-PortInUse([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try { $client.Connect('127.0.0.1', $Port); return $true }
    catch { return $false }
    finally { $client.Close() }
}

function Get-EnvValue([string]$Name) {
    $line = Get-Content $EnvFile | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
    if (-not $line) { return '' }
    return ($line -split '=', 2)[1].Trim().Trim("'", '"')
}

# Docker Compose cannot read files that start with a UTF-8 byte-order mark, which PowerShell 5.1 writes by default
function Write-TextFile([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText((Join-Path $PSScriptRoot $Path), $Text, (New-Object System.Text.UTF8Encoding $false))
}

function Invoke-Compose { docker compose --env-file $EnvFile @args }


Write-Step 'Checking Docker'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Stop-WithError 'Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/ , start it, then run this again.'
}
docker info 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Stop-WithError 'Docker is installed but not running. Open Docker Desktop, wait until it shows "Engine running", then run this again.'
}
docker compose version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Stop-WithError "This Docker version has no 'docker compose'. Update Docker Desktop, then run this again."
}


$firstStart = $false
if (-not (Test-Path $EnvFile)) {
    Write-Step 'First start: creating the configuration with new random passwords'
    if (-not (Test-Path '.env.docker.example')) {
        Stop-WithError '.env.docker.example is missing. Download DataGatherer again, then run this again.'
    }
    $dbPassword = New-RandomHex 24
    $text = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot '.env.docker.example'))
    $text = $text -replace '(?m)^SECRET_KEY=change-me(?=\r?$)', ('SECRET_KEY=' + (New-RandomHex 40))
    $text = $text -replace '(?m)^SQL_PASSWORD=change-me(?=\r?$)', ('SQL_PASSWORD=' + $dbPassword)
    $text = $text -replace '(?m)^POSTGRES_PASSWORD=change-me(?=\r?$)', ('POSTGRES_PASSWORD=' + $dbPassword)
    $text = $text -replace '(?m)^DJANGO_SUPERUSER_PASSWORD=change-me(?=\r?$)', ('DJANGO_SUPERUSER_PASSWORD=' + (New-RandomHex 12))
    Write-TextFile $EnvFile $text
    $firstStart = $true
}
if (Select-String -Path $EnvFile -Pattern '=change-me\s*$' -Quiet) {
    Stop-WithError "$EnvFile still contains 'change-me' values. Replace each of them with a long random value, then run this again."
}


$alreadyRunning = @(Invoke-Compose ps --status running --services 2>$null) -contains 'nginx'
$port = Get-EnvValue 'APP_PORT'
if (-not $port) {
    $port = 8080
    while (Test-PortInUse $port) {
        $port++
        if ($port -gt 8099) {
            Stop-WithError "Ports 8080 to 8099 are all in use. Set APP_PORT to a free port in $EnvFile, then run this again."
        }
    }
    $text = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot $EnvFile))
    Write-TextFile $EnvFile ($text.TrimEnd() + "`n`n# Port of the app on this computer, chosen at the first start`nAPP_PORT=$port`n")
}
elseif ((-not $alreadyRunning) -and (Test-PortInUse ([int]$port))) {
    Stop-WithError "Port $port is used by another program. Close that program, or set APP_PORT to another port in $EnvFile, then run this again."
}
$url = "http://127.0.0.1:$port"
$prePath = Get-EnvValue 'PRE_PATH'


Write-Step 'Downloading DataGatherer (the first time takes a few minutes)'
Invoke-Compose pull --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Step 'Download not possible: building DataGatherer on this computer instead (10 to 20 minutes)'
    Invoke-Compose build
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError 'Docker could not build DataGatherer. The messages above say why; send them to whoever maintains the app.'
    }
}

Write-Step 'Starting DataGatherer'
Invoke-Compose up -d
if ($LASTEXITCODE -ne 0) {
    Stop-WithError 'Docker could not start DataGatherer. The messages above say why; send them to whoever maintains the app.'
}


Write-Step 'Waiting for DataGatherer to be ready'
$ready = $false
for ($i = 0; $i -lt 150; $i++) {
    try {
        Invoke-WebRequest -Uri "$url/${prePath}a/admin/login/" -UseBasicParsing -TimeoutSec 5 | Out-Null
        $ready = $true
        break
    }
    catch { Start-Sleep -Seconds 2 }
}
if (-not $ready) {
    Invoke-Compose logs --tail 40 django
    Stop-WithError 'DataGatherer did not start. The messages above say why; send them to whoever maintains the app.'
}


Write-Step "DataGatherer is running at $url"
if ($firstStart) {
    Write-Host "Administrator account (also saved in $EnvFile):"
    Write-Host "  user:      $(Get-EnvValue 'DJANGO_SUPERUSER_USERNAME')"
    Write-Host "  password:  $(Get-EnvValue 'DJANGO_SUPERUSER_PASSWORD')"
}
else {
    Write-Host "Log in with your account. The administrator password chosen at the first start is"
    Write-Host "DJANGO_SUPERUSER_PASSWORD in $EnvFile."
}
Write-Host "Create accounts for other people at $url/${prePath}a/admin/"
Write-Host 'To stop DataGatherer double-click stop.bat. Your data is kept.'

if (-not $NoBrowser) { Start-Process $url }
