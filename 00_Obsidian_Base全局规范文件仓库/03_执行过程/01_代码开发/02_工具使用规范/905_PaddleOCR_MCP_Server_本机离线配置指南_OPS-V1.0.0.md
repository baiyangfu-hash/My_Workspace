---
spec_id: OPS-905
title: PaddleOCR MCP Server本机离线配置指南
version: "V1.0.0"
domain: cross-domain
lifecycle: stable
canonical_path: "00_Obsidian_Base全局规范文件仓库/03_执行过程/01_代码开发/02_工具使用规范/905_PaddleOCR_MCP_Server_本机离线配置指南_OPS-V1.0.0.md"
---

# PaddleOCR MCP Server（本机离线）配置指南 - Windows

适用场景：扫描型 PDF（页面是图片/截图），需要 OCR + 版面结构化（PP-StructureV3）。

## 1. 准备：创建独立虚拟环境

建议不要装到系统 Python，单独建 venv，避免依赖冲突。

在 PowerShell 执行（示例路径可按你习惯调整）：

```powershell
python -m venv C:\Users\fubai\.venvs\paddleocr_mcp
& C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\activate.ps1
python -m pip install -U pip setuptools wheel
```

若你不想依赖“激活”状态（比如在脚本/CI 中），可直接指定 venv 的 python：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install -U pip setuptools wheel
```

## 2. 安装 PaddleOCR MCP（paddleocr-mcp）

官方提供 wheel 安装：

```powershell
python -m pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.1.0/paddleocr_mcp-0.1.0-py3-none-any.whl
```

Windows 建议先装 `python-magic-bin`（用于避免 python-magic 缺少 native 依赖导致的 `ImportError: failed to find libmagic`）：

```powershell
python -m pip install python-magic-bin
```

若你已经装过 `python-magic`，建议卸载它，避免其覆盖/抢占 `magic` 模块导致仍然报 libmagic：

```powershell
python -m pip uninstall -y python-magic
```

然后再执行上面的 wheel 安装命令。

### 2.1 FastMCP 兼容问题（log_level 报错）

若启动 `paddleocr_mcp` 时出现报错：

`TypeError: FastMCP() no longer accepts log_level. Pass log_level to run_http_async(), or set FASTMCP_LOG_LEVEL.`

这是因为 `fastmcp>=3` 已移除了 `FastMCP(..., log_level=...)` 构造参数，而 `paddleocr_mcp==0.1.0` 仍在构造时传入 `log_level`。

处理方式（推荐：改 1 行代码，适配 fastmcp>=3）：

1) 打开文件：

`C:\Users\fubai\.venvs\paddleocr_mcp\Lib\site-packages\paddleocr_mcp\__main__.py`

2) 把 `FastMCP(...)` 里的 `log_level=...` 删除，并在创建 `FastMCP` 前增加一行：

`os.environ["FASTMCP_LOG_LEVEL"] = "INFO" if args.verbose else "WARNING"`

## 3. 安装 PaddleOCR（本机推理引擎）

按 PaddleOCR 官方安装文档安装 PaddlePaddle + PaddleOCR：

- PaddleOCR 安装文档：http://www.paddleocr.ai/v3.1.0/en/version3.x/installation.html

通常本机 CPU 版本可先尝试：

```powershell
python -m pip install paddlepaddle
python -m pip install paddleocr
```

验证：

```powershell
paddleocr_mcp --help
```

若提示找不到命令，可用绝对路径验证：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\paddleocr_mcp.exe --help
```

### 3.1 PP-StructureV3 额外依赖（paddlex[ocr]）

如果你在启动 MCP（pipeline=PP-StructureV3）时遇到类似报错：

- `PP-StructureV3 requires additional dependencies`
- `Failed to create PaddleOCR engine: A dependency error occurred during pipeline creation`

说明当前环境里 `paddlex` 缺少 OCR 额外依赖，需要安装 `paddlex[ocr]`。

