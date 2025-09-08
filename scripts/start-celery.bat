@echo off
echo Starting Celery Worker...
cd /d "%~dp0..\backend"
celery -A app.celery_app worker --loglevel=info --concurrency=2