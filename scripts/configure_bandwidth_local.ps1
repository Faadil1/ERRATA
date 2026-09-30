$ErrorActionPreference = "Stop"

function Read-PlainFromSecure {
  param([string]$Prompt)

  $secure = Read-Host $Prompt -AsSecureString
  $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  }
  finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  }
}

function New-RandomHex {
  param([int]$Bytes = 24)

  $buffer = New-Object byte[] $Bytes
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  try {
    $rng.GetBytes($buffer)
  }
  finally {
    $rng.Dispose()
  }
  return -join ($buffer | ForEach-Object { $_.ToString("x2") })
}

function Set-UserAndProcessEnv {
  param(
    [string]$Name,
    [string]$Value
  )

  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name cannot be empty."
  }

  [Environment]::SetEnvironmentVariable($Name, $Value, "User")
  [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
}

Write-Host "ERRATA Bandwidth Build local credential setup"
Write-Host "No secret value will be printed."
Write-Host ""

$AccountId = (Read-Host "Bandwidth Account ID").Trim()
$ClientId = (Read-Host "Bandwidth Client ID").Trim()
$ClientSecret = Read-PlainFromSecure "Bandwidth Client Secret"

$WebhookUsername = "errata-webhook-" + (New-RandomHex 6)
$WebhookPassword = New-RandomHex 24
$StreamUsername = "errata-stream-" + (New-RandomHex 6)
$StreamPassword = New-RandomHex 24

Set-UserAndProcessEnv "BANDWIDTH_ACCOUNT_ID" $AccountId
Set-UserAndProcessEnv "BANDWIDTH_CLIENT_ID" $ClientId
Set-UserAndProcessEnv "BANDWIDTH_CLIENT_SECRET" $ClientSecret
Set-UserAndProcessEnv "BANDWIDTH_WEBHOOK_USERNAME" $WebhookUsername
Set-UserAndProcessEnv "BANDWIDTH_WEBHOOK_PASSWORD" $WebhookPassword
Set-UserAndProcessEnv "BANDWIDTH_STREAM_USERNAME" $StreamUsername
Set-UserAndProcessEnv "BANDWIDTH_STREAM_PASSWORD" $StreamPassword

Write-Host ""
Write-Host "Configured:"
Write-Host "- BANDWIDTH_ACCOUNT_ID"
Write-Host "- BANDWIDTH_CLIENT_ID"
Write-Host "- BANDWIDTH_CLIENT_SECRET"
Write-Host "- BANDWIDTH_WEBHOOK_USERNAME"
Write-Host "- BANDWIDTH_WEBHOOK_PASSWORD"
Write-Host "- BANDWIDTH_STREAM_USERNAME"
Write-Host "- BANDWIDTH_STREAM_PASSWORD"
Write-Host ""
Write-Host "Values were stored in Windows User + current Process environment."
Write-Host "No secret value was printed."
Write-Host ""
Write-Host "Next, use these commands one at a time to copy the Voice callback credentials into Bandwidth:"
Write-Host '  $env:BANDWIDTH_WEBHOOK_USERNAME | Set-Clipboard'
Write-Host '  $env:BANDWIDTH_WEBHOOK_PASSWORD | Set-Clipboard'
Write-Host ""
Write-Host "The stream username/password do not need to be entered into the Bandwidth UI."
