param(
  [switch]$Production
)

$ErrorActionPreference = "Stop"

$Scope = "faadil1s-projects"
$Project = "errata"
$Target = if ($Production) { "production" } else { "preview" }

function Invoke-Vercel {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
  & npx --yes vercel@latest @Args
  if ($LASTEXITCODE -ne 0) {
    throw "Vercel command failed: $($Args -join ' ')"
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

  # Update first when the variable already exists; otherwise add it.
  $updated = $false
  try {
    $Value | & npx --yes vercel@latest env update $Name $Environment --sensitive --scope $Scope 2>$null
    if ($LASTEXITCODE -eq 0) { $updated = $true }
  } catch {}

  if (-not $updated) {
    $Value | & npx --yes vercel@latest env add $Name $Environment --sensitive --scope $Scope
    if ($LASTEXITCODE -ne 0) {
      throw "Unable to configure Vercel secret $Name for $Environment."
    }
  }
}

Write-Host "ERRATA Vercel deployment preflight"
Write-Host "Scope: $Scope"
Write-Host "Target: $Target"

if ([string]::IsNullOrWhiteSpace($env:ASSEMBLYAI_API_KEY)) {
  throw "ASSEMBLYAI_API_KEY is missing from this PowerShell process. Open a fresh shell if it exists as a persistent User variable."
}
if ([string]::IsNullOrWhiteSpace($env:AI33_API_KEY)) {
  throw "AI33_API_KEY is missing from this PowerShell process. Open a fresh shell if it exists as a persistent User variable."
}

$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
$SessionSecret = -join ($bytes | ForEach-Object { $_.ToString("x2") })

# Project creation is idempotent through the subsequent link step.
& npx --yes vercel@latest project add $Project --scope $Scope 2>$null
Invoke-Vercel link --yes --project $Project --scope $Scope

Set-VercelSecret "ERRATA_SESSION_HMAC_KEY" $SessionSecret $Target
Set-VercelSecret "ASSEMBLYAI_API_KEY" $env:ASSEMBLYAI_API_KEY $Target
Set-VercelSecret "AI33_API_KEY" $env:AI33_API_KEY $Target

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

$Output = & npx --yes vercel@latest @DeployArgs
if ($LASTEXITCODE -ne 0) {
  throw "Vercel deployment failed."
}

$DeployUrl = ($Output | Select-Object -Last 1).Trim()
if (-not $DeployUrl.StartsWith("http")) {
  throw "Could not resolve deployment URL from Vercel output: $DeployUrl"
}

Write-Host "Deployment URL: $DeployUrl"
Write-Host "Waiting for /api/health..."

$health = $null
for ($i = 0; $i -lt 30; $i++) {
  try {
    $health = Invoke-RestMethod -Uri "$DeployUrl/api/health" -Method Get -TimeoutSec 10
    break
  } catch {
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
