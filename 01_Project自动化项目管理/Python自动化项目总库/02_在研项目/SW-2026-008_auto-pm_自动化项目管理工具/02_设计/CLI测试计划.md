# CLI 测试计划 V0.5.2

> **项目**: SW-2026-008 auto-pm（自动化项目管理工具）
> **版本**: V0.5.2（CLI 测试整合：补齐 change/python/template + 统一组织 + cli 模式）
> **创建日期**: 2026-07-01
> **最后更新**: 2026-07-01
> **执行脚本**:
> - 统一入口：`python scripts/run_tests.py cli`（127 passed / 2 skipped）
> - 直接执行：`pytest tests/cli/ tests/spec/test_cli.py -v`
> **关联文档**:
> - [GUI测试计划.md](GUI测试计划.md)（V0.5.1 GUI 测试三层架构）
> - [PM_SESSION_SW-2026-008.md](PM_SESSION_SW-2026-008.md)

---

## 1. 测试目标

### 1.1 主目标

通过 CLI 集成测试验证 auto-pm 8 个命令组的端到端功能完整性，覆盖命令参数解析、业务逻辑执行、错误路径处理。

### 1.2 子目标

1. **命令组覆盖**：8/8 命令组均有测试（project/plc/change/doc/vartable/spec/python/template）
2. **子命令覆盖**：每个命令组的核心子命令均有测试
3. **边界用例**：缺参/非法参数/不存在项目/非法状态流转等错误路径
4. **测试隔离**：每个测试用 `tmp_path` 独立工作空间，无 session 污染
5. **统一入口**：`run_tests.py cli` 一键执行所有 CLI 测试

---

## 2. 测试范围

### 2.1 命令组覆盖矩阵

| 命令组 | 测试文件 | 子命令覆盖 | 用例数 | V0.5.2 状态 |
|--------|---------|-----------|--------|-------------|
| project | tests/cli/test_project.py | list/show/create/snapshot | 15 | 已验证（V0.5.0 已有） |
| plc | tests/cli/test_plc.py | check/init/repair/standardize | 16 | 已验证（V0.5.0 已有） |
| change | tests/cli/test_change.py | list/show/create/transition/edit | 17 | 已验证（V0.5.2 新增） |
| doc | tests/cli/test_doc.py | inject/refresh | 9 | 已验证（V0.5.0 已有） |
| vartable | tests/cli/test_vartable.py | parse/detect-encoding/list-encodings | 7 | 已验证（V0.5.0 已有） |
| spec | tests/cli/test_spec.py + tests/spec/test_cli.py | check/index/frontmatter/report | 36+3 | 已验证（V0.5.2 补边界） |
| python | tests/cli/test_python.py | init/check | 10 | 已验证（V0.5.2 新增） |
| template | tests/cli/test_template.py | list/update | 3 | 已验证（V0.5.2 新增） |
| **合计** | **7 文件 + 1 跨目录** | **8/8 命令组** | **127 passed / 2 skipped** | **覆盖 100%** |

### 2.2 测试方法

- **驱动方式**：Click `CliRunner.invoke()` 程序化驱动（不依赖真实终端）
- **工作空间隔离**：每个测试用 `tmp_path` fixture 创建独立临时工作空间
- **项目创建策略**：
  - 轻量项目：`_make_plc_project()` / `_make_python_project()` 内联创建标志文件（绕过 Copier，快）
  - 真实项目：`project create` / `python init` 调用真实 Copier 模板（少数集成测试）
- **变更单清理**：`_cleanup_test_changes` autouse fixture 在每个测试后清理变更单文件
- **公共 fixture**：tests/cli/conftest.py 提供 `plc_project_factory` / `python_project_factory` 工厂函数

### 2.3 测试环境

| 项 | 值 |
|----|-----|
| 工作空间 | `tmp_path`（每个测试独立隔离） |
| Python 环境 | `.venv`（必须激活） |
| Click 版本 | >=8.1.7 |
| 测试标记 | `@pytest.mark.cli`（已注册到 pyproject.toml） |
| 执行命令 | `python scripts/run_tests.py cli` 或 `pytest tests/cli/ tests/spec/test_cli.py` |

---

## 3. 测试用例详情

### 3.1 project 命令组（TC-01，15 用例）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-01-01~05 | list/show | 基础查询 + 不存在项目 | test_project.py |
| TC-01-06~08 | show | Week2 元数据 + Week3 资产摘要 + JSON 输出 | test_project.py |
| TC-01-09~10 | create | dry-run + 实际创建（Week2 模板） | test_project.py |
| TC-01-11~17 | snapshot | 漂移检测/dry-run/无漂移/不存在/无表/无注册表/JSON | test_project.py |
| TC-01-18~20 | doc refresh | dry-run/JSON/集成创建后刷新 | test_project.py |

