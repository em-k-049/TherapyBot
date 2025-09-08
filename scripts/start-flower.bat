@echo off
echo Starting Flower Dashboard...
cd /d "%~dp0..\backend"
celery -A app.celery_app flower --port=5555