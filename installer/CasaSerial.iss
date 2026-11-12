; CasaSerial Windows installer (Inno Setup 6)
; Build: build_setup.bat  (builds WIN\CasaSerial with PyInstaller, then compiles this script)

#ifndef AppVersion
  #define AppVersion "0.01.211"
#endif
#define AppName "CasaSerial"
#define AppExe "CasaSerial.exe"

[Setup]
; 이 GUID는 업그레이드/제거 시 같은 앱으로 인식하는 데 쓰이므로 바꾸지 않는다.
AppId={{00EF2E01-0909-4549-9BAB-F9930E4ACEF7}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=CasaSerial
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\WIN\Setup
OutputBaseFilename=CasaSerial_Setup_{#AppVersion}
SetupIconFile=..\image\CasaSerial.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; 관리자 권한 없이 사용자 폴더에 설치하는 것이 기본이다. 설치 시 모든 사용자용 설치도 선택할 수 있다.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\WIN\CasaSerial\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
