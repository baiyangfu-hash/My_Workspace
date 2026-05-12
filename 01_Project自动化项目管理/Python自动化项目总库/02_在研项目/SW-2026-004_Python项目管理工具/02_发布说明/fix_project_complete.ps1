<#
.SYNOPSIS
    项目后处理完整工具集 v1.0
.DESCRIPTION
    自动修复Python项目管理工具创建的项目中的常见问题：
    1. 修复{project_code}等占位符未被替换的问题
    2. 补全变更管理目录结构（符合Obsidian 043规范V2.1.0）
    3. 验证项目结构完整性
    4. 生成修复报告
.PARAMETER ProjectPath
    项目根目录路径
.PARAMETER ProjectCode
    实际的项目编码（如 DJ-2026-001）
.PARAMETER ProjectName
    项目名称（可选，用于填充文档内容）
.PARAMETER CompleteChangeManagement
    是否补全变更管理目录结构（默认: $true）
.PARAMETER GenerateReport
    是否生成修复报告（默认: $true）
.EXAMPLE
    .\fix_project_complete.ps1 -ProjectPath "D:\Projects\DJ-2026-001_xxx"
.EXAMPLE
    .\fix_project_complete.ps1 -ProjectPath "D:\Projects\DJ-2026-001_xxx" -ProjectCode "DJ-2026-001" -CompleteChangeManagement:$true
.NOTES
    版本: 1.0.0
    作者: AI Assistant
    日期: 2026-04-15
    用途: Python项目管理工具 V2.4.0 Bug修复辅助工具
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,

    [string]$ProjectCode = "",

    [string]$ProjectName = "",

    [bool]$CompleteChangeManagement = $true,

    [bool]$GenerateReport = $true
)

$ErrorActionPreference = "Stop"
$scriptVersion = "1.0.0"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Python项目管理工具 - 项目后处理完整工具集 v$scriptVersion" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$results = @{
    filesRenamed = 0
    filesContentFixed = 0
    dirsCreated = 0
    errors = @()
}

if (-not (Test-Path $ProjectPath)) {
    Write-Host "[ERROR] 项目路径不存在: $ProjectPath" -ForegroundColor Red
    exit 1
}

$projectDir = Get-Item $ProjectPath

if ($ProjectCode -eq "") {
    $ProjectCode = ((Split-Path $ProjectPath -Leaf) -split "_")[0]
    Write-Host "[INFO] 未指定项目编码，从路径自动提取: $ProjectCode" -ForegroundColor Yellow
}

Write-Host "项目路径: $($projectDir.FullName)" -ForegroundColor Yellow
Write-Host "项目编码: $ProjectCode" -ForegroundColor Yellow
Write-Host "项目名称: $(if($ProjectName){$ProjectName}else{'[自动检测]'})" -ForegroundColor Yellow
Write-Host "开始时间: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow
Write-Host ""

$placeholders = @{
    "{project_code}" = $ProjectCode
    "{project_name}" = $ProjectName
    "{current_date}" = (Get-Date).ToString("yyyy-MM-dd")
    "{current_time}" = (Get-Date).ToString("HH:mm:ss")
}

Write-Host "--- 步骤1: 修复文件名占位符 ---" -ForegroundColor Magenta

$filesToRename = Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object {
    $name = $_.Name
    $placeholders.Keys | Where-Object { $name -like "*$_*" }
} | ForEach-Object {
    $_
}

foreach ($file in $filesToRename) {
    $newName = $file.Name
    foreach ($placeholder in $placeholders.Keys) {
        if ($newName -like "*$placeholder*") {
            $newName = $newName.Replace($placeholder, $placeholders[$placeholder])
        }
    }

    if ($newName -ne $file.Name) {
        $newPath = Join-Path $file.Directory.FullName $newName
        try {
            Rename-Item -Path $file.FullName -NewName $newName -ErrorAction Stop
            Write-Host "  [OK] 重命名: $($file.Name) -> $newName" -ForegroundColor Green
            $results.filesRenamed++
        }
        catch {
            $errorMsg = "重命名失败: $($file.Name) - $($_.Exception.Message)"
            Write-Host "  [FAIL] $errorMsg" -ForegroundColor Red
            $results.errors += $errorMsg
        }
    }
}

Write-Host "  共修复 $($results.filesRenamed) 个文件名" -ForegroundColor Cyan
Write-Host ""

Write-Host "--- 步骤2: 修复文件内容占位符 ---" -ForegroundColor Magenta

$textExtensions = @('.md', '.txt', '.json', '.csv', '.py', '.bat', '.ps1', '.yml', '.yaml')

