# PLCPM "能使用级" 开发计划 v0.2.0

## 一、目标定义

### "能使用"的标准
用户打开GUI后可以：
1. ✅ 看到项目列表（表格形式，显示编号/名称/业务线/负责人/状态）
2. ✅ 通过对话框创建新项目（选择模板 → 填写信息 → 生成目录）
3. ✅ 编辑/删除已有项目
4. ✅ 查看模板列表和内置模板详情
5. ✅ 查看变更记录列表
6. ✅ CLI命令行完全可用
7. ✅ API接口可调用

### Trae国际版分工
- **当前环境**: 完成核心UI组件、模板渲染器、基础集成测试
- **Trae国际版**: 补完高层功能（PLC/HMI/Robot管理）、纠错优化、性能调优

---

## 二、开发任务清单

### Phase A: Application初始化增强 (优先级: P0)

#### Task A1: 集成种子数据初始化到 Application
**文件**: `src/core/app.py`
**修改内容**:
- 在 `initialize()` 方法末尾添加 `SeedService.initialize_builtin_templates()` 调用
- 导入 SeedService
- 添加初始化日志输出

**验证**: 启动时自动创建内置模板到数据库

---

### Phase B: UI组件实现 (优先级: P0)

#### Task B1: 创建 ProjectListWidget 项目列表组件
**新建文件**: `src/ui/widgets/project_list_widget.py`

**功能要求**:
```
┌─────────────────────────────────────────────────────────────┐
│ 项目管理                                              [搜索框] │
├──────┬───────────────┬──────────┬────────┬────────┬─────────┤
│ 编号  │ 名称          │ 业务线   │ 负责人  │ 状态   │ 操作    │
├──────┼───────────────┼──────────┼────────┼────────┼────────┼─────────┤
│DJ... │ 测试设备A     │ DJ       │ 张三    │ ACTIVE │ 编辑 删除│
│ZD... │ 自动化线B     │ ZD       │ 李四    │ ACTIVE │ 编辑 删除│
└──────┴───────────────┴──────────┴────────┴────────┴────────┴─────────┘
                                    [共 N 个项目]
```

**API设计**:
```python
class ProjectListWidget(QWidget):
    def __init__(self, parent=None): ...
    def refresh(self): ...           # 刷新列表
    def get_selected_project_id(self) -> str: ...  # 获取选中项ID
    def on_create_project(self): ...    # 触发创建信号
    def on_edit_project(self): ...      # 触发编辑信号
    def on_delete_project(self): ...   # 触发删除信号
    
    signal = {
        'project_created': (str,),       # project_id
        'project_updated': (str,),       # project_id
        'project_deleted': (str,)        # project_id
    }
```

**依赖**: ProjectService, ProjectModel

---

#### Task B2: 创建 ProjectDialog 项目编辑对话框
**新建文件**: `src/ui/dialogs/project_dialog.py`

**功能要求**:
- 模态对话框
- 表单字段: 名称(必填)、业务线(下拉)、模板(下拉)、负责人、描述
- 校验: 名称非空、必须选模板
- 调用 ProjectService.create_project() 或 update_project()

**两种模式**:
- **创建模式**: 无初始数据，调用 create_project()
- **编辑模式**: 加载现有数据，调用 update_project()

**依赖**: ProjectService, TemplateService, BusinessLine枚举

---

#### Task B3: 创建 TemplateListWidget 模板列表组件
**新建文件**: `src/ui/widgets/template_list_widget.py`

**功能要求**:
- 显示所有可用模板（表格或卡片视图）
- 区分内置/自定义模板（图标标识）
- 显示模板名称、版本、适用场景、适用业务线
- 右键菜单: 查看详情 / 预览结构

**依赖**: TemplateService

---

#### Task B4: 创建 ChangeListWidget 变更记录组件
**新建文件**: `src/ui/widgets/change_list_widget.py`

**功能要求**:
- 表格显示变更单: 标题/类型/状态/申请人/日期
- 状态颜色编码:
  - DRAFT: 灰色
  - PENDING: 黄色
  - APPROVED: 绿色
  - IMPLEMENTED: 蓝色
  - CLOSED: 灰色
  - REJECTED: 红色
- 筛选栏: 按项目/状态/类型筛选

**依赖**: ChangeService, ChangeType/ChangeStatus枚举

---

#### Task B5: 集成组件到 MainWindow
**修改文件**: `src/ui/main_window.py`

**修改内容**:
- 将 Tab 0 的空 QWidget 替换为 ProjectListWidget
- 将 Tab 1 替换为 TemplateListWidget
- 将 Tab 2 替换为 ChangeListWidget
- 连接工具栏按钮到对应组件方法
- 连接菜单项到对应操作
- 实现 on_new_project() 打开 ProjectDialog

---

### Phase C: 模板渲染器 (优先级: P0)

#### Task C1: 创建模板渲染器
**新建文件**: `src/core/template_renderer.py`

**功能要求**:
```python
class TemplateRenderer:
    @staticmethod
    def render_directory_structure(structure: dict, base_path: Path) -> List[Path]:
        """
        基于模板结构定义创建目录
        
        Args:
            structure: 模板的 structure JSON
            base_path: 目标根路径
            
        Returns:
            List[Path]: 创建的文件/目录列表
        """
    
    @staticmethod
    def render_file_template(template_content: str, variables: dict) -> str:
        """
        渲染文件模板（简单变量替换）
        
        支持变量: {code}, {name}, {date}, {manager} 等
        """
```

