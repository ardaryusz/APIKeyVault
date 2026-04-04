@echo off
title API Key Vault Setup Manager

rem --- Enable ANSI colors in Windows terminal ---
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

rem --- Define Colors ---
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "CYAN=%ESC%[36m"
set "YELLOW=%ESC%[33m"
set "RESET=%ESC%[0m"

:menu
cls
echo %CYAN%====================================%RESET%
echo %CYAN%      API Key Vault Setup Manager%RESET%
echo %CYAN%====================================%RESET%
echo.
echo Please choose an option:
echo %GREEN%1. Install Key Vault%RESET%
echo %YELLOW%2. Standard Uninstall (Keeps your vault data)%RESET%
echo %RED%3. Full Uninstall (Deletes program AND your vault data)%RESET%
echo.

set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto uninstall_std
if "%choice%"=="3" goto uninstall_full

echo.
echo %RED%[-] Invalid choice. Please try again.%RESET%
timeout /t 2 >nul
goto menu

:install
echo.
echo %CYAN%[*] Installing API Key Vault...%RESET%
echo.
pip install -e .
echo.
echo %GREEN%[+] Installation complete! You can now type 'keyvault' anywhere in your terminal.%RESET%
goto end

:uninstall_std
echo.
echo %YELLOW%[*] Performing Standard Uninstall...%RESET%
echo.
pip uninstall keyvault -y
echo.
echo %GREEN%[+] Uninstallation complete! The 'keyvault' command has been removed.%RESET%
echo %CYAN%[*] Your encrypted vault data in %%USERPROFILE%%\apivault was safely kept.%RESET%
goto end

:uninstall_full
echo.
echo %RED%[!!!] WARNING: FULL UNINSTALL [!!!]%RESET%
echo %YELLOW%This will remove the program AND permanently delete your encrypted vault and all API keys.%RESET%
set /p confirm="Are you absolutely sure? (y/n): "

rem /i makes the check case-insensitive so 'Y' or 'y' works
if /i not "%confirm%"=="y" (
    echo.
    echo %CYAN%[*] Full uninstall cancelled. Going back to menu...%RESET%
    timeout /t 2 >nul
    goto menu
)

echo.
echo %RED%[*] Uninstalling program...%RESET%
pip uninstall keyvault -y

echo.
echo %RED%[*] Erasing vault data...%RESET%
rem Check if the folder exists, then delete it and everything inside quietly
if exist "%USERPROFILE%\apivault" (
    rmdir /s /q "%USERPROFILE%\apivault"
    echo %GREEN%[+] Vault data completely erased.%RESET%
) else (
    echo %YELLOW%[*] No vault data found to delete.%RESET%
)

echo.
echo %GREEN%[+] Full Uninstallation complete!%RESET%
goto end

:end
echo.
set /p dummy="%CYAN%Press Enter to close...%RESET%"