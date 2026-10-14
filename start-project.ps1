
$Project = "C:\potato-disease"

# Start the FastAPI backend in a new PowerShell window
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "Set-Location '$Project'; .\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"
)

# Start the React frontend in the current terminal
Set-Location "$Project\frontend"
npm start
