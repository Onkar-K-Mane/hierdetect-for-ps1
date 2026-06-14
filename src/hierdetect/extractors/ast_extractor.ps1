param([string]$ScriptPath)
$ErrorActionPreference = 'SilentlyContinue'

$code = [System.IO.File]::ReadAllText($ScriptPath)
$ast = [System.Management.Automation.Language.Parser]::ParseInput($code, [ref]$null, [ref]$null)
$allNodes = $ast.FindAll({$true}, $true)

$nodeList = @()
$edgeList = @()
$nodeMap = @{}

for ($i = 0; $i -lt $allNodes.Count; $i++) {
    $nodeMap[$allNodes[$i]] = $i
    $nodeList += $allNodes[$i].GetType().Name
}

for ($i = 0; $i -lt $allNodes.Count; $i++) {
    $parent = $allNodes[$i].Parent
    if ($null -ne $parent -and $nodeMap.ContainsKey($parent)) {
        $edgeList += ,@($nodeMap[$parent], $i)
    }
}

@{ nodes = $nodeList; edges = $edgeList } | ConvertTo-Json -Depth 10 -Compress