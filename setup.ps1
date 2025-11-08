$ErrorActionPreference = "Stop"

Write-Host "Setting up Screendibs development environment..." -ForegroundColor Green

# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv backend\.venv
. backend\.venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

# Create example environment files if they don't exist
Write-Host "Setting up environment files..." -ForegroundColor Yellow
if (-not(Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
    Write-Host "Created backend/.env from example file. Please update with your actual values." -ForegroundColor Yellow
}

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
Set-Location backend
alembic upgrade head
Set-Location ..

Write-Host "`nSetup completed!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. Update backend/.env with your actual configuration values"
Write-Host "2. Start the backend server: cd backend && uvicorn app.main:app --reload"
Write-Host "3. Start the frontend development server: cd frontend && npm run dev"