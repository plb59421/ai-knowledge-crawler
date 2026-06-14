param(
    [string]$ProjectRoot = "D:\AI_WORK_SPACE\ai_knowledge_crawler",
    [string]$PythonExe = "python",
    [string]$DomesticTime = "06:30",
    [string]$ProxyTime = "08:30",
    [switch]$WhatIfOnly
)

$domesticAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_daily.py --group domestic --max-pages 5" -WorkingDirectory $ProjectRoot
$proxyAction = New-ScheduledTaskAction -Execute $PythonExe -Argument "scripts\run_daily.py --group proxy --max-pages 3" -WorkingDirectory $ProjectRoot

$domesticTrigger = New-ScheduledTaskTrigger -Daily -At $DomesticTime
$proxyTrigger = New-ScheduledTaskTrigger -Daily -At $ProxyTime

if ($WhatIfOnly) {
    Write-Host "Would register task: AIKnowledgeCrawler-Domestic at $DomesticTime"
    Write-Host "Would register task: AIKnowledgeCrawler-Proxy at $ProxyTime"
    exit 0
}

Register-ScheduledTask -TaskName "AIKnowledgeCrawler-Domestic" -Action $domesticAction -Trigger $domesticTrigger -Description "Run domestic AI knowledge crawler sources" -Force
Register-ScheduledTask -TaskName "AIKnowledgeCrawler-Proxy" -Action $proxyAction -Trigger $proxyTrigger -Description "Run proxy-required AI knowledge crawler sources" -Force
