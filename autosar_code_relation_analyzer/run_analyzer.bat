@echo off
setlocal

REM Windows launcher for autosar_code_relation_analyzer
REM Example (double click or terminal):
REM run_analyzer.bat --src .\src --output .\code_relation.drawio --report .\code_relation_report.md

python run_analyzer.py %*
if errorlevel 1 (
  echo Analyzer failed.
  exit /b 1
)

echo Analyzer finished.
exit /b 0
