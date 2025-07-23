[Setup]
AppName=Fiocruz Compras
AppVersion=1.0
DefaultDirName={commonpf}\Fiocruz_Compras
DefaultGroupName=Fiocruz Compras
OutputDir=.\instalador
OutputBaseFilename=Fiocruz_Compras_Instalador
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableDirPage=yes

[Files]
Source: "C:\Users\User\Desktop\Valdeir\Fiocruz_Compras\dist\Fiocruz_Compras\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{commondesktop}\Fiocruz Compras"; Filename: "{app}\Fiocruz_Compras.exe"

[Code]
function NeedsODBC(): Boolean;
begin
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 17 for SQL Server');
end;

function InitializeSetup(): Boolean;
begin
  MsgBox('Instalando o sistema Fiocruz Compras. Clique em OK para continuar.', mbInformation, MB_OK);
  Result := True;
end;

[Run]
Filename: "{app}\msodbcsql.msi"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando driver ODBC..."; Check: NeedsODBC

