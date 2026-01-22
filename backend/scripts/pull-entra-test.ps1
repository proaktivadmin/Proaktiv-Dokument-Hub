# Pull user data from Entra ID and update local database
# This is the REVERSE of the normal sync flow

Set-Location $PSScriptRoot\..

# Ensure DATABASE_URL points to local Docker PostgreSQL
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/dokument_hub"

# Load .env
$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
    Write-Host "Loaded .env file" -ForegroundColor Green
}

$testEmail = "froyland@proaktiv.no"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  ENTRA ID -> DATABASE SYNC TEST" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Email: $testEmail"
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Import Graph module
Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
Import-Module Microsoft.Graph.Users -ErrorAction Stop

# Connect to Microsoft Graph
Write-Host "[1/4] Connecting to Microsoft Graph..." -ForegroundColor Yellow
$secureSecret = ConvertTo-SecureString $env:ENTRA_CLIENT_SECRET -AsPlainText -Force
$credential = [PSCredential]::new($env:ENTRA_CLIENT_ID, $secureSecret)
Connect-MgGraph -TenantId $env:ENTRA_TENANT_ID -ClientSecretCredential $credential -NoWelcome
Write-Host "      Connected!" -ForegroundColor Green

# Fetch user from Entra ID
Write-Host ""
Write-Host "[2/4] Fetching user from Entra ID..." -ForegroundColor Yellow
$entraUser = Get-MgUser -UserId $testEmail -Property "id,displayName,givenName,surname,jobTitle,mobilePhone,mail,department,officeLocation,streetAddress,postalCode,city,country" -ErrorAction Stop

Write-Host "      Found user: $($entraUser.DisplayName)" -ForegroundColor Green
Write-Host ""
Write-Host "      Entra ID Data:" -ForegroundColor Cyan
Write-Host "        ID:             $($entraUser.Id)"
Write-Host "        Display Name:   $($entraUser.DisplayName)"
Write-Host "        Given Name:     $($entraUser.GivenName)"
Write-Host "        Surname:        $($entraUser.Surname)"
Write-Host "        Job Title:      $($entraUser.JobTitle)"
Write-Host "        Mobile Phone:   $($entraUser.MobilePhone)"
Write-Host "        Email:          $($entraUser.Mail)"
Write-Host "        Department:     $($entraUser.Department)"
Write-Host "        Office:         $($entraUser.OfficeLocation)"
Write-Host "        Street:         $($entraUser.StreetAddress)"
Write-Host "        Postal Code:    $($entraUser.PostalCode)"
Write-Host "        City:           $($entraUser.City)"
Write-Host "        Country:        $($entraUser.Country)"

# Get current database record
Write-Host ""
Write-Host "[3/4] Fetching current database record..." -ForegroundColor Yellow

$pythonGetScript = @"
import sys
import json
sys.path.insert(0, '.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.employee import Employee
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    emp = db.query(Employee).filter(Employee.email == '$testEmail').first()
    if emp:
        print(json.dumps({
            'id': str(emp.id),
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'title': emp.title,
            'phone': emp.phone,
            'email': emp.email
        }))
    else:
        print('null')
finally:
    db.close()
"@

$dbRecordJson = & py -3.12 -c $pythonGetScript
$dbRecord = $dbRecordJson | ConvertFrom-Json

if ($dbRecord) {
    Write-Host "      Found in database!" -ForegroundColor Green
    Write-Host ""
    Write-Host "      Current Database Record:" -ForegroundColor Cyan
    Write-Host "        ID:         $($dbRecord.id)"
    Write-Host "        First Name: $($dbRecord.first_name)"
    Write-Host "        Last Name:  $($dbRecord.last_name)"
    Write-Host "        Title:      $($dbRecord.title)"
    Write-Host "        Phone:      $($dbRecord.phone)"
    Write-Host "        Email:      $($dbRecord.email)"
} else {
    Write-Host "      User not found in database!" -ForegroundColor Red
    Disconnect-MgGraph | Out-Null
    exit 1
}

# Update database with Entra ID data
Write-Host ""
Write-Host "[4/4] Updating database with Entra ID data..." -ForegroundColor Yellow

# Prepare the update values from Entra
$newFirstName = $entraUser.GivenName
$newLastName = $entraUser.Surname
$newTitle = $entraUser.JobTitle
$newPhone = $entraUser.MobilePhone

Write-Host ""
Write-Host "      Changes to apply:" -ForegroundColor Yellow
Write-Host "        first_name: '$($dbRecord.first_name)' -> '$newFirstName'"
Write-Host "        last_name:  '$($dbRecord.last_name)' -> '$newLastName'"
Write-Host "        title:      '$($dbRecord.title)' -> '$newTitle'"
Write-Host "        phone:      '$($dbRecord.phone)' -> '$newPhone'"

# Python script to update the database
$pythonUpdateScript = @"
import sys
sys.path.insert(0, '.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.employee import Employee
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    emp = db.query(Employee).filter(Employee.email == '$testEmail').first()
    if emp:
        emp.first_name = '''$($newFirstName -replace "'", "''")'''
        emp.last_name = '''$($newLastName -replace "'", "''")'''
        emp.title = '''$($newTitle -replace "'", "''")'''
        emp.phone = '''$($newPhone -replace "'", "''")'''
        db.commit()
        print('SUCCESS')
    else:
        print('NOT_FOUND')
finally:
    db.close()
"@

$updateResult = & py -3.12 -c $pythonUpdateScript

if ($updateResult -eq 'SUCCESS') {
    Write-Host ""
    Write-Host "      Database updated successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "      Failed to update database: $updateResult" -ForegroundColor Red
}

# Disconnect
Disconnect-MgGraph | Out-Null

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  SYNC COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
