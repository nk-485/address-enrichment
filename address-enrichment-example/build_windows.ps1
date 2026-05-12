$ErrorActionPreference = "Stop"

python -m pip install -r requirements-build.txt
$env:PYINSTALLER_CONFIG_DIR = Join-Path (Get-Location) ".pyinstaller-cache"
python -m PyInstaller --clean --noconfirm address_enrichment_app.spec

$distFolder = "dist\AddressEnrichment-windows"
New-Item -ItemType Directory -Force -Path $distFolder | Out-Null
Copy-Item "dist\AddressEnrichment.exe" "$distFolder\AddressEnrichment.exe" -Force
Copy-Item ".env.example" "$distFolder\.env.example" -Force
Copy-Item "example_addresses.xlsx" "$distFolder\example_addresses.xlsx" -Force

@"
AddressEnrichment Windows

How to use:
1. Double-click AddressEnrichment.exe.
2. Choose an Excel or CSV input file.
3. Choose an output Excel file.
4. Paste the Google Places API key and click Save Key.
5. Run 25 rows first, review the output, then run the full file.

Recommended settings:
- Provider: google
- Field preset: contact
- Search strategy: expanded
- Max matches per address: 5

The .env.example file shows the API key format. If you create a .env file in
this folder, the app will read it automatically.
"@ | Set-Content "$distFolder\README.txt"

Compress-Archive -Path $distFolder -DestinationPath "dist\AddressEnrichment-windows.zip" -Force

Write-Host ""
Write-Host "Built standalone app in:"
Write-Host "  dist\AddressEnrichment.exe"
Write-Host "  dist\AddressEnrichment-windows.zip"
Write-Host ""
Write-Host "Put a .env file next to the executable if you want to preconfigure the API key."
