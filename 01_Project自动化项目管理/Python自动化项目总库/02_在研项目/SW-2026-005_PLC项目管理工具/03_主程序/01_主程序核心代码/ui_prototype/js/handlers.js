async function onOpenRecentProject(path) {
  if (!path) { showToast('项目路径为空', 'warning'); return; }
  showToast('正在打开项目...', 'info');
  const r = await ipcOpenProject(path);
  if (r && r.success) {
    openTab('project', 'project-detail');
  }
}

async function onCreateProject() {
  const path = await ipcBrowseDir('选择项目存储位置');
  if (!path) return;
  const name = prompt('请输入项目名称:');
  if (!name) return;
  const info = { name: name, custom_path: path, business_line: 'SW' };
  const r = await ipcCreateProject(info);
  if (r && r.success) {
    openTab('project', 'project-detail');
  }
}

async function onBrowseOpenProject() {
  const path = await ipcBrowseDir('选择项目目录');
  if (!path) return;
  const r = await ipcOpenProject(path);
  if (r && r.success) {
    openTab('project', 'project-detail');
  }
}

async function onSaveProjectInfo() {
  if (!state.currentProject) { showToast('未打开项目', 'warning'); return; }
  const nameEl = document.getElementById('projName');
  const descEl = document.getElementById('projDesc');
  const info = {
    project_id: state.currentProject.project_id,
    name: nameEl ? nameEl.value : state.currentProject.name,
    description: descEl ? descEl.value : state.currentProject.description,
  };
  const r = await ipcSaveProjectInfo(info);
  if (r && r.success) {
    showToast('项目信息已保存', 'success');
    state.currentProject.name = info.name;
    state.currentProject.description = info.description;
  }
}

async function onRefreshProject() {
  if (!state.currentProjectPath) { showToast('未打开项目', 'warning'); return; }
  showToast('正在刷新...', 'info');
  const r = await ipcGetProjectDetail(state.currentProjectPath);
  if (r && r.success) {
    state.currentProject = r.project;
    renderContent('project-detail');
    showToast('项目信息已刷新', 'success');
  }
}

async function onCloseProject() {
  await ipcCloseProject();
  openTab('dashboard', 'dashboard');
}

async function onVersionSyncCheck() {
  if (!state.currentProjectPath) {
    showToast('请先打开项目', 'warning');
    return;
  }
  openTab('change', 'change-check');
  showToast('正在执行版本同步检查...', 'info');
  const r = await ipcRunVersionCheck();
  if (r) {
    showToast('版本检查完成', r.is_consistent ? 'success' : 'warning');
  }
}

async function onSaveDocument() {
  const el = document.getElementById('docContent');
  if (!el) return;
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  showToast('文档保存功能需要指定文件路径', 'info');
}

function onInsertVariable(varName) {
  const el = document.getElementById('docContent');
  if (!el) return;
  const start = el.selectionStart;
  const end = el.selectionEnd;
  const text = '{{' + varName + '}}';
  el.value = el.value.substring(0, start) + text + el.value.substring(end);
  el.selectionStart = el.selectionEnd = start + text.length;
  el.focus();
  showToast('变量 ' + text + ' 已插入', 'success');
}

async function onRefreshChangeList() {
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  showToast('正在刷新变更列表...', 'info');
  await ipcListChangeRequests();
  renderContent('change-list');
  showToast('变更列表已刷新 (' + state.changeRequests.length + '条)', 'success');
}

async function onCreateChangeRequest() {
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  const title = prompt('变更单标题:');
  if (!title) return;
  const category = prompt('分类 (DOCU/PLC/HMI/ELEC/SAFE/MECH/SCPT):', 'DOCU');
  const r = await ipcCreateChangeRequest({
    project_path: state.currentProjectPath,
    category: category || 'DOCU',
    title: title,
    description: ''
  });
  if (r && r.success) {
    showToast('变更单已创建: ' + (r.change_id || ''), 'success');
    await onRefreshChangeList();
  }
}

async function onApproveChange(changeId) {
  if (!state.currentProjectPath) return;
  const r = await ipcApproveChangeRequest({
    project_path: state.currentProjectPath,
    change_id: changeId,
    approver: 'current_user'
  });
  if (r && r.success) {
    showToast('变更单已审核通过', 'success');
    await onRefreshChangeList();
  } else {
    showToast('审核失败: ' + (r?.error || ''), 'error');
  }
}

