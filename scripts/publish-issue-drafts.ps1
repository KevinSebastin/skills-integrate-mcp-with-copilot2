param(
    [Parameter(Mandatory = $false)]
    [string]$Repo = "KevinSebastin/skills-integrate-mcp-with-copilot2",

    [Parameter(Mandatory = $false)]
    [string]$Token = $env:GITHUB_TOKEN,

    [Parameter(Mandatory = $false)]
    [switch]$WhatIf
)

if (-not $WhatIf -and -not $Token) {
    throw "Missing GitHub token. Set GITHUB_TOKEN env var or pass -Token."
}

$draftDir = Join-Path $PSScriptRoot "..\.github\ISSUE_DRAFTS"
if (-not (Test-Path $draftDir)) {
    throw "Issue draft directory not found: $draftDir"
}

$files = Get-ChildItem -Path $draftDir -File | Sort-Object Name
if ($files.Count -eq 0) {
    throw "No draft issue files found in $draftDir"
}

$headers = @{
    Authorization = "Bearer $Token"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw

    $titleMatch = [regex]::Match($content, "## Title\s*(?:\r?\n)+(.+)")
    if (-not $titleMatch.Success) {
        Write-Warning "Skipping $($file.Name): could not parse title"
        continue
    }

    $title = $titleMatch.Groups[1].Value.Trim()
    $body = $content.Trim()

    if ($WhatIf) {
        Write-Host "[WhatIf] Would create issue: $title"
        continue
    }

    $payload = @{
        title = $title
        body  = $body
    } | ConvertTo-Json -Depth 5

    $uri = "https://api.github.com/repos/$Repo/issues"

    try {
        $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $payload
        Write-Host "Created: $($response.html_url)"
    }
    catch {
        Write-Error "Failed to create issue from $($file.Name): $($_.Exception.Message)"
    }
}
