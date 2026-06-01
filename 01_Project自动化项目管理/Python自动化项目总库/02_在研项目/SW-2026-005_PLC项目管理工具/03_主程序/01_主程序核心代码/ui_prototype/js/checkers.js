function toggleChecker(id) {
  state.checkerSelections[id] = !state.checkerSelections[id];
  const container = document.getElementById('contentMain');
  container.innerHTML = renderSpecCheck();
}

function selectAllCheckers() {
  Object.keys(state.checkerSelections).forEach(k => state.checkerSelections[k] = true);
  const container = document.getElementById('contentMain');
  container.innerHTML = renderSpecCheck();
}

function deselectAllCheckers() {
  Object.keys(state.checkerSelections).forEach(k => state.checkerSelections[k] = false);
  const container = document.getElementById('contentMain');
  container.innerHTML = renderSpecCheck();
}

function runCheck() {
  const selected = [];
  const ids = [];
  const names = {
    syntax: '语法检查', comment: '注释检查', naming: '命名规范',
    variable: '变量检查', config: '配置检查', timer: '定时器检查',
    fb_iface: 'FB接口调用检查'
  };
  Object.keys(state.checkerSelections).forEach(k => {
    if (state.checkerSelections[k]) {
      selected.push(names[k] || k);
      ids.push(k);
    }
  });
  if (selected.length === 0) {
    showToast('请至少选择一个检查器', 'warning');
    return;
  }
  if (!state.currentProjectPath) {
    showToast('请先打开项目再运行检查', 'warning');
    return;
  }
  showToast('🔍 开始检查: ' + selected.join('、'), 'info');
  ipcRunSpecCheck('', JSON.stringify(ids)).then(result => {
    if (result) {
      state.specResults = result;
      renderContent('spec-run');
      const total = result.total_issues || 0;
      showToast('检查完成: 发现 ' + total + ' 个问题', total > 0 ? 'warning' : 'success');
    }
  });
}
