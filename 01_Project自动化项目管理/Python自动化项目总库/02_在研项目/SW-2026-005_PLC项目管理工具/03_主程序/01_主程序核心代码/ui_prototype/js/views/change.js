function renderChangeList() {
  const changes = state.changeRequests || [];
  let rowsHtml = '';
  if (changes.length === 0) {
    rowsHtml = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:24px;">暂无变更单</td></tr>';
  } else {
    rowsHtml = changes.map(c => {
      const isDraft = c.status === 'draft';
      const actionBtn = isDraft
        ? `<button class="btn btn-sm btn-primary" onclick="onApproveChange('${_escHtml(c.change_id || '')}')">审核</button>`
        : `<button class="btn btn-sm btn-secondary" onclick="onViewChange('${_escHtml(c.change_id || '')}')">查看</button>`;
      return `
        <tr>
          <td style="color:var(--info);">${_escHtml(c.change_id || '')}</td>
          <td>${_escHtml(c.title || '')}</td>
          <td>${_escHtml(c.category || '')}</td>
          <td>${_statusBadgeHtml(c.status || 'draft')}</td>
          <td>${_escHtml(c.created_at || '')}</td>
          <td>${actionBtn}</td>
        </tr>
      `;
    }).join('');
  }

  return `
    <div style="display:flex;flex-direction:column;gap:14px;">
      <div class="change-toolbar">
        <button class="btn btn-primary" onclick="onCreateChangeRequest()">➕ 新建变更单</button>
        <button class="btn btn-secondary" onclick="onRefreshChangeList()">🔄 刷新列表</button>
        <button class="btn btn-secondary" onclick="onVersionSyncCheck()">🔍 版本同步检查</button>
        <span class="change-toolbar-spacer"></span>
        <input class="form-input" placeholder="搜索变更单..." style="width:200px;" oninput="onSearchChange(this.value)">
      </div>
      <table class="change-table">
        <thead>
          <tr>
            <th>编号</th>
            <th>标题</th>
            <th>分类</th>
            <th>状态</th>
            <th>创建日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody id="changeTableBody">${rowsHtml}</tbody>
      </table>
    </div>
  `;
}
