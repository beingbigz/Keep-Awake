; Keep Awake Installer Script
; Created with NSIS
;
; DESCRIPTION:
; This NSIS (Nullsoft Scriptable Install System) script creates a professional
; Windows installer for the Keep Awake application. When compiled, it generates
; a standalone installer executable that users can run to install Keep Awake
; on their Windows systems.

;
; IMPORTANT FILES TO EDIT/CHECK BEFORE COMPILING:
; 1. Line ~115-117 - Files to include in installer:
;    File "dist\KeepAwake.exe"     <- Main executable (REQUIRED)
;    File "LICENSE.txt"            <- License file (REQUIRED for license page)
;
; 2. Line ~25 - License file reference:
;    !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
;
; 3. Line ~170-172 - Files to remove during uninstall:
;    Delete $INSTDIR\KeepAwake.exe
;
; NOTE: If you add more files to install, remember to:
; - Add File "path\filename" commands in the main section
; - Add Delete $INSTDIR\filename commands in uninstall section
; - Ensure all referenced files exist before compiling

;--------------------------------
; General Attributes

Name "Keep Awake"
OutFile "KeepAwake_Installer.exe"
InstallDir "$PROGRAMFILES\Keep Awake"
InstallDirRegKey HKCU "Software\Keep Awake" "Install_Dir"
RequestExecutionLevel admin

;--------------------------------
; Interface Settings

!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Keep Awake"
VIAddVersionKey "Comments" "Keep your computer awake"
VIAddVersionKey "CompanyName" "Keep Awake Software"
VIAddVersionKey "LegalCopyright" "© 2025"
VIAddVersionKey "FileDescription" "Keep Awake Application"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
VIAddVersionKey "InternalName" "KeepAwake"
VIAddVersionKey "LegalTrademarks" ""
VIAddVersionKey "OriginalFilename" "KeepAwake.exe"

;--------------------------------
; Installer Sections

Section "Keep Awake (required)" SecMain

  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath $INSTDIR
  
  ; Put files there
  File "dist\KeepAwake.exe"
  
  ; Write the installation path into the registry
  WriteRegStr HKCU "Software\Keep Awake" "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "DisplayName" "Keep Awake"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "NoRepair" 1
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "DisplayVersion" "1.0.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "Publisher" "Keep Awake Software"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "DisplayIcon" "$INSTDIR\KeepAwake.exe"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake" "EstimatedSize" 2048
  
  WriteUninstaller "uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts" SecStartMenu

  CreateDirectory "$SMPROGRAMS\Keep Awake"
  CreateShortcut "$SMPROGRAMS\Keep Awake\Keep Awake.lnk" "$INSTDIR\KeepAwake.exe"
  CreateShortcut "$SMPROGRAMS\Keep Awake\Uninstall.lnk" "$INSTDIR\uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Desktop Shortcut" SecDesktop

  CreateShortcut "$DESKTOP\Keep Awake.lnk" "$INSTDIR\KeepAwake.exe"

SectionEnd

;--------------------------------
; Descriptions

; Language strings
LangString DESC_SecMain ${LANG_ENGLISH} "The main Keep Awake application."
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create shortcuts in the Start Menu."
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a shortcut on the Desktop."

; Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Keep Awake"
  DeleteRegKey HKCU "Software\Keep Awake"
  
  ; Remove files and uninstaller
  Delete $INSTDIR\KeepAwake.exe
  Delete $INSTDIR\uninstall.exe
  
  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Keep Awake\*.*"
  Delete "$DESKTOP\Keep Awake.lnk"
  Delete "$SMSTARTUP\Keep Awake.lnk"
  
  ; Remove directories used
  RMDir "$SMPROGRAMS\Keep Awake"
  RMDir "$INSTDIR"

SectionEnd

;--------------------------------
; Functions

Function .onInit
  ; Check if application is already running
  System::Call 'kernel32::CreateMutexA(i 0, i 0, t "KeepAwakeInstaller") i .r1 ?e'
  Pop $R0
  StrCmp $R0 0 +3
    MessageBox MB_OK|MB_ICONEXCLAMATION "The installer is already running."
    Abort

  ; Check for existing installation
  ReadRegStr $R0 HKCU "Software\Keep Awake" "Install_Dir"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "Keep Awake is already installed. $\n$\nClick 'OK' to remove the \
  previous version or 'Cancel' to cancel this upgrade." \
  IDOK uninst
  Abort

  ; Run the uninstaller
  uninst:
    ClearErrors
    ExecWait '$R0\uninstall.exe _?=$R0'
    
    IfErrors no_remove_uninstaller done
      ; You can either use Delete /REBOOTOK in the uninstaller or add some code
      ; here to remove the uninstaller. Use a registry key to check
      ; whether the user has chosen to uninstall. If you are using an uninstaller
      ; components page, make sure all sections are uninstalled.
    no_remove_uninstaller:
  
  done:
FunctionEnd
