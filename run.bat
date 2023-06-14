@ECHO off
ECHO Hey developer!
ECHO Welcome To KarmalegoWeb

start "Flask Web Server" ECHO Starting Flask Web Server ^& python application.py ^& pause ^& EXIT 0

start "Celery Task Queue"  ECHO Starting Celery Task Queue ^& celery -A celery_worker.celery worker --pool=solo ^& pause ^& EXIT 0

start "Docker - Redis Message Broker" ECHO Docker - Redis Message Broker ^& docker run -d -p 6379:6379 redis ^& pause ^& EXIT 0

@REM start "React Server" ^ ECHO Starting React Server ^& cd ..\KarmaLegoFrontend ^&^& npm start ^& pause ^& EXIT 0
