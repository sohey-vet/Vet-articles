@echo off
cd /d "%~dp0"
echo ==========================================
echo VetEvidence SNS Draft Extractor
echo ==========================================
python extract_drafts.py
pause
