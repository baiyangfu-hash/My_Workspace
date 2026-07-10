# HTML 原型 V7 架构深度解读

**生成时间**: 2026-07-08  
**版本**: V7 (最新)  
**文件**: 012_UI架构原型_V7.html

---

## 一、原型设计理念

### 1.1 定位

- **NOT** 生产代码
- **YES** 方案验证 + 交互讨论 + 高保真演示

### 1.2 为什么需要 HTML 原型？

```
PLC 工程 → 电气图纸草图 → TIA Portal 正式设计
auto-pm   → HTML 原型   → QML/Web 生产实现
```

**HTML 原型用途**:
1. 快速验证页面流程
2. 与产品/工程师讨论 UX
3. 明确信息架构
4. 性能基线评估

### 1.3 V7 相比 V6 的改进

| 方面 | V6 | V7 |
|------|----|----|
| 导航结构 | 二层 | **三层** (Platform/Workspace/Project) |
| 异步加载 | 无 | **Loading Overlay** |
| 菜单组织 | 扁平 | **按业务线分组** |
| 原型标注 | 缺少 | **"M4 迭代解锁"提示** |
| 资产摘要 | 无 | **新增 Asset Summary 模块** |

---

## 二、视觉设计系统

### 2.1 色彩体系 (深色玻璃拟物)

```css
/* 基础色 */
--bg-base: #020617;           /* 深蓝黑 */
--bg-gradient-1: #1e1b4b;    /* 紫黑 */
--bg-gradient-2: #0f172a;    /* 极深蓝 */

/* 功能色 */
--primary: #6366f1;           /* 靛蓝 - 主交互 */
--secondary: #38bdf8;         /* 天蓝 - 次级 */
--success: #10b981;           /* 绿 - 成功 */
--warning: #f59e0b;           /* 橙 - 警告 */
--danger: #ef4444;            /* 红 - 错误 */

/* 毛玻璃效果 */
--glass-bg: rgba(255, 255, 255, 0.03);
--glass-border: rgba(255, 255, 255, 0.08);
backdrop-filter: blur(16px);
```

**对比度**:
- ✅ WCAG AA 通过
- ✅ 高保真打印效果

### 2.2 排版体系

```css
字体族: 'Inter', "Microsoft YaHei", sans-serif
  └─ 优先使用 Inter 确保细节锐利
  └─ 降级到中文字体保证可读性

尺寸阶梯:
  标题1: 24px / 600 (H1)
  标题2: 15px / 600 (H3)
  正文:  14px / 400
  描述:  13px / 400
  标签:  11px / 500
```

### 2.3 间距单位

```
4px 基础单位
  ├─ gap: 8px (element 内)
  ├─ padding: 16px
  ├─ margin: 24px (section)
  └─ gap: 20px (card grid)
```

---

## 三、布局架构

### 3.1 整体框架 (Shell)

```html
<body>
  <!-- 光晕背景 -->
  <div class="ambient-orb orb-1"></div>
  <div class="ambient-orb orb-2"></div>
  
  <!-- 侧边栏 -->
  <aside class="sidebar">
    <!-- PLATFORM COCKPIT -->
    <!-- WORKSPACE -->
    <!-- ACTIVE PROJECT -->
    <!-- Settings -->
  </aside>
  
  <!-- 主内容区 -->
  <main class="main-content">
    <header class="header">  <!-- 72px 高 -->
      <search-bar />
      <actions />
    </header>
    
    <div id="app-view" class="router-view">
      <!-- 动态内容挂载点 -->
    </div>
  </main>
</body>
```

**宽度分配**:
```
Sidebar: 280px (固定)
Header:  72px (固定)
Content: 剩余 (自适应)
```

### 3.2 侧边栏结构 (Sidebar)

```
┌─────────────────────┐
│  Logo + Brand       │ (72px)
├─────────────────────┤
│                     │
│ Platform Cockpit    │ ← 平台自身研发管控
│ ├─ Dashboard        │
│ ├─ Changes          │
│ ├─ Specs            │
│ └─ Delivery         │
│                     │
├─────────────────────┤ (分隔线)
│                     │
│ Workspace           │ ← 桥梁 (业务项目)
│ ├─ Projects         │
│                     │
├─────────────────────┤ (分隔线)
│                     │
│ Active Project      │ ← 具体业务工程
│ ├─ Health Overview  │
│ ├─ Variables        │
│ ├─ Changes          │
│ ├─ Specs            │
│ └─ Delivery         │
│                     │
├─────────────────────┤
│                     │
│ Settings            │ ← 全局配置
│                     │
├─────────────────────┤
│ Backend Status      │ ← 连接状态
└─────────────────────┘
```

**特点**:
- 三轨道设计
- Context Card 展示当前项目
- Badge 显示待办数
- 连接状态实时反馈

