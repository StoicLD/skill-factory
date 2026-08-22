[CmdletBinding()]
param(
    [ValidatePattern('^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$')]
    [string]$Version = '1.1.0'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pluginName = 'ten-step-learning-suite'
$marketplaceName = 'ten-step-learning-local'
$sourceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $sourceRoot '..'))
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot '..'))
$outputParent = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot 'codex-plugin'))
$outputRoot = [System.IO.Path]::GetFullPath((Join-Path $outputParent $pluginName))
$pluginParent = Join-Path $outputRoot 'plugins'
$pluginRoot = Join-Path $pluginParent $pluginName
$marketplacePath = Join-Path $outputRoot '.agents\plugins\marketplace.json'
$packageSource = Join-Path $sourceRoot 'factory\plugins\ten-step-learning-suite'
$manifestTemplate = Join-Path $packageSource 'plugin.json.template'
$brandAssets = Join-Path $packageSource 'assets'
$pluginCreatorRoot = Join-Path $env:USERPROFILE '.codex\skills\.system\plugin-creator'

$skillNames = @(
    'ten-step-learning-report'
    'ten-step-06-learning-ladder'
    'ten-step-07-core-sprint'
    'ten-step-08-adaptive-exam'
    'ten-step-09-feynman-loop'
)
$requiredBrandAssets = @('icon.png', 'logo.png', 'logo-dark.png')

if ([System.IO.Directory]::GetParent($outputRoot).FullName -ne $outputParent) {
    throw "Unsafe output path: $outputRoot"
}
if ([System.IO.Path]::GetFileName($outputRoot) -ne $pluginName) {
    throw "Output folder must be named $pluginName"
}
if (-not (Test-Path -LiteralPath $manifestTemplate -PathType Leaf)) {
    throw "Manifest template is missing: $manifestTemplate"
}
foreach ($assetName in $requiredBrandAssets) {
    $assetPath = Join-Path $brandAssets $assetName
    if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf)) {
        throw "Brand asset is missing: $assetPath"
    }
}
foreach ($skillName in $skillNames) {
    $skillRoot = Join-Path $sourceRoot $skillName
    if (-not (Test-Path -LiteralPath (Join-Path $skillRoot 'SKILL.md') -PathType Leaf)) {
        throw "Skill source is incomplete: $skillRoot"
    }
}

# Validate authoritative sources before replacing the last successful artifact.
& python -B (Join-Path $sourceRoot 'scripts\validate_skills.py') $sourceRoot
if ($LASTEXITCODE -ne 0) {
    throw 'Source Skill validation failed.'
}
Push-Location $sourceRoot
try {
    & python -B -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) {
        throw 'Source unit tests failed.'
    }
}
finally {
    Pop-Location
}

# Every build is clean: remove only the verified direct-child artifact directory.
if (Test-Path -LiteralPath $outputRoot) {
    Remove-Item -LiteralPath $outputRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $outputParent | Out-Null

$scaffoldScript = Join-Path $pluginCreatorRoot 'scripts\create_basic_plugin.py'
$validatorScript = Join-Path $pluginCreatorRoot 'scripts\validate_plugin.py'
if (-not (Test-Path -LiteralPath $scaffoldScript -PathType Leaf)) {
    throw "Codex plugin scaffold is missing: $scaffoldScript"
}
if (-not (Test-Path -LiteralPath $validatorScript -PathType Leaf)) {
    throw "Codex plugin validator is missing: $validatorScript"
}

& python -B $scaffoldScript $pluginName `
    --path $pluginParent `
    --with-skills `
    --with-assets `
    --with-marketplace `
    --marketplace-path $marketplacePath `
    --marketplace-name $marketplaceName `
    --category Productivity
if ($LASTEXITCODE -ne 0) {
    throw 'Codex plugin scaffold failed.'
}

$manifest = Get-Content -Raw -LiteralPath $manifestTemplate | ConvertFrom-Json
$manifest.version = $Version
$manifestJson = $manifest | ConvertTo-Json -Depth 20
$manifestPath = Join-Path $pluginRoot '.codex-plugin\plugin.json'
[System.IO.File]::WriteAllText(
    $manifestPath,
    $manifestJson + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)

$marketplace = Get-Content -Raw -LiteralPath $marketplacePath | ConvertFrom-Json
$marketplace.interface.displayName = 'Ten-step-learning Local'
$marketplaceJson = $marketplace | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText(
    $marketplacePath,
    $marketplaceJson + [Environment]::NewLine,
    [System.Text.UTF8Encoding]::new($false)
)

foreach ($assetName in $requiredBrandAssets) {
    Copy-Item -LiteralPath (Join-Path $brandAssets $assetName) `
        -Destination (Join-Path (Join-Path $pluginRoot 'assets') $assetName) -Force
}
foreach ($skillName in $skillNames) {
    $sourceSkill = Join-Path $sourceRoot $skillName
    $outputSkill = Join-Path (Join-Path $pluginRoot 'skills') $skillName
    Copy-Item -LiteralPath $sourceSkill -Destination $outputSkill -Recurse -Force
}

