param(
    [string]$CalendarPath = ".\calendars"
)

# Farben für Ausgabe
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Calendar Plugin Export Fixer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob Verzeichnis existiert
if (-not (Test-Path $CalendarPath)) {
    Write-Host "ERROR: Directory not found: $CalendarPath" -ForegroundColor Red
    exit 1
}

# Alle .py Dateien im Verzeichnis
$pythonFiles = Get-ChildItem -Path $CalendarPath -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" }

Write-Host "Found $($pythonFiles.Count) Python files to check" -ForegroundColor Yellow
Write-Host ""

foreach ($file in $pythonFiles) {
    Write-Host "Checking: $($file.Name)" -ForegroundColor White
    
    $content = Get-Content $file.FullName -Raw
    
    # Prüfe ob __all__ bereits existiert
    if ($content -match '__all__\s*=') {
        Write-Host "  ✓ Already has __all__ export" -ForegroundColor Green
        continue
    }
    
    # Finde den Klassennamen (sucht nach class XXXSensor)
    if ($content -match 'class\s+(\w+Sensor)\s*\(') {
        $className = $matches[1]
        Write-Host "  Found class: $className" -ForegroundColor Cyan
        
        # Finde CALENDAR_INFO
        $hasCalendarInfo = $content -match 'CALENDAR_INFO\s*='
        
        # Finde UPDATE_INTERVAL
        $hasUpdateInterval = $content -match 'UPDATE_INTERVAL\s*='
        
        # Erstelle Export-Liste
        $exports = @($className)
        if ($hasCalendarInfo) {
            $exports += "CALENDAR_INFO"
        }
        if ($hasUpdateInterval) {
            $exports += "UPDATE_INTERVAL"
        }
        
        # Formatiere die Export-Zeile
        $exportList = ($exports | ForEach-Object { "`"$_`"" }) -join ", "
        $exportStatement = "`n`n# Export the sensor class`n__all__ = [$exportList]"
        
        # Füge am Ende der Datei hinzu
        $newContent = $content.TrimEnd() + $exportStatement
        
        # Schreibe Datei zurück
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        
        Write-Host "  ✓ Added __all__ export: [$exportList]" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ No sensor class found - skipping" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Export fixing completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Zeige Zusammenfassung
Write-Host "`nSummary:" -ForegroundColor Yellow
$filesWithExport = Get-ChildItem -Path $CalendarPath -Filter "*.py" | Where-Object { 
    $_.Name -ne "__init__.py" -and (Get-Content $_.FullName -Raw) -match '__all__\s*='
}
Write-Host "Files with __all__ export: $($filesWithExport.Count)" -ForegroundColor Green

# Optional: Zeige alle Exporte
$showAll = Read-Host "`nShow all exports? (y/n)"
if ($showAll -eq 'y') {
    Write-Host "`nCurrent exports:" -ForegroundColor Cyan
    foreach ($file in $filesWithExport) {
        $content = Get-Content $file.FullName -Raw
        if ($content -match '__all__\s*=\s*\[(.*?)\]') {
            Write-Host "$($file.Name): $($matches[1])" -ForegroundColor White
        }
    }
}	