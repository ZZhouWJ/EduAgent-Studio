$env:SERVER_PORT='8002'
$env:APP_ENV='development'
Start-Process -FilePath 'E:\DatabaseManagementPractice\AI-Collab-Audit-System\backend\.venv\Scripts\python.exe' -ArgumentList 'run.py' -WorkingDirectory 'E:\DatabaseManagementPractice\AI-Collab-Audit-System\backend'
Start-Sleep -Seconds 3
netstat -ano | findstr :8002
