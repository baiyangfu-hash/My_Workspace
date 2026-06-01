function renderProjectDetail() {
  const p = state.currentProject;
  if (!p) {
    return `
      <div class="placeholder-view">
        <div class="ph-icon">📁</div>
        <div class="ph-title">未打开项目</div>
        <div class="ph-desc">请从仪表盘选择最近项目，或点击"打开项目"浏览</div>
        <div style="margin-top:16px;display:flex;gap:8px;justify-content:center;">
          <button class="btn btn-primary" onclick="onBrowseOpenProject()">📂 打开项目</button>
        </div>
      </div>
    `;
  }

  return `
    <div class="project-layout">
      <div class="project-tree-panel">
        <div class="tree-header">📁 项目浏览</div>
        <div class="tree-body">
          <div class="tree-item selected">
            <span class="tree-icon">📁</span> ${_escHtml(p.project_id || p.name || '')}
          </div>
          <div class="tree-item" style="padding-left:28px;">
            <span class="tree-icon">📂</span> 01_源代码
          </div>
          <div class="tree-item" style="padding-left:28px;">
            <span class="tree-icon">📂</span> 02_文档
          </div>
          <div class="tree-item" style="padding-left:28px;">
            <span class="tree-icon">📂</span> 03_配置
          </div>
        </div>
      </div>
      <div class="project-detail-panel">
        <div class="detail-header">
          <span class="dh-icon">📁</span>
          <div>
            <div class="detail-title">${_escHtml(p.project_id || '')} ${_escHtml(p.name || '')}</div>
            <div class="detail-meta">${_escHtml(p.business_line || '')}项目 · 最后修改: ${_escHtml(p.updated_at || '-')} · 路径: ${_escHtml(p.path || '')}</div>
          </div>
        </div>
        <div class="detail-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">项目编号</label>
              <input class="form-input" value="${_escHtml(p.project_id || '')}" readonly>
            </div>
            <div class="form-group">
              <label class="form-label">项目类型</label>
              <input class="form-input" value="${_escHtml(p.project_type || p.business_line || '')}" readonly>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">项目名称</label>
              <input class="form-input" id="projName" value="${_escHtml(p.name || '')}">
            </div>
            <div class="form-group">
              <label class="form-label">状态</label>
              <input class="form-input" value="${_escHtml(p.status || '')}" readonly>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">项目路径</label>
            <input class="form-input" value="${_escHtml(p.path || '')}" readonly>
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <textarea class="form-input" id="projDesc" rows="3" style="resize:vertical;">${_escHtml(p.description || '')}</textarea>
          </div>
          <div style="display:flex;gap:8px;margin-top:8px;">
            <button class="btn btn-primary" onclick="onSaveProjectInfo()">💾 保存</button>
            <button class="btn btn-secondary" onclick="onRefreshProject()">🔄 刷新</button>
            <button class="btn btn-danger btn-sm" onclick="onCloseProject()">关闭项目</button>
          </div>
        </div>
      </div>
    </div>
  `;
}
