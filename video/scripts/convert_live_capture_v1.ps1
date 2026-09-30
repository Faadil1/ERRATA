$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Raw = Join-Path $Root "video\live-capture-v1\raw"
$Out = Join-Path $Root "video\judge-remotion\public\live"

New-Item -ItemType Directory -Force -Path $Raw | Out-Null
New-Item -ItemType Directory -Force -Path $Out | Out-Null

$Shots = @(
  "01-base-voice",
  "02-correction-en-fr",
  "03-negative-ghost",
  "04-stale-current-commit"
)

foreach ($shot in $Shots) {
  $input = Join-Path $Raw "$shot.webm"
  $output = Join-Path $Out "$shot.mp4"
  if (-not (Test-Path $input)) {
    Write-Host "SKIP $shot (missing raw WebM)"
    continue
  }
  Write-Host "Converting $shot..."
  & ffmpeg -y -i $input `
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" `
    -r 30 -c:v libx264 -preset medium -crf 18 `
    -c:a aac -b:a 192k -movflags +faststart $output
  if ($LASTEXITCODE -ne 0) { throw "FFmpeg conversion failed for $shot" }
}

Write-Host "Converted live clips are in video\judge-remotion\public\live"
