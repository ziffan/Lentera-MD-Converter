; Inno Setup Script — Lentera MD
; Installer untuk Windows 10/11
;
; Prasyarat:
;   1. Inno Setup 6 (https://jrsoftware.org/isdl.php)
;   2. Build PyInstaller terlebih dahulu:
;        python build_app.py --onedir
;      Output ada di: dist\windows\LenteraMD\
;
; Cara pakai:
;   - Klik kanan lentera_md_setup.iss → Compile (Inno Setup IDE)
;   - Atau dari command line: iscc lentera_md_setup.iss
;   - Output: installer\windows\Output\LenteraMD_Setup_1.0.0.exe

#define AppName      "Lentera MD"
#define AppExeName   "LenteraMD.exe"
#define AppVersion   "1.0.0"
#define AppPublisher "Lentera MD Team"
#define AppURL       "https://github.com/ziffan/Lentera-MD-Converter"
#define AppDesc      "Konversi dokumen hukum Indonesia ke Markdown"

; Path relatif dari lokasi .iss ini ke root proyek (dua folder ke atas)
#define RootDir      "..\.."
#define BuildDir     RootDir + "\dist\windows\LenteraMD"
#define IconFile     RootDir + "\assets\icons\app_icon.ico"
#define LogoFile     RootDir + "\assets\logo.png"

[Setup]
AppId={{7E9F4A2B-3C1D-4E8F-A5B6-2D3E4F5A6B7C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile={#RootDir}\LICENSE
OutputDir=Output
OutputBaseFilename=LenteraMD_Setup_{#AppVersion}
SetupIconFile={#IconFile}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=120
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

; Gambar wizard (opsional — komentari jika tidak ada)
; WizardImageFile={#LogoFile}
; WizardSmallImageFile={#LogoFile}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Buat ikon di Desktop";        GroupDescription: "Pintasan:"; Flags: unchecked
Name: "quicklaunch";    Description: "Buat ikon Quick Launch";       GroupDescription: "Pintasan:"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Seluruh isi folder build PyInstaller
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Hapus {#AppName}";        Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunch

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Jalankan {#AppName} sekarang"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\Lentera-MD-Team"

[Code]
// Cek apakah Windows 10 ke atas
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then
  begin
    MsgBox('Lentera MD membutuhkan Windows 10 atau lebih baru.', mbError, MB_OK);
    Result := False;
  end else
    Result := True;
end;
