# SW-2026-004 V2.1.0 后续收尾工作计划

> **计划日期**: 2026-04-12
> **状态**: 📝 待用户确认
> **前置条件**: V2.1.0代码升级已完成 (~1200行代码修改)

---

## 一、当前状态诊断

### 1.1 版本号混乱问题 ⚠️

| 位置 | 当前值 | 应改为 | 问题 |
|:----:|:------:|:------:|:-----|
| [version.py](03_主程序/01_主程序核心代码/src/core/version.py#L6) | **`1.1.0`** | **`2.1.0`** | 🔴 与文档V2.1.0不一致 |
| 台帐文档 | V1.0.3→已更新为V2.1.0 | ✅ | 已同步 |
| 技术方案 | DEV-V1.0.0 + DEV-V2.1.0(新) | ✅ | 双版本共存 |
| 交付清单 | V1.0.3→已更新为V2.1.0 | ✅ | 已同步 |
| setup.py | 从version.py读取 | 自动跟随 | 无需手动改 |

**结论**: 核心版本号 `version.py` 仍为 `1.1.0`，需升级到 `2.1.0`

### 1.2 数据库Schema滞后 ⚠️

[Alembic initial_schema.py](03_主程序/01_主程序核心代码/alembic/versions/initial_schema.py#L166-L179) 中的 `changes` 表定义:

```python
# 当前的旧定义 (仅8个字段):
op.create_table('changes',
    sa.Column('change_id', ...),
    sa.Column('project_id', ...),
    sa.Column('title', ...),
    sa.Column('description', ...),     # ❌ 应拆分为 reason/content_before/content_after
    sa.Column('change_type', ...),      # ❌ 应替换为 domain+nature+scope
    sa.Column('status', ...),
    sa.Column('requested_by', ...),     # ❌ 应替换为 proposer/approver/implementer
    ...
)
```

**缺少的V2.1.0字段 (14个)**:
```
domain (Enum)           - 技术领域
nature (Enum)           - 业务性质
scope (Enum)            - 影响范围
priority (String)       - 优先级 P0~P3
content_before (Text)    - 变更前内容
content_after (Text)     - 变更后内容
reason (Text)            - 变更原因
impact_analysis (Text)   - 影响分析
related_changes (JSON)   - 关联变更列表
propagation_chain (Text) - 传播链图
approval_level (String)  - 审批层级
reviewer (String)        - 复审人
approved_at (DateTime)   - 审批时间
implemented_at (DateTime)- 实施时间
completed_at (DateTime)  - 完成时间
proposer (String)        - 提出人 (替代requested_by)
approver (String)        - 审批人
implementer (String)     - 实施人
attachment (String)      - 附件路径
```

**解决方案**: 创建新的 Alembic migration 文件 `v21_change_management_upgrade.py`

### 1.3 旧文档待归档

| 文件 | 位置 | 状态 | 操作 |
|:----:|:-----|:----:|:----:|
| `01_变更管理技术方案_DEV-V1.0.0.md` | 01_项目文档/04_监控和控制/ | 存在 | → `_archive/` |
| `_archive/` 目录 | 项目根目录 | **不存在** | 需创建 |

---

## 二、执行计划 (5个任务)

### Task 1: 版本号统一升级 📌

**目标**: 将所有版本号统一为 `2.1.0`

#### 1.1 修改 version.py

**文件**: `03_主程序/01_主程序核心代码/src/core/version.py`

**当前内容**:
```python
VERSION = "1.1.0"
VERSION_INFO = {
    "major": 1,
    "minor": 1,
    "patch": 0,
    "build": "20260330",
    "status": "stable"
}
```

**目标内容**:
```python
VERSION = "2.1.0"
VERSION_INFO = {
    "major": 2,
    "minor": 1,
    "patch": 0,
    "build": "20260412",
    "status": "stable",
    "changelog": "变更管理模块V2.1.0工程化升级"
}
```

**改动点**:
- VERSION: `1.1.0` → `2.1.0` (major升级因为有架构性变更)
- major/minor/patch: `1.1.0` → `2.1.0`
- build: `20260330` → `20260412` (今日日期)
- 新增 changelog 字段 (可选)

#### 1.2 更新 spec_version_config.json (如有)

检查并同步配置文件中的版本号。

---

### Task 2: 旧文档归档 📁

**目标**: 将被V2.1.0替代的旧版本文档移入 `_archive/` 目录

#### 2.1 创建 _archive 目录结构

```
SW-2026-004_Python项目管理工具/
└── _archive/
    └── 01_项目文档/
        └── 04_监控和控制/
            └── README.md          (归档索引)
```

#### 2.2 归档文件清单

| 序号 | 源文件 | 目标路径 | 归档原因 |
|:----:|:-------|:---------|:---------|
| 1 | `01_项目文档/04_监控和控制/01_变更管理技术方案_DEV-V1.0.0.md` | `_archive/.../DEV-V1.0.0.md` | 已被DEV-V2.1.0替代 |

#### 2.3 创建归档README

在 `_archive/01_项目文档/04_监控和控制/README.md` 中记录:
- 归档日期: 2026-04-12
- 归档原因: V2.1.0升级替代
- 原文件清单及对应的新版本

---

### Task 3: 数据库迁移脚本 🗄️

**目标**: 创建 Alembic migration 为 changes 表添加14个V2.1.0新字段

#### 3.1 创建迁移文件

**文件**: `03_主程序/01_主程序核心代码/alembic/versions/v21_change_mgmt_upgrade.py`

**revision ID**: `v21_change_mgmt`
**down_revision**: `initial_schema`

#### 3.2 upgrade() 内容

```python
def upgrade() -> None:
    # === V2.1.0: 变更管理模块工程化升级 ===

    # 1. 新增二维分类字段 (替代 change_type)
    op.add_column('changes', sa.Column('domain', sa.String(10), nullable=True, default='PLC'))
    op.add_column('changes', sa.Column('nature', sa.String(10), nullable=True, default='OPT'))
    op.add_column('changes', sa.Column('scope', sa.String(10), nullable=True, default='LOCAL'))

    # 2. 新增优先级和详细内容
    op.add_column('changes', sa.Column('priority', sa.String(10), nullable=True, default='P2'))
    op.add_column('changes', sa.Column('reason', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('content_before', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('content_after', sa.Text(), nullable=True))
    op.add_column('changes', sa.Column('impact_analysis', sa.Text(), nullable=True))

    # 3. 新增传播链与关联
    op.add_column('changes', sa.Column('related_changes', sa.JSON(), nullable=True))
    op.add_column('changes', sa.Column('propagation_chain', sa.Text(), nullable=True))

    # 4. 新增分级审批字段
    op.add_column('changes', sa.Column('approval_level', sa.String(30), nullable=True))
    op.add_column('changes', sa.Column('reviewer', sa.String(50), nullable=True))

    # 5. 新增时间戳
    op.add_column('changes', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('changes', sa.Column('implemented_at', sa.DateTime(), nullable=True))
    op.add_column('changes', sa.Column('completed_at', sa.DateTime(), nullable=True))

    # 6. 替换人员字段 (保留旧字段兼容)
    op.add_column('changes', sa.Column('proposer', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('approver', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('implementer', sa.String(100), nullable=True))
    op.add_column('changes', sa.Column('attachment', sa.String(500), nullable=True))

    # 7. 数据迁移: 将旧字段的值映射到新字段
    op.execute("""
        UPDATE changes SET
            proposer = requested_by,
            domain = CASE
                WHEN change_type IN ('需求变更', '需求') THEN 'REQ'
                WHEN change_type IN ('缺陷修复', '缺陷') THEN 'DEF'
                WHEN change_type IN ('优化改进', '优化', '技术变更') THEN 'OPT'
                WHEN change_type IN ('配置调整', '配置') THEN 'CFG'
                WHEN change_type IN ('紧急变更', '紧急') THEN 'EMRG'
                ELSE 'OPT'
            END,
            scope = CASE
                WHEN impact LIKE '%全局%' OR impact LIKE '%系统%' THEN 'SYSTEM'
                WHEN impact LIKE '%模块%' OR impact LIKE '%部分%' THEN 'MODULE'
                WHEN impact LIKE '%局部%' OR impact LIKE '%小%' THEN 'LOCAL'
                ELSE 'LOCAL'
            END
        WHERE requested_by IS NOT NULL
    """)
```

#### 3.3 downgrade() 内容

```python
def downgrade() -> None:
    # 移除所有V2.1.0新增字段 (按添加顺序逆序)
    new_columns = [
        'attachment', 'implementer', 'approver', 'proposer',
        'completed_at', 'implemented_at', 'approved_at',
        'reviewer', 'approval_level',
        'propagation_chain', 'related_changes',
        'impact_analysis', 'content_after', 'content_before',
        'reason', 'priority',
        'scope', 'nature', 'domain',
    ]
    for col in new_columns:
        op.drop_column('changes', col)
```

---

### Task 4: 文件重命名与清理 🔄

#### 4.1 重命名台帐文件

**源文件**: `01_项目文档/04_监控和控制/06_版本变更台帐_CHG-V1.0.3.md`
**目标文件**: `01_项目文档/04_监控和控制/06_版本变更台帐_CHG-V2.1.0.md`

**同时需要更新的引用**:
- [交付清单](06_交付物/01_交付清单_DEL-V1.0.0.md) 中的链接
- [技术方案](01_项目文档/04_监控和控制/01_变更管理技术方案_DEV-V2.1.0.md) 中可能的引用

#### 4.2 重命名交付清单 (可选)

**源文件**: `06_交付物/01_交付清单_DEL-V1.0.0.md`
**目标文件**: `06_交付物/01_交付清单_DEL-V2.1.0.md`

#### 4.3 清理冗余引用

检查所有文档中对旧版本的引用并更新。

---

### Task 5: 重新打包可执行文件 📦

**目标**: 使用升级后的代码生成新的 exe 文件

#### 5.1 前置检查

- [ ] version.py 已更新为 2.1.0
- [ ] 所有代码修改已保存
- [ ] 数据库迁移脚本已创建

#### 5.2 执行打包命令

```bash
cd 03_主程序/01_主程序核心代码
python build.py --clean --onedir
```

**参数说明**:
- `--clean`: 清理旧的 build/dist 缓存
- `--onedir`: 打包为目录模式 (推荐，启动更快)

#### 5.3 打包后操作

1. **验证版本号**: 运行生成的 exe → 检查关于对话框显示 `2.1.0`
2. **复制到交付物目录**:
   ```
   复制: dist/Python项目管理工具/ → 06_交付物/01_可执行文件/
   ```
3. **复制数据库**: 如果使用了测试数据库，需一并复制
4. **更新交付清单**: 标记 exe 版本为 V2.1.0

#### 5.4 可选: 生成 zip 交付包

```bash
# 在 06_交付物/ 目录下
powershell Compress-Archive -Path * -DestinationPath "Python项目管理工具_2.1.0_交付物.zip"
```

---

## 三、执行顺序与依赖关系

```
Task 1 (版本号) ──┬──→ Task 3 (DB迁移) ──┐
                  │                       │
                  ├──→ Task 2 (归档) ─────┤
                  │                       ├──→ Task 5 (打包)
                  └──→ Task 4 (重命名) ───┘
```

**推荐执行顺序**:

1. ✅ **Task 1** - 版本号升级 (最先，因为打包依赖它)
2. ✅ **Task 2** - 旧文档归档 (独立，可与T1并行)
3. ✅ **Task 4** - 文件重命名 (独立，可与T1/T2并行)
4. ✅ **Task 3** - DB迁移脚本 (依赖T1完成)
5. ✅ **Task 5** - 重新打包 (依赖T1+T3+T4全部完成)

**预计时间**: 
- Task 1: ~5分钟
- Task 2: ~10分钟
- Task 3: ~20分钟 (含SQL映射逻辑验证)
- Task 4: ~15分钟 (含引用更新)
- Task 5: ~10分钟 (打包) + ~5分钟 (验证)

**总计**: ~65分钟 (不含调试时间)

---

## 四、验证标准

### 4.1 版本一致性验证

```bash
# 检查所有版本号是否一致
grep -r "V1\.0\." 01_项目文档/  # 应无结果 (或仅有归档文件)
grep -r "2\.1\.0" src/core/version.py  # 应匹配
grep -r "2\.1\.0" 01_项目文档/  # 应有多处匹配
```

### 4.2 数据库迁移验证

```bash
cd 03_主程序/01_主程序核心代码
alembic upgrade head  # 应用迁移
alembic current       # 应显示 v21_change_mgmt
alembic downgrade     # 回滚测试
alembic upgrade head  # 重新应用
```

然后检查 SQLite 数据库:
```bash
sqlite3 data/project_manager.db ".schema changes"  # 应包含24+列
```

### 4.3 打包验证

- [ ] exe 文件生成成功
- [ ] 启动无报错
- [ ] 关于对话框显示版本 2.1.0
- [ ] 变更管理模块正常加载 (9列表格 + 3筛选器)
- [ ] 新建项目时目录结构正确 (04_变更管理/01_变更单/{7领域})

### 4.4 文档完整性验证

- [ ] 旧文档已归档到 _archive/
- [ ] 台帐文件名已更新为 CHG-V2.1.0
- [ ] 交付清单中所有链接有效
- [ ] 无残留的 V1.0.x 版本号引用 (除 _archive/ 内)

---

## 五、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|:----:|:----:|:----:|:---------|
| 打包失败 (缺少依赖) | 低 | 🔴 高 | 提前运行 `pip install -r requirements.txt` |
| DB迁移失败 (旧数据冲突) | 中 | 🟡 中 | 迁移脚本使用 nullable + default; 先备份数据库 |
| 文件重命名导致链接断裂 | 低 | 🟡 中 | 全局搜索替换所有引用 |
| 版本号不一致 | 低 | 🟡 低 | 最终验证步骤会捕获 |

---

## 六、交付物清单 (完成后)

| # | 交付物 | 位置 | 状态 |
|:-:|:-------|:-----|:----:|
| 1 | version.py (V2.1.0) | src/core/ | 待生成 |
| 2 | v21_change_mgmt_upgrade.py | alembic/versions/ | 待生成 |
| 3 | _archive/ (归档目录) | 项目根/ | 待创建 |
| 4 | 06_版本变更台帐_CHG-V2.1.0.md | 01_项目文档/ | 待重命名 |
| 5 | 01_交付清单_DEL-V2.1.0.md | 06_交付物/ | 待重命名 |
| 6 | Python项目管理工具.exe (V2.1.0) | 06_交付物/01_可执行文件/ | 待打包 |
| 7 | Python项目管理工具_2.1.0_交付物.zip | 06_交付物/ | 可选 |

---

**计划版本**: V1.0.0
**编制人**: AI Assistant
**编制日期**: 2026-04-12
**状态**: 待用户确认后执行