联网安装（Windows 建议强制使用 wheel，避免编译）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install -U "paddlex[ocr]==3.5.2" --only-binary=:all:
```

离线安装（推荐）：先在有网络的机器下载 wheels，再拷贝到本机离线安装。

在“有网络的机器”执行（下载到 wheelhouse 目录）：

```powershell
python -m pip download --dest wheelhouse --only-binary=:all: "paddlex[ocr]==3.5.2"
```

把 wheelhouse 整个目录拷贝到离线机器，然后在“离线机器”执行：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install --no-index --find-links wheelhouse "paddlex[ocr]==3.5.2"
```

### 3.2 兜底方案：先用 OCR pipeline

如果你暂时无法把 `paddlex[ocr]` 装齐（例如网络太慢/离线缺 wheel），可以先把 pipeline 改为 `OCR` 启动服务，保证 MCP 可用：

- `PADDLEOCR_MCP_PIPELINE=OCR`

### 3.3 PaddlePaddle 3.3.x 已知问题（PP-StructureV3 推理失败）

现象（Trae 工具调用时常表现为 “Error calling tool”）：

- `NotImplementedError: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support ... onednn_instruction.cc:118`

原因：

- PaddlePaddle 3.3.x 在 Windows/CPU 的某些推理路径（oneDNN / PIR 相关）存在兼容问题，会导致 PP-StructureV3 的底层推理在 `predictor.run()` 阶段直接失败。

解决方案（推荐固定版本）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install --force-reinstall --no-deps paddlepaddle==3.2.2
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -c "import paddle; print(paddle.__version__)"
```

确认输出为 `3.2.2` 后，再重启 Trae / 重载 MCP Servers。

## 4. 在 Trae 里添加 MCP Server（stdio）

### 4.1 Trae 全局配置（推荐：对所有工作区/项目生效）

在 Trae 的 MCP 页面，使用“手动配置（JSON）”添加一次即可（对 My_Workspace 下所有项目通用）：

```json
{
  "mcpServers": {
    "paddleocr-ppstructure-local": {
      "command": "C:\\\\Users\\\\fubai\\\\.venvs\\\\paddleocr_mcp\\\\Scripts\\\\paddleocr_mcp.exe",
      "args": ["--verbose"],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PP-StructureV3",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local",
        "PADDLEOCR_MCP_DEVICE": "cpu"
      }
    }
  }
}
```

保存后重载 MCP Servers（或重启 Trae）。

### 4.2 My_Workspace 项目级配置（对整个 My_Workspace 工作空间生效）

若你希望“项目级 MCP”统一从 My_Workspace 根目录加载：把 Trae 打开的项目根目录设为 `C:\Users\fubai\Desktop\My_Workspace`，并在该目录创建文件：

`C:\Users\fubai\Desktop\My_Workspace\.trae\mcp.json`

内容同上面的 JSON。然后打开 Trae 的“启用项目级 MCP”开关并重载。

### 4.3 单项目手动新增（仅对当前项目生效）

在 Trae 的 MCP Server 管理界面新增一个 server（stdio 模式），字段建议如下：

- name：`paddleocr-ppstructure-local`
- command：
  - `C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\paddleocr_mcp.exe`
- args：留空或 `["--verbose"]`
- env：
  - `PADDLEOCR_MCP_PIPELINE=PP-StructureV3`
  - `PADDLEOCR_MCP_PPOCR_SOURCE=local`
  - `PADDLEOCR_MCP_DEVICE=cpu`

注意：

- Trae 里使用 stdio 模式时，不要在 args 里配置 `--http/--host/--port`，否则会变成 HTTP transport，导致 MCP 工具调用失败。

保存后重启 Trae（或重载 MCP Servers）。

## 6. 跨电脑复制（可复用实施方案）

目标：把“已验证可用”的安装经验复制到另一台 Windows 电脑，确保 `PP-StructureV3 + 本机推理 + Trae MCP` 能直接跑通。

### 6.1 前置一致性要求

- Windows x64
- Python 主版本一致（建议统一用 3.11）
- 目标电脑可联网或可接收离线 wheel 包目录（wheelhouse）

### 6.2 推荐方案：离线 wheelhouse + requirements（最稳定）

在“已装好并跑通”的电脑上执行：

1) 导出 requirements：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip freeze > C:\Temp\paddleocr_mcp_requirements.txt
```