function onViewChange(changeId) {
  const c = state.changeRequests.find(x => x.change_id === changeId);
  if (!c) return;
  const lines = [
    '编号: ' + (c.change_id || ''),
    '标题: ' + (c.title || ''),
    '分类: ' + (c.category || ''),
    '状态: ' + (c.status || ''),
    '描述: ' + (c.description || '无'),
    '创建: ' + (c.created_at || ''),
    '更新: ' + (c.updated_at || ''),
  ];
  alert(lines.join('\n'));
}

function onSearchChange(keyword) {
  const body = document.getElementById('changeTableBody');
  if (!body) return;
  const rows = body.querySelectorAll('tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(keyword.toLowerCase()) ? '' : 'none';
  });
}

async function onSaveSettings() {
  const settings = {};
  const pathEl = document.getElementById('settProjectPath');
  const autoSaveEl = document.getElementById('settAutoSave');
  const logLevelEl = document.getElementById('settLogLevel');
  const fontSizeEl = document.getElementById('settFontSize');
  const tabWidthEl = document.getElementById('settTabWidth');
  const themeEl = document.getElementById('settTheme');
  if (pathEl) settings.default_project_path = pathEl.value;
  if (autoSaveEl) settings.auto_save = autoSaveEl.checked;
  if (logLevelEl) settings.log_level = logLevelEl.value;
  if (fontSizeEl) settings.font_size = parseInt(fontSizeEl.value) || 15;
  if (tabWidthEl) settings.tab_width = parseInt(tabWidthEl.value) || 4;
  if (themeEl) settings.theme = themeEl.value;
  for (const [key, value] of Object.entries(settings)) {
    await _pyapi('update_setting', key, value);
  }
  state.settings = { ...state.settings, ...settings };
  showToast('设置已保存', 'success');
}

async function onResetSettings() {
  const r = await _pyapi('reset_settings');
  if (r) {
    showToast('设置已恢复默认', 'success');
    const s = await _pyapi('get_settings');
    if (s) state.settings = s;
    renderContent('settings-general');
  }
}

async function onBrowseSettingPath(elId) {
  const path = await ipcBrowseDir('选择默认项目路径');
  if (path) {
    const el = document.getElementById(elId);
    if (el) el.value = path;
  }
}

async function onLoadFixers() {
  await ipcGetAvailableFixers();
  renderContent('spec-auto-fix');
  showToast('已加载 ' + state.fixers.length + ' 个修复器', 'success');
}

async function onScanFixes() {
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  showToast('正在扫描...', 'info');
  const r = await ipcScanFixes({ project_path: state.currentProjectPath });
  if (r) {
    state.fixResults = r;
    renderContent('spec-auto-fix');
    showToast('扫描完成: ' + (r.total_issues || 0) + ' 个问题', r.total_issues > 0 ? 'warning' : 'success');
  }
}

async function onFixProject(dryRun) {
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  const msg = dryRun ? '正在预览修复...' : '正在执行修复...';
  showToast(msg, 'info');
  const r = await ipcFixProject({ project_path: state.currentProjectPath, fixer_ids: [], dry_run: dryRun });
  if (r) {
    state.fixResults = r;
    renderContent('spec-auto-fix');
    showToast(dryRun ? '预览完成' : '修复完成: ' + (r.total_fixed || 0) + ' 项', 'success');
  }
}

async function onExportExcelSingle() {
  const path = await ipcBrowseFile('选择FB源文件', 'SCL files (*.scl);;ST files (*.st);;All files (*.*)');
  if (!path) return;
  showToast('正在导出...', 'info');
  const r = await ipcExportExcelSingle({ file_path: path });
  if (r && r.success) {
    showToast('Excel已导出: ' + r.path, 'success');
  } else {
    showToast('导出失败: ' + (r?.error || ''), 'error');
  }
}

async function onExportExcelBatch() {
  if (!state.currentProjectPath) { showToast('请先打开项目', 'warning'); return; }
  showToast('正在批量导出...', 'info');
  const r = await ipcExportExcelBatch();
  if (r && r.success) {
    showToast('批量导出完成: ' + r.path, 'success');
  } else {
    showToast('导出失败: ' + (r?.error || ''), 'error');
  }
}

async function onOpenDocument() {
  const path = await ipcBrowseFile('选择文档文件', 'Markdown (*.md);;All files (*.*)');
  if (!path) return;
  showToast('正在加载文档...', 'info');
  const r = await ipcReadDocument(path);
  if (r && r.success) {
    openTab('document', 'doc-editor');
    setTimeout(() => {
      const el = document.getElementById('docContent');
      if (el) el.value = r.content || '';
    }, 100);
    showToast('文档已加载', 'success');
  } else {
    showToast('加载失败: ' + (r?.error || ''), 'error');
  }
}