### 3.2 plc 命令组（TC-02，16 用例）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-02-01~05 | check | all/single/not_found/substance/fix | test_plc.py |
| TC-02-06~09 | check Python | 友好输出/JSON/--all 跳过/不污染驾驶舱 | test_plc.py |
| TC-02-10~14 | init | standard/test-suite/默认/shared-library 失败/无效模式/已存在 | test_plc.py |
| TC-02-15~17 | repair | 正常/dry-run/not_found | test_plc.py |
| TC-02-18~21 | standardize | 预览/执行/无变更/not_found | test_plc.py |

### 3.3 change 命令组（TC-03，17 用例，V0.5.2 新增）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-03-01~05 | list | 空列表/有变更单/--status/--domain/--full | test_change.py |
| TC-03-06~07 | show | 正常/not_found | test_change.py |
| TC-03-08~10 | create | 正常/缺参/not_found 项目 | test_change.py |
| TC-03-11~14 | transition | draft→submitted/非法状态/not_found/不可达状态 | test_change.py |
| TC-03-15~17 | edit | 正常/not_found/无字段更新 | test_change.py |

### 3.4 doc 命令组（TC-04，9 用例）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-04-01~05 | inject | dry-run/写入/inject+refresh 一致性/锚点缺失/JSON | test_doc.py |
| TC-04-06~07 | inject 边界 | not_found/skip 已存在 marker | test_doc.py |
| TC-04-08~09 | refresh | bracket 保留（inject/refresh） | test_doc.py |

### 3.5 vartable 命令组（TC-05，7 用例）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-05-01~03 | parse | JSON/table/不存在文件 | test_vartable.py |
| TC-05-04~05 | detect-encoding | text/json | test_vartable.py |
| TC-05-06~07 | list-encodings/help | 列表/帮助 | test_vartable.py |

### 3.6 spec 命令组（TC-06，36+3 用例）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-06-01~07 | check | help/missing-workspace/with-workspace/json/severity/nonexistent/project-scope | tests/spec/test_cli.py |
| TC-06-08~16 | index | with-workspace/single-domain/missing/nonexistent/pm/python/idempotent/invalid | tests/spec/test_cli.py |
| TC-06-17~22 | frontmatter | dry-run/missing/nonexistent/spec-id/nonexistent-spec/apply-with-fix | tests/spec/test_cli.py |
| TC-06-23~28 | report | with-workspace/json/missing/nonexistent/custom-output/markdown-default | tests/spec/test_cli.py |
| TC-06-29~36 | config/quiet | check-config/quiet-no-errors/quiet-with-errors/index-quiet/index-config/frontmatter-quiet/report-quiet/report-config/nonexistent/quiet-json | tests/spec/test_cli.py |
| TC-06-37~39 | 边界 | help/no-subcommand/invalid-subcommand（V0.5.2 新增） | tests/cli/test_spec.py |

### 3.7 python 命令组（TC-07，10 用例，V0.5.2 新增）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-07-01~03 | init | dry-run/实际创建/已存在路径 | test_python.py |
| TC-07-04~10 | check | 正常/JSON/not_found/非 Python/--all/无 Python/缺参 | test_python.py |

### 3.8 template 命令组（TC-08，3 用例，V0.5.2 新增）

| 用例 ID | 子命令 | 描述 | 文件 |
|---------|--------|------|------|
| TC-08-01 | list | 列出可用模板（从 test_plc.py 迁移） | test_template.py |
| TC-08-02~03 | update | not_found/missing-copier-answers | test_template.py |

---

## 4. 执行命令

### 4.1 统一入口（推荐）

```powershell
# 激活虚拟环境
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 切换到项目目录
cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"

# 全量 CLI 测试（tests/cli/ + tests/spec/test_cli.py）
python scripts/run_tests.py cli

# 详细输出
python scripts/run_tests.py cli --verbose
```

### 4.2 直接 pytest

```powershell
# 全量 CLI 测试
pytest tests/cli/ tests/spec/test_cli.py -v --no-cov

# 单个命令组
pytest tests/cli/test_change.py -v --no-cov
pytest tests/cli/test_python.py -v --no-cov

# 单个测试用例
pytest tests/cli/test_change.py::test_change_create_normal -v --no-cov
```

### 4.3 按标记筛选

```powershell
# 仅运行带 @pytest.mark.cli 标记的测试
pytest tests/cli/ -m cli -v --no-cov
```

