param(
  [switch]$Production
)

$ErrorActionPreference = "Stop"

# Vercel CLI writes normal informational output (including its version banner)
# to stderr. Windows PowerShell can promote native stderr to NativeCommandError
# when ErrorActionPreference is Stop even when the process itself succeeds.
# Native process success/failure is judged explicitly by LASTEXITCODE.
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$Scope = "faadil1s-projects"
$Project = "errata"
$Target = if ($Production) { "production" } else { "preview" }

function Get-ErrataSecret {
  param([string]$Name)

  $processValue = [Environment]::GetEnvironmentVariable($Name, "Process")
  if (-not [string]::IsNullOrWhiteSpace($processValue)) {
    return [pscustomobject]@{
      Value = $processValue
      Source = "Process"
    }
  }

  $userValue = [Environment]::GetEnvironmentVariable($Name, "User")
  if (-not [string]::IsNullOrWhiteSpace($userValue)) {
    return [pscustomobject]@{
      Value = $userValue
      Source = "Windows User"
    }
  }

  $machineValue = [Environment]::GetEnvironmentVariable($Name, "Machine")
  if (-not [string]::IsNullOrWhiteSpace($machineValue)) {
    return [pscustomobject]@{
      Value = $machineValue
      Source = "Windows Machine"
    }
  }

  $envPath = Join-Path (Get-Location) ".env"
  if (Test-Path $envPath) {
    foreach ($line in Get-Content -LiteralPath $envPath) {
      $trimmed = $line.Trim()
      if (
        [string]::IsNullOrWhiteSpace($trimmed) -or
        $trimmed.StartsWith("#")
      ) {
        continue
      }

      $prefix = "$Name="
      if ($trimmed.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
        $value = $trimmed.Substring($prefix.Length).Trim()
        if (
          ($value.StartsWith('"') -and $value.EndsWith('"')) -or
          ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
          $value = $value.Substring(1, $value.Length - 2)
        }
        if (-not [string]::IsNullOrWhiteSpace($value)) {
          return [pscustomobject]@{
            Value = $value
            Source = ".env"
          }
        }
      }
    }
  }

  return $null
}

function Invoke-Vercel {
  param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
  )

  $previousPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    & npx --yes vercel@latest @Args
    $exitCode = $LASTEXITCODE
  }
  finally {
    $ErrorActionPreference = $previousPreference
  }

  if ($exitCode -ne 0) {
    throw "Vercel command failed with exit code $($exitCode): $($Args -join ' ')"
  }
}

function Set-VercelSecret {
  param(
    [string]$Name,
    [string]$Value,
    [string]$Environment
  )

  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name is not available in the current Windows process environment."
  }

  $updated = $false

  $previousPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    try {
      $Value | & npx --yes vercel@latest env update $Name $Environment --sensitive --scope $Scope 2>$null
      if ($LASTEXITCODE -eq 0) {
        $updated = $true
      }
    }
    catch {
      $updated = $false
    }

    if (-not $updated) {
      $Value | & npx --yes vercel@latest env add $Name $Environment --sensitive --scope $Scope
      $exitCode = $LASTEXITCODE
      if ($exitCode -ne 0) {
        throw "Unable to configure Vercel secret $Name for $Environment (exit code $exitCode)."
      }
    }
  }
  finally {
    $ErrorActionPreference = $previousPreference
  }
}

Write-Host "ERRATA Vercel deployment preflight"
Write-Host "Scope: $Scope"
Write-Host "Target: $Target"

$AssemblySecret = Get-ErrataSecret "ASSEMBLYAI_API_KEY"
$Ai33Secret = Get-ErrataSecret "AI33_API_KEY"

if ($null -eq $AssemblySecret) {
  throw "ASSEMBLYAI_API_KEY was not found in Process, Windows User/Machine variables, or .env."
}

if ($null -eq $Ai33Secret) {
  throw "AI33_API_KEY was not found in Process, Windows User/Machine variables, or .env."
}

Write-Host "AssemblyAI secret source: $($AssemblySecret.Source)"
Write-Host "AI33 secret source: $($Ai33Secret.Source)"

$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
  $rng.GetBytes($bytes)
}
finally {
  $rng.Dispose()
}
$SessionSecret = -join ($bytes | ForEach-Object { $_.ToString("x2") })

# Reuse the existing local Vercel link when available. The ERRATA project
# already exists in faadil1s-projects; avoid project creation here because
# project setup can trigger validation/deployment side effects before preflight.
$ProjectFile = Join-Path (Get-Location) ".vercel\project.json"
if (Test-Path $ProjectFile) {
  Write-Host "Vercel project link: existing .vercel/project.json"
}
else {
  Invoke-Vercel link --yes --project $Project --scope $Scope
}

Set-VercelSecret "ERRATA_SESSION_HMAC_KEY" $SessionSecret $Target
Set-VercelSecret "ASSEMBLYAI_API_KEY" $AssemblySecret.Value $Target
Set-VercelSecret "AI33_API_KEY" $Ai33Secret.Value $Target

$GitSha = (git rev-parse HEAD).Trim()
if ([string]::IsNullOrWhiteSpace($GitSha)) {
  throw "Unable to resolve git HEAD."
}

$DeployArgs = @(
  "deploy",
  "--yes",
  "--scope", $Scope,
  "--env", "ERRATA_RUNTIME_GIT_SHA=$GitSha"
)

if ($Production) {
  $DeployArgs += "--prod"
}

$previousPreference = $ErrorActionPreference
try {
  $ErrorActionPreference = "Continue"
  $Output = & npx --yes vercel@latest @DeployArgs
  $deployExitCode = $LASTEXITCODE
}
finally {
  $ErrorActionPreference = $previousPreference
}

if ($deployExitCode -ne 0) {
  throw "Vercel deployment failed with exit code $deployExitCode."
}

$DeployUrl = (
  $Output |
  ForEach-Object { "$_".Trim() } |
  Where-Object { $_ -match '^https://[^\s]+$' } |
  Select-Object -Last 1
)

if ([string]::IsNullOrWhiteSpace($DeployUrl)) {
  throw "Could not resolve a deployment URL from Vercel output."
}

Write-Host "Deployment URL: $DeployUrl"
Write-Host "Waiting for /api/health..."

$health = $null

for ($i = 0; $i -lt 30; $i++) {
  try {
    $health = Invoke-RestMethod -Uri "$DeployUrl/api/health" -Method Get -TimeoutSec 10
    break
  }
  catch {
    Start-Sleep -Seconds 2
  }
}

if ($null -eq $health) {
  throw "Deployment never exposed /api/health."
}

if ($health.runtime -ne "vercel-fastapi") {
  throw "Unexpected runtime: $($health.runtime)"
}

if ($health.git_sha -ne $GitSha) {
  throw "Runtime SHA mismatch. Expected $GitSha; observed $($health.git_sha)"
}

Write-Host ""
Write-Host "VERIFIED"
Write-Host "git_sha=$($health.git_sha)"
Write-Host "session_signing_ready=$($health.session_signing_ready)"
Write-Host "assemblyai_ready=$($health.assemblyai_ready)"
Write-Host "ai33_ready=$($health.ai33_ready)"
Write-Host "full_public_voice_ready=$($health.full_public_voice_ready)"
Write-Host ""
Write-Host "No secret value was printed."
