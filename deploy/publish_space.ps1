# Push deploy/hf_space to your Hugging Face Space (git)
# Usage: .\deploy\publish_space.ps1 -SpaceUser Dolendra -SpaceName ollive-oss-assistant

param(
    [string]$SpaceUser = "Dolendra",
    [string]$SpaceName = "ollive-oss-assistant"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Preparing Space bundle..."
python deploy\prepare_hf_space.py

$SpaceDir = Join-Path $Root "deploy\hf_space"
Set-Location $SpaceDir

$remote = "https://huggingface.co/spaces/$SpaceUser/$SpaceName"

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

$existing = git remote get-url space 2>$null
if (-not $existing) {
    git remote add space $remote
}

git add -A
git commit -m "Deploy OSS assistant to HF Space" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing new to commit, pushing anyway..."
}

Write-Host "Pushing to $remote"
git push space main

Write-Host ""
Write-Host "Live demo: https://huggingface.co/spaces/$SpaceUser/$SpaceName"
