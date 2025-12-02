# 🔧 AUTOMATED CELERY ERROR FIX SCRIPT
# Copy and paste this ENTIRE script into PowerShell (Run as Administrator)
# File: FIX_CELERY_ERRORS.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HMIP-2026 Celery Error Auto-Fix" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "C:\Users\ratan\HMIP-2026\backend"

# Check if backend directory exists
if (-Not (Test-Path $backendPath)) {
    Write-Host "✗ Backend directory not found!" -ForegroundColor Red
    exit
}

Set-Location $backendPath
Write-Host "✓ Changed to backend directory" -ForegroundColor Green
Write-Host ""

# ============================================
# Step 1: Activate Virtual Environment
# ============================================
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv\Scripts\activate.ps1") {
    & "venv\Scripts\activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Run: python -m venv venv" -ForegroundColor Yellow
    exit
}

Write-Host ""

# ============================================
# Step 2: Install Missing Packages
# ============================================
Write-Host "Step 2: Installing missing packages..." -ForegroundColor Yellow

$packages = @("python-decouple", "twilio")

foreach ($package in $packages) {
    Write-Host "  Installing $package..." -ForegroundColor Gray
    pip install $package --quiet
}

Write-Host "✓ Packages installed" -ForegroundColor Green
Write-Host ""

# ============================================
# Step 3: Fix Djongo Issue
# ============================================
Write-Host "Step 3: Fixing Djongo compatibility issue..." -ForegroundColor Yellow

$fixDjongo = Read-Host "Uninstall djongo and use SQLite? (y/n)"

if ($fixDjongo -eq "y") {
    Write-Host "  Uninstalling djongo..." -ForegroundColor Gray
    pip uninstall djongo -y --quiet
    Write-Host "✓ Djongo removed" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "  IMPORTANT: You need to update settings.py manually!" -ForegroundColor Yellow
    Write-Host "  Replace DATABASES section with:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  DATABASES = {" -ForegroundColor Cyan
    Write-Host "      'default': {" -ForegroundColor Cyan
    Write-Host "          'ENGINE': 'django.db.backends.sqlite3'," -ForegroundColor Cyan
    Write-Host "          'NAME': BASE_DIR / 'db.sqlite3'," -ForegroundColor Cyan
    Write-Host "      }" -ForegroundColor Cyan
    Write-Host "  }" -ForegroundColor Cyan
    Write-Host ""
    
    $openSettings = Read-Host "Open settings.py now? (y/n)"
    if ($openSettings -eq "y") {
        notepad "hmip_backend\settings.py"
        Write-Host "  Waiting for you to save settings.py..." -ForegroundColor Yellow
        Read-Host "Press Enter when done"
    }
}

Write-Host ""

# ============================================
# Step 4: Create Missing URL Files
# ============================================
Write-Host "Step 4: Creating missing URL files..." -ForegroundColor Yellow

# Create permissions/urls.py
$permissionsUrls = @"
from django.urls import path

app_name = 'permissions'

urlpatterns = [
    # Add permission endpoints here
]
"@

# Create location/urls.py
$locationUrls = @"
from django.urls import path

app_name = 'location'

urlpatterns = [
    # Add location endpoints here
]
"@

# Create ai_engine/urls.py
$aiUrls = @"
from django.urls import path

app_name = 'ai_engine'

urlpatterns = [
    # Add AI endpoints here
]
"@

# Create notifications/urls.py
$notificationsUrls = @"
from django.urls import path

app_name = 'notifications'

urlpatterns = [
    # Add notification endpoints here
]
"@

# Write files
$permissionsUrls | Out-File -FilePath "apps\permissions\urls.py" -Encoding UTF8
$locationUrls | Out-File -FilePath "apps\location\urls.py" -Encoding UTF8
$aiUrls | Out-File -FilePath "apps\ai_engine\urls.py" -Encoding UTF8
$notificationsUrls | Out-File -FilePath "apps\notifications\urls.py" -Encoding UTF8

Write-Host "✓ Created apps/permissions/urls.py" -ForegroundColor Green
Write-Host "✓ Created apps/location/urls.py" -ForegroundColor Green
Write-Host "✓ Created apps/ai_engine/urls.py" -ForegroundColor Green
Write-Host "✓ Created apps/notifications/urls.py" -ForegroundColor Green

Write-Host ""

# ============================================
# Step 5: Run Django Checks
# ============================================
Write-Host "Step 5: Running Django system checks..." -ForegroundColor Yellow

python manage.py check

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Django checks passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Django checks failed!" -ForegroundColor Red
    Write-Host "  Please fix the errors above before running Celery" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 6: Run Migrations (Optional)
# ============================================
$runMigrations = Read-Host "Run migrations now? (y/n)"

if ($runMigrations -eq "y") {
    Write-Host "  Running makemigrations..." -ForegroundColor Gray
    python manage.py makemigrations
    
    Write-Host "  Running migrate..." -ForegroundColor Gray
    python manage.py migrate
    
    Write-Host "✓ Migrations complete" -ForegroundColor Green
}

Write-Host ""

# ============================================
# Summary
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fix Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "What was fixed:" -ForegroundColor Cyan
Write-Host "  ✓ Installed python-decouple" -ForegroundColor Green
Write-Host "  ✓ Installed twilio" -ForegroundColor Green
Write-Host "  ✓ Created missing URL files" -ForegroundColor Green
if ($fixDjongo -eq "y") {
    Write-Host "  ✓ Removed djongo" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Make sure settings.py uses SQLite (not djongo)" -ForegroundColor Gray
Write-Host "  2. Run: python manage.py runserver" -ForegroundColor Gray
Write-Host "  3. Run: celery -A hmip_backend worker -l info" -ForegroundColor Gray

Write-Host ""
Write-Host "Try running Celery now? (y/n)" -ForegroundColor Yellow
$tryCelery = Read-Host

if ($tryCelery -eq "y") {
    Write-Host ""
    Write-Host "Starting Celery worker..." -ForegroundColor Yellow
    celery -A hmip_backend worker --loglevel=info
}