@echo off
color 5

python update.py
 
timeout /t 20

python builder.pyw
