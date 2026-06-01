function renderAutoFix() {
  const fixers = state.fixers || [];
  let fixerHtml = '';
  if (fixers.length === 0) {
    fixerHtml = '<div style="color:var(--text-muted);padding:16px;text-align:center;">点击"加载修复器"获取可用修复器列表</div>';
  } else {
    fixerHtml = fixers.map(f => `
      <div class="checker-card selected" style="margin-bottom:8px;">
        <span class="check-icon">🔧</span>
        <div class="check-info">
          <div class="check-name">${_escHtml(f.name || f.id || '')}</div>
          <div class="check-count">${_escHtml(f.description || '')}</div>
        </div>
      </div>
    `).join('');
  }

  const fr = state.fixResults;
  let resultHtml = '';
  if (fr) {
    resultHtml = `
      <div class="result-panel" style="margin-top:12px;">
        <div class="result-header">📋 修复结果</div>
        <div style="padding:12px;">
          <p>扫描文件: ${fr.files_scanned || 0} | 发现问题: ${fr.total_issues || 0} | 可修复: ${fr.fixable_issues || 0}</p>
          ${fr.total_fixed !== undefined ? '<p>已修复: ' + fr.total_fixed + ' | 已回滚: ' + (fr.total_rolled_back || 0) + '</p>' : ''}
        </div>
      </div>
    `;
  }

  return `
    <div style="display:flex;flex-direction:column;gap:12px;">
      <div style="display:flex;gap:8px;align-items:center;">
        <button class="btn btn-secondary" onclick="onLoadFixers()">📋 加载修复器</button>
        <button class="btn btn-primary" onclick="onScanFixes()">🔍 扫描问题</button>
        <button class="btn btn-secondary" onclick="onFixProject(true)">👁 预览修复</button>
        <button class="btn btn-primary" onclick="onFixProject(false)">🔧 执行修复</button>
      </div>
      ${fixerHtml}
      ${resultHtml}
    </div>
  `;
}
