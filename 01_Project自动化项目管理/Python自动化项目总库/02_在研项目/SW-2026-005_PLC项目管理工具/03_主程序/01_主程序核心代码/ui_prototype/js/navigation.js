function switchActivity(view) {
  state.activeActivity = view;

  document.querySelectorAll('.activity-item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === view);
  });

  const titles = {
    dashboard: '仪表盘',
    project: '项目管理',
    document: '文档管理',
    'plc-tools': 'PLC工具',
    change: '变更管理',
    spec: '规范中心',
    settings: '设置'
  };
  document.getElementById('sidebarTitle').textContent = titles[view] || '';
  document.getElementById('sidebarContent').innerHTML = sidebarTemplates[view] || '';

  const tabMap = {
    dashboard: 'dashboard',
    project: 'project-detail',
    document: 'doc-editor',
    'plc-tools': 'plc-st-editor',
    change: 'change-list',
    spec: 'spec-run',
    settings: 'settings-general'
  };
  if (tabMap[view]) openTab(view, tabMap[view]);
}

function openTab(view, tabId) {
  if (!state.openTabs.includes(tabId)) {
    state.openTabs.push(tabId);
  }
  state.activeTab = tabId;
  state.activeActivity = view;

  document.querySelectorAll('.activity-item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === view);
  });

  const titles = {
    dashboard: '仪表盘',
    project: '项目管理',
    document: '文档管理',
    'plc-tools': 'PLC工具',
    change: '变更管理',
    spec: '规范中心',
    settings: '设置'
  };
  document.getElementById('sidebarTitle').textContent = titles[view] || '';
  document.getElementById('sidebarContent').innerHTML = sidebarTemplates[view] || '';

  renderTabBar();
  renderContent(tabId);
}

const tabNames = {
  'dashboard': '📊 仪表盘',
  'project-detail': '📋 项目详情',
  'project-new': '➕ 新建项目',
  'project-browse': '🌳 工作空间浏览',
  'project-open': '📂 打开项目',
  'doc-editor': '📝 文档编辑器',
  'doc-new': '➕ 新建文档',
  'change-list': '🔄 变更单列表',
  'change-new': '➕ 新建变更单',
  'change-check': '🔍 版本同步',
  'change-chg': '📝 CHG文档',
  'change-ifc': '📝 IFC文档',
  'change-report': '📊 同步报告',
  'plc-st-editor': '📝 ST编辑器',
  'plc-var-check': '🔍 变量检查',
  'plc-syslib': '📚 SysLib库',
  'plc-fb-interface': '🔗 FB接口检查',
  'spec-run': '✅ 选择检查器',
  'spec-naming': '🏷 命名规范',
  'spec-syntax': '📝 语法检查',
  'spec-comment': '💬 注释检查',
  'spec-config': '⚙ 配置检查',
  'spec-timer': '⏱ 定时器检查',
  'spec-var': '📦 变量检查',
  'spec-fb-iface': '🔗 FB接口调用',
  'spec-auto-fix': '🔧 自动修复',
  'spec-excel': '📊 Excel导出',
  'settings-general': '⚙ 常规设置',
  'settings-editor': '📝 编辑器',
  'settings-appearance': '🎨 外观',
  'settings-shortcuts': '⌨ 快捷键',
};

function renderTabBar() {
  const bar = document.getElementById('tabBar');
  bar.innerHTML = state.openTabs.map(id => `
    <div class="tab-item ${id === state.activeTab ? 'active' : ''}" onclick="selectTab('${id}')">
      ${tabNames[id] || id}
      ${id !== 'dashboard' ? `<span class="tab-close" onclick="event.stopPropagation();closeTab('${id}')">✕</span>` : ''}
    </div>
  `).join('');
}

function selectTab(tabId) {
  state.activeTab = tabId;
  renderTabBar();
  renderContent(tabId);
}

function closeTab(tabId) {
  const idx = state.openTabs.indexOf(tabId);
  if (idx > -1) state.openTabs.splice(idx, 1);
  if (state.openTabs.length === 0) state.openTabs = ['dashboard'];
  if (state.activeTab === tabId) {
    state.activeTab = state.openTabs[Math.min(idx, state.openTabs.length - 1)];
  }
  renderTabBar();
  renderContent(state.activeTab);
}

function renderContent(tabId) {
  const container = document.getElementById('contentMain');
  switch (tabId) {
    case 'dashboard': container.innerHTML = renderDashboard(); break;
    case 'project-detail': container.innerHTML = renderProjectDetail(); break;
    case 'doc-editor': case 'doc-new': container.innerHTML = renderDocumentEditor(); break;
    case 'change-list': container.innerHTML = renderChangeList(); break;
    case 'spec-run': container.innerHTML = renderSpecCheck(); break;
    case 'settings-general': container.innerHTML = renderSettings(); break;
    case 'plc-st-editor':
      container.innerHTML = renderPlaceholder('ST代码编辑器', '语法高亮SCL/ST编辑器，支持代码折叠和智能提示');
      break;
    case 'plc-var-check':
      container.innerHTML = renderPlaceholder('变量检查器', '检查项目中变量命名规范和使用情况');
      break;
    case 'project-new':
      container.innerHTML = renderPlaceholder('新建项目', '项目创建向导 — 选择类型/模板并配置基本参数');
      break;
    case 'spec-auto-fix':
      container.innerHTML = renderAutoFix();
      break;
    case 'spec-excel':
      container.innerHTML = renderExcelExport();
      break;
    default:
      container.innerHTML = renderPlaceholder(tabId.replace(/-/g, ' '), '该功能正在开发中，敬请期待。');
  }
}

function showPlaceholderView(id) {
  openTab(state.activeActivity, id);
}