---

## 5. 评估标准

### 5.1 通过/失败标准

| 等级 | 标准 |
|------|------|
| ✅ 全部通过 | 0 failed，所有命令组覆盖 |
| 🟡 部分通过 | 0 failed，但命令组覆盖 < 8/8 |
| ❌ 失败 | 任何 failed |

### 5.2 测试报告产出

每次执行后生成：
1. **pytest 终端输出**：通过/失败/跳过计数 + 耗时
2. **junit XML**：`coverage/junit/test-results.xml`（供 CI 解析）
3. **覆盖率报告**：`coverage/html/`（HTML 格式，可选）

---

## 6. 已知限制

### 6.1 测试环境限制

- CliRunner 无法验证真实终端输出格式（颜色/表格渲染）
- 无法验证 `auto-pm` 命令行别名（需真实安装）
- Copier 模板测试依赖模板存在（python-tool 模板缺失时跳过）

### 6.2 测试覆盖缺口

- ✅ V0.5.2 已补齐 change/python/template 命令组
- ⚠️ gui 命令（`auto-pm gui` 启动 GUI）未在 CLI 层测试（GUI 本身有专门测试）
- ⚠️ 部分子命令的复杂参数组合未全覆盖（如 change create 的所有 scope 组合）

### 6.3 跨目录组织

- spec CLI 测试分两处：
  - tests/spec/test_cli.py：依赖 tests/spec/conftest.py 的 populated_workspace fixture（保留原位避免 fixture 断裂）
  - tests/cli/test_spec.py：新增边界用例，使用 tests/cli/conftest.py 的 fixture 体系
- 统一入口 `run_tests.py cli` 涵盖两处

---

## 7. 后续迭代计划

### 7.1 V0.5.2 已完成（2026-07-01）

1. ✅ 新增 tests/cli/test_change.py（17 用例，覆盖 5 子命令）
2. ✅ 新增 tests/cli/test_python.py（10 用例，覆盖 2 子命令）
3. ✅ 新增 tests/cli/test_template.py（3 用例，覆盖 2 子命令）
4. ✅ 新增 tests/cli/test_spec.py（3 边界用例）
5. ✅ 迁移 test_plc.py 的 test_template_list 到 test_template.py
6. ✅ 增强 tests/cli/conftest.py（plc_project_factory/python_project_factory）
7. ✅ run_tests.py 添加 cli 模式
8. ✅ 注册 cli marker 到 pyproject.toml

### 7.2 V0.5.x 后续优化

- 补齐 change create 的 scope 组合边界用例
- 补齐 doc refresh 的锚点缺失边界用例
- 评估 spec CLI 测试统一迁移到 tests/cli/ 的可行性（需重构 fixture）

### 7.3 V0.6.0+ 长期演进

- 引入 CLI 输出快照测试（snapshottest）
- 评估 CLI 参数组合的 property-based testing（hypothesis）
- 建立 CLI 命令性能基准（响应时间监控）

---

## 8. 附录

### 8.1 测试脚本结构

```
tests/
├── cli/
│   ├── conftest.py              # CLI 测试 fixture（cli_runner/plc_project_factory/python_project_factory）
│   ├── test_project.py          # project 命令组（15 用例）
│   ├── test_plc.py              # plc 命令组（16 用例）
│   ├── test_change.py           # change 命令组（17 用例，V0.5.2 新增）
│   ├── test_doc.py              # doc 命令组（9 用例）
│   ├── test_vartable.py         # vartable 命令组（7 用例）
│   ├── test_python.py           # python 命令组（10 用例，V0.5.2 新增）
│   ├── test_template.py         # template 命令组（3 用例，V0.5.2 新增）
│   └── test_spec.py             # spec 边界用例（3 用例，V0.5.2 新增）
├── spec/
│   └── test_cli.py              # spec 命令组主体（36 用例，保留原位）
└── ...
```

### 8.2 V0.5.2 测试执行结果

- **全量 CLI 测试**：127 passed, 2 skipped in 12.10s
- **新增用例**：32 passed, 1 skipped（python init 实际创建因模板缺失跳过）
- **无回归**：原有 96 passed 全部通过

### 8.3 关键代码引用

- 统一入口：[scripts/run_tests.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/scripts/run_tests.py)（cli 模式）
- CLI 测试 fixture：[tests/cli/conftest.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/cli/conftest.py)
- change 命令测试：[tests/cli/test_change.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/cli/test_change.py)
- python 命令测试：[tests/cli/test_python.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/cli/test_python.py)
