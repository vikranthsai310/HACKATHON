# Quick Start Commands for Windows PowerShell

# Install dependencies
function Install-Dependencies {
    pip install -r requirements.txt
}

# Run unit tests
function Test-Phase1 {
    pytest test_phase1.py -v
}

# Run full system test
function Test-System {
    python test_system.py
}

# Start API server
function Start-Server {
    python -m app.main
}

# Start with auto-reload (development)
function Start-Dev {
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Clean cache files
function Clean-Cache {
    Get-ChildItem -Path . -Include __pycache__,*.pyc,*.pyo,.pytest_cache -Recurse -Force | Remove-Item -Recurse -Force
}

# Format code
function Format-Code {
    black app/ --line-length=120
}

# Show help
function Show-Help {
    Write-Host "Available commands:"
    Write-Host "  Install-Dependencies  - Install all dependencies"
    Write-Host "  Test-Phase1          - Run unit tests"
    Write-Host "  Test-System          - Run full system test"
    Write-Host "  Start-Server         - Start API server"
    Write-Host "  Start-Dev            - Start with auto-reload"
    Write-Host "  Clean-Cache          - Clean cache files"
    Write-Host "  Format-Code          - Format code with black"
}

# Export functions
Export-ModuleMember -Function Install-Dependencies, Test-Phase1, Test-System, Start-Server, Start-Dev, Clean-Cache, Format-Code, Show-Help

Write-Host ""
Write-Host "HRM Decision System - PowerShell Commands Loaded" -ForegroundColor Green
Write-Host "Type 'Show-Help' to see available commands" -ForegroundColor Cyan
Write-Host ""
