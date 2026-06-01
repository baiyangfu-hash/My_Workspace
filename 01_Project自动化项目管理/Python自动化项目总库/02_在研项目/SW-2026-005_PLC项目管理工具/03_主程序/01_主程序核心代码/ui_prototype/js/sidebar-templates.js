const sidebarTemplates = {
  dashboard: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('project')">
        <span class="arrow open" id="arrow-project">▶</span>
        <span class="section-icon">📁</span> 项目管理
      </button>
      <div class="sidebar-section-body" id="body-project">
        <div class="sidebar-item active" onclick="openTab('dashboard')">
          <span class="item-icon">📊</span> 项目仪表盘
        </div>
        <div class="sidebar-item" onclick="openTab('project', 'project-detail')">
          <span class="item-icon">📋</span> 项目详情
        </div>
        <div class="sidebar-item" onclick="onBrowseOpenProject()">
          <span class="item-icon">📂</span> 打开项目
        </div>
      </div>
    </div>
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('quick')">
        <span class="arrow open" id="arrow-quick">▶</span>
        <span class="section-icon">⚡</span> 快速操作
      </button>
      <div class="sidebar-section-body" id="body-quick">
        <div class="sidebar-item" onclick="openTab('document', 'doc-new')">
          <span class="item-icon">📝</span> 新建文档
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-run')">
          <span class="item-icon">🔍</span> 运行规范检查
        </div>
        <div class="sidebar-item" onclick="openTab('change', 'change-check')">
          <span class="item-icon">🔄</span> 版本同步检查
        </div>
      </div>
    </div>
  `,

  project: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('project')">
        <span class="arrow open" id="arrow-project">▶</span>
        <span class="section-icon">📁</span> 项目浏览
      </button>
      <div class="sidebar-section-body" id="body-project">
        <div class="sidebar-item" onclick="openTab('project', 'project-browse')">
          <span class="item-icon">🌳</span> 工作空间
          <span class="badge">3</span>
        </div>
        <div class="sidebar-item active" onclick="openTab('project', 'project-detail')">
          <span class="item-icon">📋</span> DJ-2026-005
        </div>
        <div class="sidebar-item" onclick="openTab('project', 'project-detail')">
          <span class="item-icon">📋</span> SW-2026-007
        </div>
        <div class="sidebar-item" onclick="openTab('project', 'project-detail')">
          <span class="item-icon">📋</span> SW-2026-008
        </div>
      </div>
    </div>
    <div class="sidebar-separator"></div>
    <div class="sidebar-item" onclick="openTab('project', 'project-new')">
      <span class="item-icon">➕</span> 新建项目...
    </div>
    <div class="sidebar-item" onclick="openTab('project', 'project-open')">
      <span class="item-icon">📂</span> 打开项目...
    </div>
    <div class="sidebar-item" onclick="showToast('请从仪表盘选择项目路径', 'info')">
      <span class="item-icon">🔌</span> 挂载工作空间...
    </div>
  `,

  document: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('templates')">
        <span class="arrow open" id="arrow-templates">▶</span>
        <span class="section-icon">📄</span> 文档模板
      </button>
      <div class="sidebar-section-body" id="body-templates">
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-1')">
          <span class="item-icon">📋</span> 项目计划书
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-2')">
          <span class="item-icon">📋</span> 功能规格说明
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-3')">
          <span class="item-icon">📋</span> 接口定义文档
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-4')">
          <span class="item-icon">📋</span> 测试计划
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-5')">
          <span class="item-icon">📋</span> 变更申请书
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-6')">
          <span class="item-icon">📋</span> 用户手册
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('doc-tpl-7')">
          <span class="item-icon">📋</span> 发布说明
        </div>
      </div>
    </div>
    <div class="sidebar-separator"></div>
    <div class="sidebar-item" onclick="openTab('document', 'doc-editor')">
      <span class="item-icon">✏️</span> 文档编辑器
    </div>
    <div class="sidebar-item" onclick="openTab('document', 'doc-new')">
      <span class="item-icon">➕</span> 从模板新建...
    </div>
    <div class="sidebar-item" onclick="onOpenDocument()">
      <span class="item-icon">💾</span> 打开文档...
    </div>
  `,

  'plc-tools': `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('tools')">
        <span class="arrow open" id="arrow-tools">▶</span>
        <span class="section-icon">⚡</span> PLC开发工具
      </button>
      <div class="sidebar-section-body" id="body-tools">
        <div class="sidebar-item active" onclick="openTab('plc-tools', 'plc-st-editor')">
          <span class="item-icon">📝</span> ST代码编辑器
        </div>
        <div class="sidebar-item" onclick="showPlaceholderView('plc-io')">
          <span class="item-icon">🔌</span> IO分配表
          <span style="font-size:10px;color:var(--text-muted);">开发中</span>
        </div>
        <div class="sidebar-item" onclick="openTab('plc-tools', 'plc-var-check')">
          <span class="item-icon">🔍</span> 变量检查器
        </div>
      </div>
    </div>
    <div class="sidebar-separator"></div>
    <div class="sidebar-item" onclick="openTab('plc-tools', 'plc-syslib')">
      <span class="item-icon">📚</span> SysLib库浏览器
    </div>
    <div class="sidebar-item" onclick="openTab('plc-tools', 'plc-fb-interface')">
      <span class="item-icon">🔗</span> FB接口检查
    </div>
  `,

  change: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('change')">
        <span class="arrow open" id="arrow-change">▶</span>
        <span class="section-icon">🔄</span> 变更管理
      </button>
      <div class="sidebar-section-body" id="body-change">
        <div class="sidebar-item active" onclick="openTab('change', 'change-list')">
          <span class="item-icon">📋</span> 变更单列表
          <span class="badge">5</span>
        </div>
        <div class="sidebar-item" onclick="openTab('change', 'change-new')">
          <span class="item-icon">➕</span> 新建变更单
        </div>
      </div>
    </div>
    <div class="sidebar-separator"></div>
    <div class="sidebar-item" onclick="openTab('change', 'change-check')">
      <span class="item-icon">🔍</span> 版本同步检查
    </div>
    <div class="sidebar-item" onclick="openTab('change', 'change-chg')">
      <span class="item-icon">📝</span> 生成CHG文档
    </div>
    <div class="sidebar-item" onclick="openTab('change', 'change-ifc')">
      <span class="item-icon">📝</span> 生成IFC文档
    </div>
    <div class="sidebar-item" onclick="openTab('change', 'change-report')">
      <span class="item-icon">📊</span> 同步报告
    </div>
  `,

  spec: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('spec-checkers')">
        <span class="arrow open" id="arrow-spec-checkers">▶</span>
        <span class="section-icon">✅</span> 检查器
        <span class="badge">7</span>
      </button>
      <div class="sidebar-section-body" id="body-spec-checkers">
        <div class="sidebar-item active" onclick="openTab('spec', 'spec-run')">
          <span class="item-icon">🔍</span> 选择检查器
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-syntax')">
          <span class="item-icon">📝</span> 语法检查
          <span class="badge badge-trae">Trae</span>
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-comment')">
          <span class="item-icon">💬</span> 注释检查
          <span class="badge badge-trae">Trae</span>
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-naming')">
          <span class="item-icon">🏷</span> 命名规范
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-var')">
          <span class="item-icon">📦</span> 变量检查
          <span class="badge badge-hybrid">混合</span>
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-config')">
          <span class="item-icon">⚙</span> 配置检查
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-timer')">
          <span class="item-icon">⏱</span> 定时器检查
        </div>
        <div class="sidebar-item" onclick="openTab('spec', 'spec-fb-iface')">
          <span class="item-icon">🔗</span> FB接口调用
          <span class="badge badge-hybrid">混合</span>
        </div>
      </div>
    </div>
    <div class="sidebar-separator"></div>
    <div class="sidebar-item" onclick="openTab('spec', 'spec-auto-fix')">
      <span class="item-icon">🔧</span> 自动修复
    </div>
    <div class="sidebar-item" onclick="openTab('spec', 'spec-excel')">
      <span class="item-icon">📊</span> Excel导出
    </div>
  `,

  settings: `
    <div class="sidebar-section">
      <button class="sidebar-section-header" onclick="toggleSection('settings-group')">
        <span class="arrow open" id="arrow-settings-group">▶</span>
        <span class="section-icon">⚙</span> 设置
      </button>
      <div class="sidebar-section-body" id="body-settings-group">
        <div class="sidebar-item active" onclick="openTab('settings', 'settings-general')">
          <span class="item-icon">🖥</span> 常规设置
        </div>
        <div class="sidebar-item" onclick="openTab('settings', 'settings-editor')">
          <span class="item-icon">📝</span> 编辑器
        </div>
        <div class="sidebar-item" onclick="openTab('settings', 'settings-appearance')">
          <span class="item-icon">🎨</span> 外观
        </div>
        <div class="sidebar-item" onclick="openTab('settings', 'settings-shortcuts')">
          <span class="item-icon">⌨</span> 快捷键
        </div>
      </div>
    </div>
  `
};