### 3.3 内容路由 (Router View)

```javascript
// 路由表
const ROUTES = {
  'platform-dashboard': 'view-platform-dashboard',
  'platform-changes': 'view-platform-changes',
  'platform-specs': 'view-platform-specs',
  'platform-delivery': 'view-platform-delivery',
  'projects': 'view-projects',
  'project-dashboard': 'view-project-dashboard',
  'vartables': 'view-vartables',
  'project-changes': 'view-project-changes',
  'project-specs': 'view-project-specs',
  'project-delivery': 'view-project-delivery',
  'settings': 'view-settings',
};

// 导航触发
nav-item.onclick → app.navigate(route)
  → app.viewContainer.innerHTML = template
  → app.init_[route_name]() // 初始化逻辑
```

---

## 四、核心模块深度剖析

### 4.1 驾驶舱 (Dashboard)

#### 信息架构

```
┌─────────────────────────────────────────┐
│ 页面头 (Page Header)                     │
│ - 标题: SW-2026-008_auto-pm...          │
│ - 面包屑: Python项目/02_在研/SW-2026-008│
│ - 操作: CLI终端 / 资源管理器打开         │
└─────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ KPI 网格 (4列)                            │
├───────────────┬───────────────┐          │
│ 开发阶段      │ 技术债        │          │
│ Developing    │ 0 项          │          │
├───────────────┼───────────────┤          │
│ 测试通过率    │ 活跃变更单    │          │
│ 100%          │ CHG-102       │          │
└───────────────┴───────────────┘          │
```

#### 组件

##### KPI Card

```html
<div class="kpi-card glass-panel">
  <div class="kpi-header">
    <label>当前开发阶段</label>
    <icon>🚩</icon>
  </div>
  <div class="kpi-value">Developing</div>
  <div class="kpi-subtitle">距上个 Milestone (V0.9.2) 已过去 1 天</div>
</div>
```

**特性**:
- Hover 上浮动画
- 顶部渐变线
- 3 行内容垂直布局

##### 状态机 (State Machine View)

```
需求澄清 ──→ 方案评审 ──→ 实施中 ──→ 闭环归档
  ✓          ✓         ◉ (当前) 
  
┴──────────── 进度条 50% ──────────┬────────┴
```

**实现**:
```javascript
// 状态节点
.sm-node {
  position: relative;
  cursor: pointer;
  transition: all 0.3s;
}

.sm-node.done .sm-circle {
  background: rgba(16, 185, 129, 0.1);  // 绿色
  border-color: #10b981;
}

.sm-node.active .sm-circle {
  animation: pulse 2s infinite;  // 脉冲动画
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
}
```

##### 时间线 (Activity Timeline)

```
● 状态流转: Review -> Implementing
  CHG-102 开始实施 V2 UI 架构重构
  10:45 AM
  
─────────── (连接线) ───────────
  
● 代码规范告警
  LSP 检测到 VarTableEditorView.qml 存在 undefined 风险
  昨天 16:30
```

**实现**:
```css
.timeline-item {
  display: flex;
  gap: 16px;
  position: relative;
}

/* 连接线 */
.timeline-item::before {
  position: absolute;
  left: 5px;
  top: 20px;
  bottom: -20px;
  width: 1px;
  background: var(--glass-border);
}

/* 圆点 */
.timeline-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px var(--primary);
  margin-top: 4px;
  position: relative;
  z-index: 2;  /* 覆盖连接线 */
}
```

### 4.2 变更中心 (Changes Split View)

#### 二分屏设计

```
┌────────────────────────────────────────┐
│ 标题 + 视图切换                         │
├─────────────────┬──────────────────────┤
│                 │                      │
│ 列表区          │  详情区              │
│ (380px fixed)   │  (flex 1)            │
│                 │                      │
│ □ CHG-102       │ CHG-102             │
│   UI架构原型    │ UI架构原型 V2 重构  │
│   Implementing  │                      │
│                 │ 创建人: fubai       │
│ □ CHG-101       │ 创建日期: 2026-07-08│
│   治理收口      │                      │
│   Closed        │ 变更描述            │
│                 │ ...                  │
│ □ CHG-080       │ 实施记录            │
│   变量表整合    │ [2026-07-08 10:00]  │
│   Implementing  │ ...                  │
└─────────────────┴──────────────────────┘
```

#### 视图切换

```javascript
// Toggle Between Split View & Ledger
btn-view-split.onclick → toggleChangeView('split')
  └─ #change-view-split.style.display = 'flex'
  └─ #change-view-ledger.style.display = 'none'
  └─ btn-split.style.background = 'var(--primary)'

btn-view-ledger.onclick → toggleChangeView('ledger')
  └─ #change-view-split.style.display = 'none'
  └─ #change-view-ledger.style.display = 'flex'
  └─ btn-ledger.style.background = 'var(--primary)'
```

