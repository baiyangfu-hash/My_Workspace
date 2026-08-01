import sys
sys.path.insert(0, '01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具')
from auto_pm.utils.file_utils import read_file, write_file
from pathlib import Path

path = Path('c:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/04_监控/01_变更管理/01_变更单/CHG-DOCU/CHG-DOCU-2026-002.md')
content = read_file(str(path))

# §5 变更前后
content = content.replace(
    '| 涉及文件/交付物 | （待填写） |\n| 关键参数/配置 | （待填写） |',
    '| 涉及文件/交付物 | 7 个 PRD 文档：GlobalVars DSN/UM、FB_1002 CHG/UM、FB_External CHG/UM、FB_1003 UM |\n| 关键参数/配置 | 补齐后 7/7 模块 PRD 四件套完整 |'
)

# §6.1 五大约束
content = content.replace('| **范围(Scope)** | □无 □低 □中 □高 |  |  |', '| **范围(Scope)** | □无 ☑低 □中 □高 | 补齐 4 个模块的 PRD 文档 | 按现有模板格式填充 |')
content = content.replace('| **进度(Schedule)** | □无 □低 □中 □高 | 延迟___天 |', '| **进度(Schedule)** | ☑无 □低 □中 □高 | 无延迟 |')
content = content.replace('| **成本(Cost)** | □无 □低 □中 □高 | 增加___元 |', '| **成本(Cost)** | ☑无 □低 □中 □高 | 无增加 |')
content = content.replace('| **质量(Quality)** | □无 □低 □中 □高 |  |', '| **质量(Quality)** | ☑无 □低 □中 □高 | 文档完整性提升 |')
content = content.replace('| **风险(Risk)** | □无 □低 □中 □高 |  |', '| **风险(Risk)** | ☑无 □低 □中 □高 | 无代码变更，风险极低 |')
content = content.replace('**风险等级**（PMBOK风险评估）：□无 □低 □中 □高', '**风险等级**（PMBOK风险评估）：☑无 □低 □中 □高')
content = content.replace('（待填写）\n\n### 6.2', '文档补全无代码变更风险，无需额外缓解措施\n\n### 6.2')

# §6.3 传播链
content = content.replace(
    '[___________] → [___________] → [___________]\n     ↓               ↓               ↓\n  (领域)          (领域)           (领域)',
    '[DOCU 文档补全] → 无跨领域影响\n     ↓\n  (仅 DOCU 领域)'
)

# §7 实施计划
content = content.replace(
    '| | | | | | | | |',
    '| 1 | 补齐 GlobalVars DSN/UM | fubai | 2026-08-02 | 2026-08-02 | 无 | 已完成 |\n| 2 | 补齐 FB_1002 CHG/UM | fubai | 2026-08-02 | 2026-08-02 | 无 | 已完成 |\n| 3 | 补齐 FB_External CHG/UM | fubai | 2026-08-02 | 2026-08-02 | 无 | 已完成 |\n| 4 | 补齐 FB_1003 UM | fubai | 2026-08-02 | 2026-08-02 | 无 | 已完成 |'
)

# §9 实施记录
content = content.replace(
    '| | | | | | | |\n\n## 10. 变更验证',
    '| 2026-08-02 | fubai | 补齐 PRD 四件套 | 创建 7 个 PRD 文档：GlobalVars DSN/UM、FB_1002 CHG/UM、FB_External CHG/UM、FB_1003 UM | 已完成 | 文档按现有模板格式填充，7/7 模块 PRD 四件套完整 |\n\n## 10. 变更验证'
)

# §10.1 验证项
content = content.replace(
    '| | | | | | | | |\n\n### 10.2',
    '| 1 | 文件存在性检查 | 7 个文件全部存在 | 7/7 存在 | 7/7 存在 | ✅通过 | fubai | 2026-08-02 |\n| 2 | 文件内容完整性 | 每个文件包含完整的章节结构 | 全部完整 | 全部完整 | ✅通过 | fubai | 2026-08-02 |\n| 3 | 台帐一致性 | 台帐已自动更新 CHG-DOCU-2026-002 | 已更新 | 已更新 | ✅通过 | fubai | 2026-08-02 |\n\n### 10.2'
)

# §10.3 验证结论
content = content.replace(
    '| □ 全部通过,可关闭 □ 部分不通过,需返工 □ 需补充验证 |',
    '| ☑ 全部通过,可关闭 □ 部分不通过,需返工 □ 需补充验证 |'
)

# §11 版本详细变更说明
content = content.replace(
    '1. 变更单创建\n2. 初始版本，记录变更基本信息、原因、内容、影响分析',
    '1. 补齐 GlobalVars DSN/UM（详细设计说明书 + 使用说明）\n2. 补齐 FB_1002 CHG/UM（变更记录 + 使用说明，含 V11.0.0 破坏性重构文档）\n3. 补齐 FB_External CHG/UM（变更记录 + 使用说明，含 V4.1.0 安全信号链修复文档）\n4. 补齐 FB_1003 UM（使用说明，含 6 步 S20~S25 状态机描述）\n5. 所有文档按现有 PRD 模板格式填充，与已有文档风格一致\n6. 补齐后 DJ-2026-005 全 7 模块 PRD 四件套 100% 完整'
)

write_file(str(path), content)
print('变更单已填写完成')