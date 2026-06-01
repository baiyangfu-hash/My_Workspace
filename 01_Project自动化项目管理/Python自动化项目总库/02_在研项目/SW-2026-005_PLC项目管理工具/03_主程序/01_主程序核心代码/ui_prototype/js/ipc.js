function _pyapi(name, ...args) {
  if (!window.pywebview || !window.pywebview.api) {
    console.warn('[IPC] pywebview.api not available, call:', name, args);
    return Promise.resolve(null);
  }
  try {
    const fn = window.pywebview.api[name];
    if (typeof fn === 'function') return fn(...args);
    console.warn('[IPC] method not found:', name);
  } catch(e) { console.error('[IPC]', name, e); }
  return Promise.resolve(null);
}

window.__ipc_recv = function(payload) {
  if (!payload || !payload.event) return;
  const evt = payload.event;
  const data = payload.data;
  switch(evt) {
    case 'project_created':
      showToast('项目创建成功: ' + (data.path || ''), 'success');
      ipcLoadDashboard();
      break;
    case 'project_opened':
      updateStatusBarProject(data.project_id || '');
      ipcLoadDashboard();
      break;
    case 'project_closed':
      state.currentProject = null;
      state.currentProjectPath = '';
      updateStatusBarProject('');
      ipcLoadDashboard();
      break;
    case 'setting_changed':
      showToast('设置已更新: ' + (data.key || ''), 'info');
      break;
    case 'settings_reset':
      showToast('设置已恢复默认', 'info');
      renderContent('settings-general');
      break;
    case 'document_created':
      showToast('文档已创建: ' + (data.path || ''), 'success');
      break;
  }
};

async function ipcCreateProject(info) {
  const r = await _pyapi('create_project', JSON.stringify(info));
  if (!r || !r.success) { showToast(r?.error || '创建失败', 'error'); return null; }
  showToast('项目创建成功', 'success');
  await ipcLoadDashboard();
  return r;
}
async function ipcOpenProject(path) {
  const r = await _pyapi('open_project', path);
  if (r && r.success) {
    state.currentProject = r.project;
    state.currentProjectPath = r.project.path || path;
    updateStatusBarProject(r.project.project_id || '');
    showToast('项目已打开: ' + (r.project.name || ''), 'success');
  } else {
    showToast(r?.error || '打开项目失败', 'error');
  }
  return r;
}
async function ipcCloseProject() {
  const r = await _pyapi('close_project');
  state.currentProject = null;
  state.currentProjectPath = '';
  updateStatusBarProject('');
  showToast('项目已关闭', 'info');
  return r;
}
async function ipcGetProjectDetail(path) { return await _pyapi('get_project_detail', path); }
async function ipcSaveProjectInfo(info) { return await _pyapi('save_project_info', JSON.stringify(info)); }
async function ipcRunVersionCheck(path) { return await _pyapi('run_version_check', path || state.currentProjectPath); }
async function ipcGenerateCHG(path, dir) { return await _pyapi('generate_chg', path || state.currentProjectPath, dir || ''); }
async function ipcGenerateIFC(path, dir) { return await _pyapi('generate_ifc', path || state.currentProjectPath, dir || ''); }
async function ipcRunSpecCheck(path, ids) { return await _pyapi('run_spec_check', path || state.currentProjectPath, ids || '[]'); }
async function ipcGetCheckers() {
  const r = await _pyapi('get_checkers');
  state.checkers = r || [];
  return r || [];
}
async function ipcBrowseDir(title) { return await _pyapi('browse_directory', title || '') || ''; }
async function ipcBrowseFile(title, filter) { return await _pyapi('browse_file', title || '', filter || '') || ''; }
async function ipcSaveFileDialog(title, filter) { return await _pyapi('save_file_dialog', title || '', filter || '') || ''; }
async function ipcListChangeRequests(path) {
  const r = await _pyapi('list_change_requests', path || state.currentProjectPath);
  state.changeRequests = r || [];
  return r || [];
}
async function ipcCreateChangeRequest(params) { return await _pyapi('create_change_request', JSON.stringify(params)); }
async function ipcUpdateChangeStatus(params) { return await _pyapi('update_change_status', JSON.stringify(params)); }
async function ipcApproveChangeRequest(params) { return await _pyapi('approve_change_request', JSON.stringify(params)); }
async function ipcReadDocument(filePath) { return await _pyapi('read_document', filePath); }
async function ipcSaveDocument(params) { return await _pyapi('save_document', JSON.stringify(params)); }
async function ipcGetAvailableFixers() {
  const r = await _pyapi('get_available_fixers');
  state.fixers = r || [];
  return r || [];
}
async function ipcScanFixes(params) { return await _pyapi('scan_fixes', JSON.stringify(params)); }
async function ipcFixProject(params) { return await _pyapi('fix_project', JSON.stringify(params)); }
async function ipcExportExcelSingle(params) { return await _pyapi('export_excel_single', JSON.stringify(params)); }
async function ipcExportExcelBatch(path) { return await _pyapi('export_excel_batch', path || state.currentProjectPath); }
async function ipcGetDashboardStats() {
  const r = await _pyapi('get_dashboard_stats');
  if (r) state.dashboardStats = r;
  return r;
}
async function ipcRunDiagnosis(path) { return await _pyapi('run_diagnosis', path || state.currentProjectPath); }
async function ipcWindowMinimize() { return await _pyapi('window_minimize'); }
async function ipcWindowMaximize() { return await _pyapi('window_maximize'); }
async function ipcWindowClose() { return await _pyapi('window_close'); }

async function ipcPing() { return await _pyapi('ipc_ping'); }
async function ipcGetMockData(type) { return await _pyapi('get_mock_data', type); }

async function ipcLoadDashboard() {
  await ipcGetDashboardStats();
  renderContent('dashboard');
}

async function _ipcAutoPing() {
  const r = await ipcPing();
  if (r && r.status === 'ok') {
    showToast('IPC连接成功 (mock=' + r.mock_mode + ')', 'success');
    console.log('[IPC] ping成功:', r);
  } else {
    showToast('IPC未连接 - 运行在纯前端模式', 'warning');
  }
}

function runIpcTest(testName) {
  const outputEl = document.getElementById('ipcTestOutput');
  if (!outputEl) return;
  outputEl.textContent = '正在执行: ' + testName + ' ...';
  const tests = {
    ping: async () => { const r = await ipcPing(); return JSON.stringify(r, null, 2); },
    app_info: async () => { const r = await _pyapi('get_app_info'); return JSON.stringify(r, null, 2); },
    recent_projects: async () => { const r = await _pyapi('get_recent_projects'); return JSON.stringify(r, null, 2); },
    checkers: async () => { const r = await _pyapi('get_checkers'); return JSON.stringify(r, null, 2); },
    spec_check: async () => { const r = await ipcRunSpecCheck('', '["naming","syntax"]'); return JSON.stringify(r, null, 2); },
    diagnosis: async () => { const r = await _pyapi('run_diagnosis', ''); return JSON.stringify(r, null, 2); },
    version_check: async () => { const r = await ipcRunVersionCheck(''); return JSON.stringify(r, null, 2); },
    settings: async () => { const r = await _pyapi('get_settings'); return JSON.stringify(r, null, 2); },
  };
  if (tests[testName]) {
    tests[testName]().then(result => {
      outputEl.textContent = '[' + testName + '] 结果:\n' + result;
      showToast(testName + ' 测试完成', 'success');
    }).catch(err => {
      outputEl.textContent = '[' + testName + '] 错误: ' + err;
      showToast(testName + ' 测试失败', 'error');
    });
  }
}
