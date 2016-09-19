!define PRODUCT_NAME "AutoAPT"
!define PRODUCT_VERSION "0.900.B"
!define PY_VERSION "3.5.2"
!define PY_MAJOR_VERSION "3.5"
!define BITNESS "64"
!define ARCH_TAG ".amd64"
!define INSTALLER_NAME "AutoAPT_0.900.B.exe"
!define PRODUCT_ICON "isl-trans.ico"
 
SetCompressor lzma

RequestExecutionLevel admin

; Modern UI installer stuff 
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

; UI pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES${BITNESS}\${PRODUCT_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

!addplugindir c:\python35\lib\site-packages\nsist
!include windowsversion.nsh
!include x64.nsh

Section "-msvcrt"
  ${GetWindowsVersion} $R0

  StrCpy $0 "--"

  ${If} ${RunningX64}
    ${If} $R0 == "8.1"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows8.1-KB2999226-x64.msu"
    ${ElseIf} $R0 == "8"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows8-RT-KB2999226-x64.msu"
    ${ElseIf} $R0 == "7"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows6.1-KB2999226-x64.msu"
    ${ElseIf} $R0 == "Vista"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows6-KB2999226-x64.msu"
    ${EndIf}
  ${Else}
    ${If} $R0 == "8.1"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows8.1-KB2999226-x86.msu"
    ${ElseIf} $R0 == "8"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows8-RT-KB2999226-x86.msu"
    ${ElseIf} $R0 == "7"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows6.1-KB2999226-x86.msu"
    ${ElseIf} $R0 == "Vista"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows6-KB2999226-x86.msu"
    ${EndIf}
  ${EndIf}

  IfFileExists "$SYSDIR\ucrtbase.dll" skip_msvcrt
  StrCmp $0 "--" skip_msvcrt

  DetailPrint "Need to install MSVCRT 2015. This may take a few minutes."
  DetailPrint "Downloading $0"
  inetc::get /RESUME "" "$0" "$INSTDIR\msvcrt.msu"
  Pop $2
  DetailPrint "Download finished ($2)"
  ${If} $2 == "OK"
    DetailPrint "Running wusa to install update package"
    ExecWait 'wusa "$INSTDIR\msvcrt.msu" /quiet /norestart' $1
    Delete "$INSTDIR\msvcrt.msu"
  ${Else}
    MessageBox MB_OK "Failed to download important update! \
            ${PRODUCT_NAME} will not run until you install the Visual C++ \
            redistributable for Visual Studio 2015.\
            $\n$\nhttp://www.microsoft.com/en-us/download/details.aspx?id=48145"
  ${EndIf}

  # This WUSA exit code means a reboot is needed.
  ${If} $1 = 0x00240005
    SetRebootFlag true
  ${EndIf}

  skip_msvcrt:
SectionEnd


Section "!${PRODUCT_NAME}" sec_app
  SectionIn RO
  SetShellVarContext all
  File ${PRODUCT_ICON}
  SetOutPath "$INSTDIR\pkgs"
  File /r "pkgs\*.*"
  SetOutPath "$INSTDIR"
  
  ; Install files
    SetOutPath "$INSTDIR"
      File "AutoAPT.launch.py"
      File "isl-trans.ico"
  
  ; Install directories
    SetOutPath "$INSTDIR\Python"
    File /r "Python\*.*"
    SetOutPath "$INSTDIR\demo_setup_files"
    File /r "demo_setup_files\*.*"
  
  ; Install shortcuts
  ; The output path becomes the working directory for shortcuts
  SetOutPath "%HOMEDRIVE%\%HOMEPATH%"
    CreateShortCut "$SMPROGRAMS\AutoAPT.lnk" "$INSTDIR\Python\python.exe" \
      '"$INSTDIR\AutoAPT.launch.py"' "$INSTDIR\isl-trans.ico"
  SetOutPath "$INSTDIR"

  
  ; Byte-compile Python files.
  DetailPrint "Byte-compiling Python modules..."
  nsExec::ExecToLog '"$INSTDIR\Python\python" -m compileall -q "$INSTDIR\pkgs"'
  WriteUninstaller $INSTDIR\uninstall.exe
  ; Add ourselves to Add/remove programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoRepair" 1

  ; Check if we need to reboot
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
                /SD IDNO IDNO noreboot
      Reboot
  noreboot:
SectionEnd

Section "Uninstall"
  SetShellVarContext all
  Delete $INSTDIR\uninstall.exe
  Delete "$INSTDIR\${PRODUCT_ICON}"
  RMDir /r "$INSTDIR\pkgs"

  ; Remove ourselves from %PATH%

  ; Uninstall files
    Delete "$INSTDIR\AutoAPT.launch.py"
    Delete "$INSTDIR\isl-trans.ico"
  ; Uninstall directories
    RMDir /r "$INSTDIR\Python"
    RMDir /r "$INSTDIR\demo_setup_files"
  ; Uninstall shortcuts
      Delete "$SMPROGRAMS\AutoAPT.lnk"
  RMDir $INSTDIR
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd



; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:${PRODUCT_NAME}"
    
FunctionEnd