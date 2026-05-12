# Packaging The Address Enrichment App

Use this when the app needs to run on computers where Python may not be installed.

## Recommended Distribution

Build a standalone executable with PyInstaller:

- Build on macOS to create a macOS app/binary.
- Build on Windows to create a Windows `.exe`.
- Build on Linux to create a Linux binary.

PyInstaller packages Python and the required libraries into the app. End users do not need to install Python, `openpyxl`, or any command-line tools.

## Build On macOS Or Linux

```bash
cd "/path/to/address-enrichment-example"
chmod +x build_mac_or_linux.sh
./build_mac_or_linux.sh
```

The output is created under:

```text
dist/AddressEnrichment
```

## Build On Windows

Open PowerShell in the project folder:

```powershell
.\build_windows.ps1
```

The outputs are created under:

```text
dist\AddressEnrichment.exe
dist\AddressEnrichment-windows.zip
```

The zip contains:

- `AddressEnrichment.exe`
- `.env.example`
- `example_addresses.xlsx`
- `README.txt`

## Build Windows With GitHub Actions

If the project is pushed to GitHub, use the included workflow:

```text
.github/workflows/build-windows.yml
```

Steps:

1. Push this folder to a GitHub repository.
2. Open the repository on GitHub.
3. Go to **Actions**.
4. Select **Build Windows App**.
5. Click **Run workflow**.
6. Download the `AddressEnrichment-windows` artifact from the completed run.

This is the easiest way to produce a Windows `.exe` without owning or configuring a Windows computer.

## API Key Setup For End Users

Users can paste the Google Places API key into the app and click **Save Key**.

For managed distribution, you can also ship a `.env` file next to the executable:

```text
GOOGLE_PLACES_API_KEY=your-api-key
```

Do not commit `.env` to git.

## User Workflow

1. Open `AddressEnrichment`.
2. Choose an input `.xlsx` or `.csv` file.
3. Choose an output `.xlsx` file.
4. Paste and save the Google Places API key if needed.
5. Use these defaults for richer cold-calling results:
   - Provider: `google`
   - Field preset: `contact`
   - Search strategy: `expanded`
   - Max matches per address: `5`
6. Run 25 rows first, review the output, then uncheck the test limit for the full file.

## Important Limitation

A standalone executable is operating-system-specific. One file cannot run unchanged on macOS, Windows, and Linux. Build one artifact per target operating system.

PyInstaller does not reliably cross-compile Windows executables from macOS. Use a Windows machine or the GitHub Actions workflow for the Windows build.
