# C:\DEV\TSI\backups\Register-BackupTask.ps1
# Ejecuta este script con la misma cuenta de Windows que creó pgpass.conf.
$ErrorActionPreference = "Stop"

$taskName = "TSI-Backup-PostgreSQL-Render"
$scriptPath = "C:\DEV\TSI\backups\Backup-TSI.ps1"

if (!(Test-Path -LiteralPath $scriptPath)) {
    throw "No se encuentra el script de respaldo: $scriptPath"
}

$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory "C:\DEV\TSI\backups"

$trigger = New-ScheduledTaskTrigger -Daily -At "22:00"

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Respaldo diario de PostgreSQL de TSI en Render" `
    -Force

Write-Host "Tarea '$taskName' registrada para ejecutarse diariamente a las 22:00."
Write-Host "Nota: la tarea debe ejecutarse bajo la misma cuenta de Windows que tiene pgpass.conf."
