# C:\DEV\TSI\backups\Setup-Credentials.ps1
$ErrorActionPreference = "Stop"

# Datos de conexion PostgreSQL en Render
$hostName = "dpg-dbc3vhgn74is73fa0jvg-a.oregon-postgres.render.com"
$port = "5432"
$db = "taidu_1e9u"
$user = "taidu_user"

$securePassword = Read-Host "Introduce la contraseña PostgreSQL de Render" -AsSecureString
$password = [System.Net.NetworkCredential]::new("", $securePassword).Password

if ($password.Contains("`n") -or $password.Contains("`r")) {
    throw "La contraseña contiene un salto de linea no compatible con pgpass.conf."
}

function Escape-PgPassField([string]$Value) {
    $Value = $Value.Replace('\', '\\')
    $Value = $Value.Replace(':', '\:')
    return $Value
}

$credDir = Join-Path $env:APPDATA "postgresql"
$pgpass = Join-Path $credDir "pgpass.conf"
New-Item -ItemType Directory -Force -Path $credDir | Out-Null

$line = (@($hostName, $port, $db, $user, $password) |
    ForEach-Object { Escape-PgPassField $_ }) -join ":"

[System.IO.File]::WriteAllText(
    $pgpass,
    $line + "`n",
    [System.Text.UTF8Encoding]::new($false)
)

# Restringir acceso al usuario actual de Windows
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
& icacls.exe $pgpass /inheritance:r /grant:r "${identity}:(R,W)" | Out-Null

if ($LASTEXITCODE -ne 0) {
    Remove-Item -LiteralPath $pgpass -Force -ErrorAction SilentlyContinue
    throw "No se pudieron configurar los permisos de pgpass.conf."
}

$password = $null
$line = $null
$securePassword = $null

Write-Host "Credenciales guardadas en: $pgpass"
Write-Host "La contraseña no se ha mostrado en pantalla."
