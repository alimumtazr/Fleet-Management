# Fail-proof installation script for DBMS Ride Service Application

# Navigate to the project directory
cd DBMS-Project---Ride-Service-Application

# Check if virtual environment exists, create if not
if (-Not (Test-Path -Path ".\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    try {
        python -m venv venv
    }
    catch {
        Write-Host "Error creating virtual environment. Trying with python3..." -ForegroundColor Yellow
        try {
            python3 -m venv venv
        }
        catch {
            Write-Host "Failed to create virtual environment. Make sure Python is installed." -ForegroundColor Red
            exit 1
        }
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
try {
    .\venv\Scripts\Activate
}
catch {
    Write-Host "Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
try {
    python -m pip install --upgrade pip
}
catch {
    Write-Host "Failed to upgrade pip, but continuing..." -ForegroundColor Yellow
}

# Check if requirements.txt exists
if (-Not (Test-Path -Path ".\requirements.txt")) {
    Write-Host "requirements.txt not found in current directory." -ForegroundColor Red
    exit 1
}

# Install requirements with error handling
Write-Host "Installing requirements..." -ForegroundColor Green
try {
    pip install -r requirements.txt
}
catch {
    Write-Host "Error during package installation. Trying one by one..." -ForegroundColor Yellow
    
    # Read requirements.txt and install packages one by one
    foreach($line in Get-Content .\requirements.txt) {
        if ($line.Trim() -ne "") {
            Write-Host "Installing $line" -ForegroundColor Cyan
            try {
                pip install $line
            }
            catch {
                Write-Host "Failed to install $line. Continuing with other packages..." -ForegroundColor Red
            }
        }
    }
}

# Verify installation
Write-Host "Verifying critical dependencies..." -ForegroundColor Green
$criticalPackages = @("fastapi", "uvicorn", "sqlalchemy")
$allInstalled = $true

foreach ($package in $criticalPackages) {
    try {
        $result = pip show $package
        if ($result) {
            Write-Host "$package is installed successfully." -ForegroundColor Green
        } else {
            Write-Host "$package verification failed." -ForegroundColor Red
            $allInstalled = $false
        }
    }
    catch {
        Write-Host "$package verification failed." -ForegroundColor Red
        $allInstalled = $false
    }
}

if ($allInstalled) {
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "To run the application: uvicorn main:app --reload" -ForegroundColor Cyan
} else {
    Write-Host "Some critical packages may not be installed correctly." -ForegroundColor Yellow
    Write-Host "You may need to manually install missing packages." -ForegroundColor Yellow
}