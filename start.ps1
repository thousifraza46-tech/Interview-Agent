Write-Host "🤖 Starting AI Interview Agent..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -eq 0 -or $env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow

$packages = @("streamlit", "openai", "sentence_transformers", "whisper", "edge_tts")
$missing = @()

foreach ($package in $packages) {
    $check = .\venv\Scripts\python.exe -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $package
    }
}

if ($missing.Count -gt 0) {
    Write-Host "❌ Missing packages: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "📥 Installing missing packages..." -ForegroundColor Yellow
    .\venv\Scripts\pip.exe install -r requirements.txt
} else {
    Write-Host "✅ All dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔑 Checking API configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
    
    $apiStatus = .\venv\Scripts\python.exe -c "from ai_engine import check_api_status; import json; print(json.dumps(check_api_status()))" | ConvertFrom-Json
    
    if ($apiStatus.status -eq "operational") {
        Write-Host "✅ OpenAI API connected - AI Mode ENABLED" -ForegroundColor Green
    } else {
        Write-Host "⚠️  OpenAI API issue: $($apiStatus.message)" -ForegroundColor Yellow
        Write-Host "📚 The system will use Standard Mode with curated questions" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "📚 The system will use Standard Mode" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To enable AI Mode:" -ForegroundColor White
    Write-Host "1. Create a .env file in this directory" -ForegroundColor White
    Write-Host "2. Add: OPENAI_API_KEY=your_api_key_here" -ForegroundColor White
}

Write-Host ""
Write-Host "🚀 Launching AI Interview Agent..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

.\venv\Scripts\python.exe -m streamlit run app.py

Write-Host ""
Write-Host "👋 AI Interview Agent stopped." -ForegroundColor Cyan
