# MCP工具使用指南

**文档版本**: V1.0.0  
**编制日期**: 2026-04-21  
**编制人**: 技术团队

---

## 1. 文档目的

本文档提供MCP（Model Context Protocol）工具的标准使用方法和最佳实践，特别是PDF reader工具的使用指南，解决文件读取路径问题，确保MCP工具能够正确读取和分析文件。

## 2. 适用范围

适用于使用MCP工具读取本地文件的场景，特别是PLC程序、电气图纸等技术文档的读取和分析。

## 3. MCP工具概述

### 3.1 工具类型

| 工具名称 | 功能描述 | 适用场景 |
|---------|---------|----------|
| PDF reader | 读取和分析PDF文件 | 技术文档、图纸、报告等PDF文件的读取 |
| File System | 读取本地文件系统 | 文本文件、配置文件等的读取 |
| GitHub | 操作GitHub仓库 | 代码仓库管理、文件操作等 |
| Excel | 处理Excel文件 | 数据表格、报表等的读取和操作 |
| Sequential Thinking | 序列思维处理 | 复杂问题的分析和推理 |

### 3.2 工具访问路径

MCP工具的配置文件位于：
```
c:\Users\fubai\.trae-cn\mcps\s_My_Workspace-0bf8a693\solo_coder/
```

## 4. PDF reader工具使用指南

### 4.1 问题描述

使用MCP PDF reader工具读取本地PDF文件时，可能遇到以下问题：
- 绝对路径被拒绝："Absolute paths are not allowed"
- 相对路径找不到文件："File not found"
- 路径格式不正确导致读取失败

### 4.2 解决方案

**使用`file://`协议的URL格式**：
```
file:///D:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/0100_项目/DJ-2026-005_边框缓存机/02_PLC程序/编译器导出pdf程序/01_梯形图.pdf
```

**格式说明**：
- 协议：`file://`
- 根目录：使用三个斜杠 `///`
- 路径分隔符：使用正斜杠 `/`
- 完整路径：包含盘符和所有目录层次

### 4.3 MCP工具调用示例

```json
{
  "server_name": "mcp_pdf-reader-mcp",
  "tool_name": "read_pdf",
  "args": {
    "sources": [{
      "url": "file:///D:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/0100_项目/DJ-2026-005_边框缓存机/02_PLC程序/编译器导出pdf程序/01_梯形图.pdf"
    }],
    "include_full_text": true,
    "include_metadata": true,
    "include_page_count": true
  }
}
```

### 4.4 备选方案

**使用Read工具**：
- 对于快速确认文件存在性，可使用Read工具直接读取PDF文件
- 返回的是原始二进制内容，但可以确认文件可读取

## 5. 最佳实践

### 5.1 路径处理

1. **绝对路径**：使用`file://`协议时，必须使用完整的绝对路径
2. **路径格式**：使用正斜杠 `/` 作为路径分隔符
3. **大小写**：保持路径大小写与实际文件系统一致
4. **特殊字符**：确保路径中不包含特殊字符，如有需要请使用URL编码

### 5.2 工具选择

| 工具 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| MCP PDF reader | 需要解析PDF内容 | 能够提取文本和元数据 | 路径格式要求严格 |
| Read工具 | 快速确认文件存在 | 简单直接 | 只返回原始二进制内容 |

### 5.3 故障排查

1. **文件存在性**：使用PowerShell命令验证文件是否存在
   ```powershell
   Test-Path "D:\BaiduSyncdisk\My_Workspace\path\to\file.pdf"
   ```

2. **路径格式**：确保使用正确的`file://`协议格式

3. **权限问题**：确保MCP工具有权限访问目标文件

4. **文件格式**：确认目标文件是有效的PDF文件

## 6. 示例应用

### 6.1 读取PLC程序PDF文件

**步骤**：
1. 确认PDF文件路径
2. 构建`file://`协议URL
3. 使用MCP PDF reader工具读取
4. 分析返回的PDF内容

**示例**：
- 文件路径：`D:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\0100_项目\DJ-2026-005_边框缓存机\02_PLC程序\编译器导出pdf程序\01_梯形图.pdf`
- URL格式：`file:///D:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/0100_项目/DJ-2026-005_边框缓存机/02_PLC程序/编译器导出pdf程序/01_梯形图.pdf`

### 6.2 读取电气图纸PDF文件

**步骤**：
1. 确认电气图纸PDF文件路径
2. 构建`file://`协议URL
3. 使用MCP PDF reader工具读取
4. 分析电气图纸内容

## 7. 版本管理

| 版本 | 日期 | 变更内容 | 编制人 |
|------|------|----------|--------|
| V1.0.0 | 2026-04-21 | 初始版本，记录MCP工具使用方法 | 技术团队 |

## 8. 相关资源

- [PDF读取问题分析报告](../../../.trae/specs/pdf-reader-issue/analysis_report.md)
- [MCP PDF reader工具配置](c:\Users\fubai\.trae-cn\mcps\s_My_Workspace-0bf8a693\solo_coder/mcp_pdf-reader-mcp/tools/read_pdf.json)

## 9. 结语

本指南提供了MCP工具的标准使用方法，特别是解决了PDF reader工具路径格式的问题。通过遵循本指南，可以确保MCP工具能够正确读取和分析文件，提高工作效率。

对于其他MCP工具的使用，可参考各自的工具配置文件和相关文档。