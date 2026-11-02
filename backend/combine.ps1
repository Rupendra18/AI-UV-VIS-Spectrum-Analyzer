$files = @(
    "requirements.txt",
    "app.py",
    "templates\base.html",
    "templates\login.html",
    "templates\dashboard.html",
    "templates\reports.html",
    "templates\history.html",
    "templates\settings.html",
    "static\css\style.css",
    "static\js\script.js"
)

$outPath = "c:\Users\rukku\OneDrive\Desktop\AI_Spectrum_Analyzer_All_Code.txt"
if (Test-Path $outPath) { Remove-Item $outPath }

foreach ($file in $files) {
    Add-Content $outPath "================================================================"
    Add-Content $outPath "FILE: $file"
    Add-Content $outPath "================================================================"
    Get-Content "c:\Users\rukku\OneDrive\Desktop\New folder\$file" | Add-Content $outPath
    Add-Content $outPath "`n`n"
}
