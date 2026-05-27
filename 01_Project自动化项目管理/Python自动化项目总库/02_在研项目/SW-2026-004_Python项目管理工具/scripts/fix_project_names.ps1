<#
.SYNOPSIS
    修复项目中未替换的 {project_code} 占位符
.DESCRIPTION
    批量重命名包含 {project_code} 的文件，替换为实际的项目编码
.PARAMETER ProjectPath
    项目根目录路径
.PARAMETER ProjectCode
    实际的项目编码（默认: DJ-2026-001）
.EXAMPLE
    .\fix_project_names.ps1 -ProjectPath "D:\Projects\DJ-2026-001_xxx"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,

    [string]$ProjectCode = "DJ-2026-001"
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  项目名称修复工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "项目路径: $ProjectPath" -ForegroundColor Yellow
Write-Host "项目编码: $ProjectCode" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $ProjectPath)) {
    Write-Host "[ERROR] 项目路径不存在: $ProjectPath" -ForegroundColor Red
    exit 1
}

$filesToFix = Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object {
    $_.Name -like "*project_code*"
}

if ($filesToFix.Count -eq 0) {
    Write-Host "[INFO] 未发现需要修复的文件" -ForegroundColor Green
    exit 0
}

Write-Host "发现 $($filesToFix.Count) 个需要修复的文件:" -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($file in $filesToFix) {
    $newName = $file.Name.Replace("{project_code}", $ProjectCode)
    $newPath = Join-Path $file.Directory.FullName $newName

    try {
        Rename-Item -Path $file.FullName -NewName $newName -ErrorAction Stop
        Write-Host "[OK] 重命名成功: $($file.Name) -> $newName" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "[FAIL] 重命名失败: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  修复完成!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "成功: $successCount 个文件" -ForegroundColor Green
Write-Host "失败: $failCount 个文件" -ForegroundColor Red
Write-Host ""

if ($failCount -gt 0) {
    exit 1
} else {
    exit 0
}