# Build artifacts must not contain repository metadata or interpreter caches.
$discardDirectories = Get-ChildItem -LiteralPath $outputRoot -Recurse -Force -Directory |
    Where-Object { $_.Name -in @('.git', '__pycache__', '.pytest_cache') } |
    Sort-Object FullName -Descending
foreach ($directory in $discardDirectories) {
    Remove-Item -LiteralPath $directory.FullName -Recurse -Force
}
Get-ChildItem -LiteralPath $outputRoot -Recurse -Force -File |
    Where-Object { $_.Extension -in @('.pyc', '.pyo') } |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

# Verify that packaged source files are byte-identical to authoritative inputs.
foreach ($assetName in $requiredBrandAssets) {
    $sourceAsset = Join-Path $brandAssets $assetName
    $outputAsset = Join-Path (Join-Path $pluginRoot 'assets') $assetName
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceAsset).Hash
    $outputHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputAsset).Hash
    if ($sourceHash -ne $outputHash) {
        throw "Packaged brand asset differs from source: $outputAsset"
    }
}
foreach ($skillName in $skillNames) {
    $sourceSkill = Join-Path $sourceRoot $skillName
    $outputSkill = Join-Path (Join-Path $pluginRoot 'skills') $skillName
    $sourceFiles = @(Get-ChildItem -LiteralPath $sourceSkill -Recurse -Force -File)
    $outputFiles = @(Get-ChildItem -LiteralPath $outputSkill -Recurse -Force -File)
    if ($sourceFiles.Count -ne $outputFiles.Count) {
        throw "Packaged file count differs for $skillName"
    }
    foreach ($sourceFile in $sourceFiles) {
        $relativePath = [System.IO.Path]::GetRelativePath($sourceSkill, $sourceFile.FullName)
        $outputFile = Join-Path $outputSkill $relativePath
        if (-not (Test-Path -LiteralPath $outputFile -PathType Leaf)) {
            throw "Packaged file is missing: $outputFile"
        }
        $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceFile.FullName).Hash
        $outputHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputFile).Hash
        if ($sourceHash -ne $outputHash) {
            throw "Packaged file differs from source: $outputFile"
        }
    }
}

& python -B $validatorScript $pluginRoot
if ($LASTEXITCODE -ne 0) {
    throw 'Codex Plugin validation failed.'
}
& python -B (Join-Path $sourceRoot 'scripts\validate_skills.py') (Join-Path $pluginRoot 'skills')
if ($LASTEXITCODE -ne 0) {
    throw 'Packaged Skill validation failed.'
}

$packagedFiles = @(Get-ChildItem -LiteralPath $outputRoot -Recurse -Force -File)
Write-Host "Built $pluginName $Version"
Write-Host "Marketplace: $outputRoot"
Write-Host "Plugin: $pluginRoot"
Write-Host "Skills: $($skillNames.Count)"
Write-Host "Files: $($packagedFiles.Count)"
Write-Host "Install marketplace: codex plugin marketplace add `"$outputRoot`""
Write-Host "Install plugin: codex plugin add $pluginName@$marketplaceName"