#### 列表项交互

```javascript
// Click to show detail
list-item.onclick → showChangeDetail(changeId)
  ├─ 查询数据库: const change = Database.changes.find(...)
  ├─ 构造 HTML: detailView.innerHTML = `...`
  └─ 渲染到详情区
```

### 4.3 变量表管理 (Asset Summary)

#### 新增模块 (V7)

```html
<template id="view-vartables">
  <page-header />
  
  <!-- 资产卡片网格 -->
  <grid-4col>
    <asset-card>
      <icon>🖥️</icon>
      <label>Function Blocks (FB)</label>
      <value>124</value>
    </asset-card>
    ...
  </grid-4col>
  
  <!-- 健康度分布图 -->
  <health-bar>
    <progress style="width:70%">正常挂载</progress>
    <progress style="width:20%">孤儿变量</progress>
    <progress style="width:10%">映射断裂</progress>
  </health-bar>
  
  <!-- 未来功能提示 -->
  <future-capability>
    <icon>🔒</icon>
    <h3>详细变量表映射编辑</h3>
    <button disabled>进入变量矩阵视图</button>
  </future-capability>
</template>
```

#### Future Capability 设计模式

```css
.future-capability {
  border: 1px dashed rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.02);
  position: relative;
  overflow: hidden;
}

.future-capability::before {
  content: '🚀 M4 迭代解锁 / Plugin Required';
  position: absolute;
  top: 12px;
  right: -30px;
  background: var(--warning);
  transform: rotate(45deg);
  font-size: 10px;
  font-weight: bold;
}
```

**作用**:
- 👁️ 向用户展示路线图
- 📋 预留扩展槽位
- 🔐 禁用按钮表达状态

### 4.4 项目变更控制矩阵 (Impact Analysis Tab)

#### 影响分析展示

```
┌─────────────────────────────────────┐
│ CHG-PLC-2026-001 影响分析演示       │
├──────────────────┬──────────────────┤
│ 左侧              │ 右侧             │
├──────────────────┼──────────────────┤
│ 风险等级: High   │ 缓解措施:         │
│                  │ 强制运行         │
│ 约束影响:        │ HMI_Tag_Sync     │
│ □ 排期: 低       │ 工具；执行全量   │
│ □ 成本: 无       │ 变量地址回归测试 │
│ □ 质量: 高       │                  │
│                  │ 受限领域波及:    │
│ 传播链路:        │ □ PLC:           │
│ FB_ValveControl  │   FB_ValveControl│
│ → Global_Vars    │ □ HMI:           │
│ → HMI_Tags       │   Screen_Main    │
└──────────────────┴──────────────────┘
```

### 4.5 规范检查 (Specs Center)

#### 进度反馈

```html
<div class="progress-container">
  <div class="progress-label">
    <span>健康度扫描进度</span>
    <span id="scan-pct">100% (2 项违规未修复)</span>
  </div>
  <div class="progress-bar">
    <div id="scan-bar" style="width: 100%; background: var(--warning)"></div>
  </div>
</div>
```

#### 扫描结果表格

```
┌──────────────┬─────────────────────────┬──────────────┬──────────┬──────────┐
│ 规则编号     │ 规则描述                 │ 定位点       │ 状态     │ 操作     │
├──────────────┼─────────────────────────┼──────────────┼──────────┼──────────┤
│ LSP-SCL-001  │ FB 内部变量前缀检查      │ ...L24       │ ❌ 违规  │ Auto Fix │
│ LSP-DB-015   │ DB 优化块访问检查        │ HMI_Data.db  │ ❌ 违规  │ Auto Fix │
│ LSP-DOC-003  │ PM_SESSION 章节检查      │ PM_SESSION.md│ ✅ 通过  │ -        │
└──────────────┴─────────────────────────┴──────────────┴──────────┴──────────┘
```

---

## 五、交互模式总结

### 5.1 标准流程 (Standard Workflows)

#### 创建变更单流程

```
User Click "新建" 
  → Modal: "请选择创建的类型"
  → Select "工程变更单"
  → MultiStep Dialog:
    Step 1: 基本信息 (标题、域、紧急程度)
    Step 2: 描述字段 (背景、必要性、风险)
    Step 3: 确认 & 提交
  → CHG-*.md 文件生成
  → 列表刷新
```

#### 状态流转流程

```
User Click "流转阶段" on Active Change
  → Guard Check: 是否有权限？是否满足前置条件？
  → State Machine Popup: 显示可达状态
  → User Select Target State
  → Updated PM_SESSION + DB
  → Timeline 更新
  → UI 刷新
```

### 5.2 模态交互 (Modal Pattern)

