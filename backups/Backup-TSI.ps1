
# ============================================================
# Taidu Selling Intelligence
# Respaldo PostgreSQL en Render
# Compatible con Windows PowerShell 5.1
# Retencion: 7 dias
# ============================================================

$ErrorActionPreference = "Stop"

$DbHost = "dpg-dbc3vhgn74is73fa0jvg-a.oregon-postgres.render.com"
$DbPort = "5432"
$DbName = "taidu_1e9u"
$DbUser = "taidu_user"

$Base = "C:\DEV\TSI\backups"
$LogDir = Join-Path $Base "logs"
$PgBin = "C:\Program Files\PostgreSQL\18\bin"
$PgDump = Join-Path $PgBin "pg_dump.exe"
$PgRestore = Join-Path $PgBin "pg_restore.exe"
$PgPass = Join-Path $env:APPDATA "postgresql\pgpass.conf"

New-Item -ItemType Directory -Force -Path $Base, $LogDir |
    Out-Null

$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "backup_$Stamp.log"
$TempFile = Join-Path $Base "TSI_$Stamp.partial"
$BackupFile = Join-Path $Base "TSI_$Stamp.dump"
$DumpErrorFile = Join-Path $LogDir "pg_dump_$Stamp.log"

function Write-Log {
    param([string]$Message)
    Add-Content -LiteralPath $LogFile -Encoding UTF8 `
        -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
}

$ExitCode = 1

try {
    if (!(Test-Path $PgDump)) {
        throw "No se encuentra pg_dump.exe: $PgDump"
    }

    if (!(Test-Path $PgRestore)) {
        throw "No se encuentra pg_restore.exe: $PgRestore"
    }

    if (!(Test-Path $PgPass)) {
        throw "No se encuentra pgpass.conf."
    }

    $env:PGPASSFILE = $PgPass
    $env:PGSSLMODE = "require"
    $env:PGCONNECT_TIMEOUT = "30"

    Write-Log "Inicio del respaldo: $DbName"
    Write-Host "Iniciando respaldo de $DbName..."

    # Crear un proceso independiente para evitar que
    # PowerShell 5.1 interprete stderr como una excepcion.
    $Arguments = @(
        "--host=$DbHost"
        "--port=$DbPort"
        "--username=$DbUser"
        "--dbname=$DbName"
        "--format=custom"
        "--no-owner"
        "--no-privileges"
        "--verbose"
        "--file=$TempFile"
    )

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $PgDump
    $StartInfo.Arguments = ($Arguments -join " ")
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo

    [void]$Process.Start()

    $StdOutTask = $Process.StandardOutput.ReadToEndAsync()
    $StdErrTask = $Process.StandardError.ReadToEndAsync()

    $Process.WaitForExit()

    $StdOut = $StdOutTask.Result
    $StdErr = $StdErrTask.Result
    $DumpCode = $Process.ExitCode

    $Process.Dispose()

    if ($StdOut) {
        Add-Content -LiteralPath $DumpErrorFile -Value $StdOut
    }

    if ($StdErr) {
        Add-Content -LiteralPath $DumpErrorFile -Value $StdErr
        foreach ($Line in ($StdErr -split "`r?`n")) {
            if ($Line.Trim()) {
                Write-Log "pg_dump: $Line"
            }
        }
    }

    Write-Log "Codigo de salida de pg_dump: $DumpCode"

    if ($DumpCode -ne 0) {
        throw "pg_dump fallo con codigo $DumpCode. Revisa $DumpErrorFile"
    }

    if (!(Test-Path $TempFile)) {
        throw "pg_dump no genero el archivo temporal."
    }

    if ((Get-Item $TempFile).Length -le 0) {
        throw "El archivo de respaldo esta vacio."
    }

    Write-Host "Validando el respaldo..."

    $RestoreOutput = & $PgRestore --list $TempFile 2>&1
    $RestoreCode = $LASTEXITCODE

    if ($RestoreCode -ne 0) {
        foreach ($Line in $RestoreOutput) {
            Write-Log "pg_restore: $Line"
        }
        throw "La validacion de pg_restore fallo."
    }

    Move-Item -LiteralPath $TempFile -Destination $BackupFile -Force

    $SizeBytes = (Get-Item $BackupFile).Length
    $SizeMB = [math]::Round($SizeBytes / 1MB, 3)

    Write-Log "RESPALDO VALIDADO: $BackupFile"
    Write-Log "Tamano: $SizeBytes bytes"
    Write-Log "Proceso finalizado correctamente."

    # Retener siete dias; solo eliminar despues de un
    # respaldo nuevo y validado.
    $Cutoff = (Get-Date).AddDays(-7)

    Get-ChildItem $Base -Filter "TSI_*.dump" -File |
        Where-Object { $_.LastWriteTime -lt $Cutoff } |
        ForEach-Object {
            Write-Log "Eliminando respaldo antiguo: $($_.Name)"
            Remove-Item -LiteralPath $_.FullName -Force
        }

    Write-Host ""
    Write-Host "RESPALDO EXITOSO" -ForegroundColor Green
    Write-Host "Archivo: $BackupFile"
    Write-Host "Tamano: $SizeMB MB"
    Write-Host "Registro: $LogFile"

    $ExitCode = 0
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"

    Write-Host ""
    Write-Host "ERROR EN EL RESPALDO" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host "Registro: $LogFile"

    Remove-Item -LiteralPath $TempFile `
        -Force -ErrorAction SilentlyContinue
}
finally {
    Remove-Item Env:\PGPASSFILE -ErrorAction SilentlyContinue
    Remove-Item Env:\PGSSLMODE -ErrorAction SilentlyContinue
    Remove-Item Env:\PGCONNECT_TIMEOUT -ErrorAction SilentlyContinue
}

exit $ExitCode
