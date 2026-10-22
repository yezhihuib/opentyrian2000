# Materialize an external current pack before any game/profile activity.
function New-CurrentCraft267Pack([string]$RepoRoot, [ValidateSet('preview','debug')][string]$Kind, [string]$Python) {
    $craftPython = $Python
    if (-not $craftPython) { $craftPython = (Get-Command python -ErrorAction Stop).Source }
    $craftOutput = Join-Path (Split-Path -Parent $RepoRoot) ('current-craft267-packs\' + $Kind + '-' + [Guid]::NewGuid().ToString('N'))
    $craftResult = & $craftPython (Join-Path $RepoRoot 'scripts\build_current_craft267.py') --root $RepoRoot view --kind $Kind --output $craftOutput
    if ($LASTEXITCODE -ne 0) { throw 'Current craft267 pack validation failed; no game was launched.' }
    $craftView = ($craftResult | Out-String | ConvertFrom-Json)
    if ($craftView.status -ne 'PASS' -or -not (Test-Path -LiteralPath $craftView.path -PathType Container)) {
        throw 'Current craft267 pack did not complete.'
    }
    return $craftView.path
}