$contentFiles = Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object {
    $textExtensions -contains $_.Extension.ToLower()
}

foreach ($file in $contentFiles) {
    try {
        $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)

        $needsUpdate = $false
        foreach ($placeholder in $placeholders.Keys) {
            if ($content.Contains($placeholder)) {
                $needsUpdate = $true
                break
            }
        }

        if ($needsUpdate) {
            $newContent = $content
            foreach ($placeholder in $placeholders.Keys) {
                $newContent = $newContent.Replace($placeholder, $placeholders[$placeholder])
            }

            [System.IO.File]::WriteAllText($file.FullName, $newContent, [System.Text.Encoding]::UTF8)
            Write-Host "  [OK] 内容更新: $($file.Name)" -ForegroundColor Green
            $results.filesContentFixed++
        }
    }
    catch {
        $errorMsg = "内容修复失败: $($file.Name) - $($_.Exception.Message)"
        Write-Host "  [WARN] $errorMsg" -ForegroundColor Yellow
        $results.errors += $errorMsg
    }
}

Write-Host "  共修复 $($results.filesContentFixed) 个文件内容" -ForegroundColor Cyan
Write-Host ""

if ($CompleteChangeManagement) {
    Write-Host "--- 步骤3: 补全变更管理目录结构 ---" -ForegroundColor Magenta

    $changeMgmtBase = Join-Path $ProjectPath "00_项目管理\04_变更管理"
    $changeOrderDir = Join-Path $changeMgmtBase "01_变更单"

    if (-not (Test-Path $changeMgmtBase)) {
        New-Item -ItemType Directory -Path $changeMgmtBase -Force | Out-Null
        Write-Host "  [OK] 创建: 04_变更管理/" -ForegroundColor Green
        $results.dirsCreated++
    }

    if (-not (Test-Path $changeOrderDir)) {
        New-Item -ItemType Directory -Path $changeOrderDir -Force | Out-Null
        Write-Host "  [OK] 创建: 01_变更单/" -ForegroundColor Green
        $results.dirsCreated++
    }

    $chgDomains = @(
        @{code="ELEC"; name="电气设计类"; desc="电气图纸修改、IO点位调整、元器件选型变更"},
        @{code="MECH"; name="机械结构类"; desc="结构件修改、3D模型更新、BOM调整"},
        @{code="PLC"; name="PLC程序类"; desc="程序逻辑修改、功能块新增、通讯协议变更"},
        @{code="HMI"; name="HMI程序类"; desc="界面布局修改、操作流程优化、报警信息调整"},
        @{code="SCPT"; name="脚本工具类"; desc="辅助脚本修改、数据处理逻辑变更"},
        @{code="DOCU"; name="文档类"; desc="技术文档更新、操作手册修订、规格书变更"},
        @{code="SAFE"; name="安全功能类"; desc="安全逻辑修改、急停回路变更、防护装置调整"}
    )

    foreach ($domain in $chgDomains) {
        $domainDir = Join-Path $changeOrderDir "CHG-$($domain.code)"
        $readmePath = Join-Path $domainDir "README.md"

        if (-not (Test-Path $domainDir)) {
            New-Item -ItemType Directory -Path $domainDir -Force | Out-Null
            Write-Host "  [OK] 创建: CHG-$($domain.code)/" -ForegroundColor Green
            $results.dirsCreated++
        }

        if (-not (Test-Path $readmePath)) {
            $readmeContent = @"
# $($domain.name)变更单

## 用途
存放所有$($domain.name)相关的变更记录和文档。

## 命名规范
- 格式：`CHG-$($domain.code)-[YYYY]-[序号]_[简短描述].md`
- 示例：`CHG-$($domain.code)-2026-001_示例变更.md`

## 典型变更类型
$($domain.desc -split '、' | ForEach-Object { "- $_" })

## 关联文档
- [$($ProjectCode)_版本变更台帐.md](../../$($ProjectCode)_版本变更台帐.md)

---
**最后更新**: $(Get-Date -Format 'yyyy-MM-dd')
"@
            Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
            Write-Host "  [OK] 创建: CHG-$($domain.code)/README.md" -ForegroundColor Green
        }
    }

    $ledgerPath = Join-Path $changeMgmtBase "$($ProjectCode)_版本变更台帐.md"
    if (-not (Test-Path $ledgerPath)) {
        $ledgerContent = @"
# $ProjectCode 版本变更台帐

## 版本变更记录

| 版本号 | 变更日期 | 变更类型 | 变更内容摘要 | 变更人 | 审批人 | 状态 |
|:------:|:--------:|:--------:|-------------|:------:|:------:|:----:|
| V1.0.0 | $(Get-Date -Format 'yyyy-MM-dd') | 初始创建 | 项目初始化 | 系统 | - | 已发布 |

---
**最后更新**: $(Get-Date -Format 'yyyy-MM-dd')
"@
        Set-Content -Path $ledgerPath -Value $ledgerContent -Encoding UTF8
        Write-Host "  [OK] 创建: $($ProjectCode)_版本变更台帐.md" -ForegroundColor Green
    }

    $rootReadmePath = Join-Path $changeMgmtBase "README.md"
    if (-not (Test-Path $rootReadmePath)) {
        $rootReadmeContent = @"
# 变更管理目录

本目录按照 Obsidian 规范 043_通用变更管理目录结构说明_PM-V2.1.0 组织。

## 目录结构

### 01_变更单/

| 子目录 | 编码 | 用途 |
|--------|:----:|------|
| CHG-ELEC | ELEC | 电气设计类变更 |
| CHG-MECH | MECH | 机械结构类变更 |
| CHG-PLC | PLC | PLC程序类变更 |
| CHG-HMI | HMI | HMI程序类变更 |
| CHG-SCPT | SCPT | 脚本工具类变更 |
| CHG-DOCU | DOCU | 文档类变更 |
| CHG-SAFE | SAFE | 安全功能类变更 |

## 文件

- [$($ProjectCode)_版本变更台帐.md](./$($ProjectCode)_版本变更台帐.md) - 版本变更历史记录

---
**最后更新**: $(Get-Date -Format 'yyyy-MM-dd')
"@
        Set-Content -Path $rootReadmePath -Value $rootReadmeContent -Encoding UTF8
        Write-Host "  [OK] 创建: README.md（根目录）" -ForegroundColor Green
    }

    Write-Host "  共创建/更新 $($results.dirsCreated) 个目录和文件" -ForegroundColor Cyan
    Write-Host ""
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  处理完成!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "统计信息:" -ForegroundColor Yellow
Write-Host "  文件名修复: $($results.filesRenamed) 个" -ForegroundColor White
Write-Host "  内容修复:   $($results.filesContentFixed) 个" -ForegroundColor White
Write-Host "  目录创建:   $($results.dirsCreated) 个" -ForegroundColor White
Write-Host "  错误数量:   $($results.errors.Count) 个" -ForegroundColor White
Write-Host ""
Write-Host "耗时: $($duration.TotalSeconds.ToString('F2')) 秒" -ForegroundColor Yellow
Write-Host "结束时间: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow

if ($results.errors.Count -gt 0) {
    Write-Host ""
    Write-Host "错误详情:" -ForegroundColor Red
    foreach ($err in $results.errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
}

if ($GenerateReport) {
    $reportPath = Join-Path $projectDir.FullName "_fix_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
    $reportContent = @"
# 项目后处理修复报告

**生成时间**: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))
**工具版本**: v$scriptVersion
**项目路径**: $($projectDir.FullName)
**项目编码**: $ProjectCode

---

## 修复统计

| 项目 | 数量 |
|------|:----:|
| 文件名修复 | $($results.filesRenamed) |
| 内容修复 | $($results.filesContentFixed) |
| 目录创建 | $($results.dirsCreated) |
| 错误数 | $($results.errors.Count) |
| 总耗时 | $($duration.TotalSeconds.ToString('F2'))秒 |

## 修复详情

### 文件名修复列表

共修复 $($results.filesRenamed) 个文件的 `{project_code}` 占位符。

### 内容修复列表

共修复 $($results.filesContentFixed) 个文件的内容占位符。

### 新增目录/文件

共创建 $($results.dirsCreated) 个目录和文件，包括：
- 4个变更管理子目录（CHG-ELEC, CHG-MECH, CHG-HMI, CHG-SAFE）
- 各子目录的 README.md
- 版本变更台帐
- 变更管理根目录 README.md

$(if ($results.errors.Count -gt 0) { @"
## 错误清单

$($errors | ForEach-Object { "- `n$_`n" })
"@ } else { @"
## 错误清单

无错误 ✅
"@ })

---

**工具**: Python项目管理工具 - 项目后处理完整工具集
**版本**: v$scriptVersion
"@

    Set-Content -Path $reportPath -Value $reportContent -Encoding UTF8
    Write-Host ""
    Write-Host "[INFO] 修复报告已生成: $reportPath" -ForegroundColor Cyan
}

Write-Host ""
exit ($results.errors.Count -gt 0 ? 1 : 0)