```javascript
class ModalManager {
  showModal(title, body, onConfirm) {
    $('#modal-title').textContent = title;
    $('#modal-body').textContent = body;
    $('#sys-modal').classList.add('active');
    
    // 点击背景或取消按钮时关闭
    modal.onclick = (e) => {
      if (e.target === modal) this.closeModal();
    };
  }
  
  closeModal() {
    $('#sys-modal').classList.remove('active');
  }
}
```

**用途**:
- ✅ 确认删除
- ✅ 提示后台操作中
- ✅ 输入验证

### 5.3 异步加载状态 (V7 新增)

```html
<div class="loading-overlay active">
  <div class="spinner"></div>
  <p>正在扫描工作区...</p>
</div>
```

```css
.loading-overlay {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.loading-overlay.active {
  opacity: 1;
  pointer-events: all;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}
```

---

## 六、数据流示意图

### 6.1 单向数据流

```
┌──────────────┐
│ Mock Database│
│ (JavaScript) │
└────────┬─────┘
         │ (模拟)
         ↓
┌──────────────────┐
│ Application      │
│ (Controller)     │
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│ View             │
│ (Render)         │
└──────────────────┘
```

### 6.2 用户交互流

```
User Action
  ↓
.onclick / form.onsubmit
  ↓
app.method()
  ↓
Update Database / DOM
  ↓
Re-render View
```

---

## 七、性能优化亮点

### 7.1 CSS 优化

```css
/* 使用 CSS 变量减少重复 */
:root {
  --primary: #6366f1;
  --radius-lg: 16px;
  --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 避免 expensive repaints */
.kpi-card {
  will-change: transform;  /* GPU 加速 */
}

/* 预加载字体 */
<link rel="preconnect" href="https://fonts.gstatic.com">
```

### 7.2 JavaScript 优化

```javascript
// 事件委托而非逐个绑定
document.on('click', '.nav-item', (e) => { ... });

// 防抖模式
const debounce = (fn, delay) => {
  let timer;
  return () => {
    clearTimeout(timer);
    timer = setTimeout(fn, delay);
  };
};

search.oninput = debounce(() => updateList(), 300);
```

### 7.3 Lighthouse 评分

| 指标 | 目标 | 预期 |
|------|------|------|
| Performance | >90 | 95 (纯 HTML/CSS/JS) |
| Accessibility | >90 | 92 (高对比度) |
| Best Practices | >90 | 93 |
| SEO | N/A | - |

---

## 八、向 QML/Web 的转化指南

### 8.1 组件映射表

| HTML 原型 | QML 组件 | Web (React) |
|-----------|----------|------------|
| `.glass-panel` | Rectangle + opacity | `<div className="glass">` |
| `.sidebar` | ListView | `<nav>` |
| `.kpi-card` | GridLayout + Text | `<Card />` |
| `.sm-node` | Canvas + Mouse | SVG |
| `.modal-overlay` | Dialog | `<Dialog />` |
| `.data-table` | TableView | `<DataTable />` |

### 8.2 复用机制

- ✅ CSS 变量 → 直接用于 QML Theme
- ✅ 布局比例 → 转换为 Qt Layouts
- ✅ 交互动画 → 用 QML Behavior 或 CSS Animation
- ✅ 颜色系统 → Pydantic ColorModel → QML Palette

### 8.3 迁移检查表

- [ ] 所有页面路由已定义
- [ ] 所有数据模型已序列化为 DTO
- [ ] 所有用户交互已转换为 Command
- [ ] 所有异步操作已适配 async/await
- [ ] 所有样式已参数化为主题变量

---

## 九、设计文档位置

所有相关文档存储在:
```
02_设计/
├── 001_产品需求文档_PRD.md         # 产品定义
├── 002_接口文档_INT.md             # 接口契约
├── 003_详细设计说明书_DSN.md       # 架构细节
├── 004_技术方案文档_TEC.md         # 技术决策
├── 005_里程碑与实施计划.md         # M0-M9 规划
├── 006_UI架构原型.html             # 旧原型
├── 007_UI架构原型说明.md           # 原型说明
└── Html原型预览/
    ├── 012_UI架构原型_V7.html      # 最新 ✅
    ├── 011_UI架构原型_V6.html
    └── ...
```

---

## 十、总结

**V7 HTML 原型**是 auto-pm 的交互设计真源，展示了：

1. ✅ **三轨道导航** (Platform/Workspace/Project)
2. ✅ **六工作域** (Dashboard/Changes/Specs/Delivery/Assets/Settings)
3. ✅ **深色玻璃拟物** 视觉风格
4. ✅ **状态机可视化** + 时间线
5. ✅ **影响分析矩阵** 展示
6. ✅ **未来功能提示** (M4 解锁)
7. ✅ **异步加载反馈**

**下一步**:
- QML 页面按 V7 样式渲染
- Web 化时复用 CSS 变量系统
- Contract 接口继续保持稳定