2) 下载 wheelhouse（只下二进制 wheel，避免编译；体积较大，耐心等待）：

```powershell
mkdir C:\Temp\paddleocr_mcp_wheelhouse
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip download --dest C:\Temp\paddleocr_mcp_wheelhouse --only-binary=:all: -r C:\Temp\paddleocr_mcp_requirements.txt
```

把以下两个东西拷贝到目标电脑（U盘/网盘均可）：

- `C:\Temp\paddleocr_mcp_requirements.txt`
- `C:\Temp\paddleocr_mcp_wheelhouse\`（整个目录）

在目标电脑上执行：

1) 创建 venv 并升级 pip：

```powershell
python -m venv C:\Users\fubai\.venvs\paddleocr_mcp
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install -U pip setuptools wheel
```

2) 离线安装（从 wheelhouse 安装）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install --no-index --find-links C:\Temp\paddleocr_mcp_wheelhouse -r C:\Temp\paddleocr_mcp_requirements.txt
```

3) 修复 Windows libmagic（如果 wheelhouse 里没包含它，可单独补装）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip uninstall -y python-magic
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -m pip install python-magic-bin
```

### 6.3 FastMCP v3 兼容补丁（自动打补丁）

若目标电脑启动时报：

`TypeError: FastMCP() no longer accepts log_level ...`

在目标电脑运行下面脚本自动修复（将 log_level 从构造参数迁移为环境变量 FASTMCP_LOG_LEVEL）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -c "import pathlib, re; p=pathlib.Path(r'C:\Users\fubai\.venvs\paddleocr_mcp\Lib\site-packages\paddleocr_mcp\__main__.py'); s=p.read_text(encoding='utf-8'); s=s.replace('log_level=\"INFO\" if args.verbose else \"WARNING\",\\n',''); if 'FASTMCP_LOG_LEVEL' not in s: s=re.sub(r\"(server_name\\s*=\\s*f\\\"PaddleOCR \\{args\\.pipeline\\} MCP server\\\"\\s*\\n)\", r\"\\1        os.environ[\\\"FASTMCP_LOG_LEVEL\\\"] = \\\"INFO\\\" if args.verbose else \\\"WARNING\\\"\\n\", s); p.write_text(s, encoding='utf-8'); print('patched', p)"
```

### 6.4 验证（目标电脑）

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\paddleocr_mcp.exe --help
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\paddleocr_mcp.exe --pipeline PP-StructureV3 --ppocr_source local --device cpu --verbose --help
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\python.exe -c "import paddle; print(paddle.__version__)"
```

如需进一步验证“能创建 PP-StructureV3 引擎”，可尝试启动 HTTP（看到启动日志后 Ctrl+C 退出）：

```powershell
C:\Users\fubai\.venvs\paddleocr_mcp\Scripts\paddleocr_mcp.exe --pipeline PP-StructureV3 --ppocr_source local --device cpu --http --host 127.0.0.1 --port 18080 --verbose
```

### 6.5 Trae 配置复制

Trae MCP 的 JSON 配置（见 4.1）可以直接复制到目标电脑 Trae 的“手动配置（JSON）”里。只要确保 `command` 路径与目标电脑 venv 路径一致即可。

## 5. 使用建议（扫描型 PDF）

优先用 PP-StructureV3，让其输出 Markdown（包含标题/段落/表格结构）。

给我下达的典型指令示例：

- “用 paddleocr-ppstructure-local 解析 `xxx.pdf`，输出 Markdown，并重点提取：IO 表、信号定义、报警码、状态机步骤。”