**使用场景**: 用户创建项目后，自动在 Projects/{code}/ 下生成标准目录结构

---

#### Task C2: 集成模板渲染到项目创建流程
**修改文件**: `src/services/project_service.py` 或新建 `src/services/project_creator_service.py`

**新增功能**:
- `create_project_from_template()` 方法
- 步骤:
  1. 调用 create_project() 创建数据库记录
  2. 调用 TemplateRenderer 生成目录结构
  3. 返回项目对象 + 创建的文件列表

---

### Phase D: 文档同步 (优先级: P1)

#### Task D1: 更新 README.md
**修改文件**: `README.md`
**新增内容**:
- v0.2.0 功能清单
- UI截图说明（文字描述）
- 四种启动方式的详细说明
- 新增文件清单

#### Task D2: 更新 SPEC.md
**修改文件**: `docs/SPEC.md`
**新增内容**:
- M01-M06 功能点完成状态更新
- 新增 UI 组件规格
- 新增模板渲染器规格

#### Task D3: 更新 verify_project.py
**修改文件**: `verify_project.py`
**新增检查项**:
- widgets/ 目录存在性
- dialogs/ 目录存在性
- template_renderer.py 存在性

---

### Phase E: 基础集成测试 (优先级: P1)

#### Task E1: UI组件单元测试
**新建文件**: `tests/test_ui/test_widgets.py`

**测试内容**:
- ProjectListWidget 可实例化
- ProjectDialog 可打开/关闭
- 信号连接正确

#### Task E2: 端到端集成测试
**新建文件**: `tests/test_integration/test_full_flow.py`

**测试场景**:
1. 启动应用 → 自动初始化模板
2. GUI创建项目 → 验证数据库记录
3. GUI编辑项目 → 验证数据更新
4. GUI删除项目 → 验证软删除

---

## 三、Token预算估算

| 任务 | Token估算 | 优先级 |
|------|-----------|--------|
| A1: Application初始化 | 3,000 | P0 |
| B1: ProjectListWidget | 15,000 | P0 |
| B2: ProjectDialog | 12,000 | P0 |
| B3: TemplateListWidget | 10,000 | P0 |
| B4: ChangeListWidget | 8,000 | P0 |
| B5: MainWindow集成 | 5,000 | P0 |
| C1: 模板渲染器 | 8,000 | P0 |
| C2: 项目创建集成 | 7,000 | P0 |
| D1-D3: 文档更新 | 5,000 | P1 |
| E1-E2: 集成测试 | 12,000 | P1 |
| **总计** | **~85,000** | |

---

## 四、执行顺序

```
Step 1: A1 (初始化增强)
         ↓
Step 2: C1 (模板渲染器) ──→ 并行 Step 3
         ↓                    ↓
Step 3: B1+B2 (项目和对话框)     Step 4: B3+B4 (模板+变更)
         ↓                    ↓
         └────────→ Step 5: B5 (主窗口集成)
                    ↓
              Step 6: C2 (创建流程集成)
                    ↓
              Step 7: D1-D3 (文档同步)
                    ↓
              Step 8: E1-E2 (测试)
```

---

## 五、交付物清单

### 新建文件 (11个)
```
src/ui/widgets/
├── __init__.py
├── project_list_widget.py      # 项目列表组件
├── template_list_widget.py     # 模板列表组件
└── change_list_widget.py       # 变更记录组件

src/ui/dialogs/
├── __init__.py
└── project_dialog.py          # 项目编辑对话框

src/core/
└── template_renderer.py         # 模板渲染器

tests/test_ui/
├── __init__.py
└── test_widgets.py             # UI组件测试

tests/test_integration/
├── __init__.py
└── test_full_flow.py           # 端到端测试
```

### 修改文件 (5个)
```
src/core/app.py                  # 集成种子数据
src/ui/main_window.py           # 集成UI组件
src/services/project_service.py # 新增创建流程
README.md                        # 更新文档
docs/SPEC.md                     # 更新规格
verify_project.py               # 更新验证脚本
```

---

## 六、验收标准

### 功能验收
- [ ] `python -m src.ui.main_window` 启动GUI
- [ ] 主窗口显示项目列表Tab（含示例数据或空表）
- [ ] 点击"新建项目"弹出对话框，填写后可创建
- [ ] 项目列表实时刷新
- [ ] 可切换到模板/变更Tab查看数据
- [ ] 状态栏显示正确信息
- [ ] `python -m src.cli.main --help` CLI正常工作
- [ ] API `/api/projects` 返回正确JSON

### 代码质量
- [ ] 无循环导入
- [ ] 无硬编码路径
- [ ] 所有public方法有docstring
- [ ] pytest tests/ 至少通过20个测试

### 文档完整性
- [ ] README 反映v0.2.0功能
- [ ] SPEC 更新功能点状态
- [ ] verify_project 覆盖新组件

---

**计划版本**: v0.2.0  
**编制日期**: 2026-04-21  
**状态**: 待确认后执行
