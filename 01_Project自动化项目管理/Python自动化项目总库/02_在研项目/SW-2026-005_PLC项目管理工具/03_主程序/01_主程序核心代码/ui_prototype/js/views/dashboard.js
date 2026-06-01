function renderDashboard() {
  const ds = state.dashboardStats;
  const recent = ds.recent_projects || [];
  let recentHtml = '';
  if (recent.length === 0) {
    recentHtml = '<li class="recent-item" style="color:var(--text-muted);justify-content:center;">暂无最近项目</li>';
  } else {
    recentHtml = recent.map(p => `
      <li class="recent-item" onclick="onOpenRecentProject('${_escHtml(p.path || '')}')">
        <span class="recent-icon">📁</span>
        <div>
          <div>${_escHtml(p.name || p.project_id || '')}</div>
          <div class="recent-path">${_escHtml(p.path || '')}</div>
        </div>
      </li>
    `).join('');
  }

  return `
    <div class="dashboard">
      <div class="welcome-section">
        <div class="welcome-title">PLC项目管理工具</div>
        <div class="welcome-subtitle">Trae伴生式工作空间治理 — 规范检查 · 文档生成 · 变更管理</div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-card-header">
            <div class="stat-card-icon orange">📁</div>
            <div>
              <div class="stat-card-label">工作空间项目</div>
              <div class="stat-card-value">${ds.project_count || 0}</div>
            </div>
          </div>
          <div class="stat-card-detail">最近打开的项目数</div>
        </div>
        <div class="stat-card">
          <div class="stat-card-header">
            <div class="stat-card-icon blue">📝</div>
            <div>
              <div class="stat-card-label">文档模板</div>
              <div class="stat-card-value">${ds.template_count || 0}</div>
            </div>
          </div>
          <div class="stat-card-detail">可用文档模板</div>
        </div>
        <div class="stat-card">
          <div class="stat-card-header">
            <div class="stat-card-icon green">✅</div>
            <div>
              <div class="stat-card-label">规范检查通过率</div>
              <div class="stat-card-value">--</div>
            </div>
          </div>
          <div class="stat-card-detail">运行检查后显示</div>
        </div>
        <div class="stat-card">
          <div class="stat-card-header">
            <div class="stat-card-icon yellow">🔄</div>
            <div>
              <div class="stat-card-label">待处理变更</div>
              <div class="stat-card-value">${state.changeRequests.filter(c => c.status !== 'completed' && c.status !== 'cancelled').length}</div>
            </div>
          </div>
          <div class="stat-card-detail">未完成的变更单</div>
        </div>
      </div>

      <div class="section-grid">
        <div class="section-panel">
          <div class="section-panel-header">
            ⚡ 快速操作
          </div>
          <div class="section-panel-body">
            <div class="quick-actions">
              <button class="quick-action-btn" onclick="openTab('document','doc-new')">
                <span class="qa-icon">📝</span> 新建文档
              </button>
              <button class="quick-action-btn" onclick="openTab('spec','spec-run')">
                <span class="qa-icon">🔍</span> 运行检查
              </button>
              <button class="quick-action-btn" onclick="onCreateProject()">
                <span class="qa-icon">📁</span> 新建项目
              </button>
              <button class="quick-action-btn" onclick="onVersionSyncCheck()">
                <span class="qa-icon">🔄</span> 版本同步
              </button>
              <button class="quick-action-btn" onclick="openTab('plc-tools','plc-st-editor')">
                <span class="qa-icon">📝</span> ST编辑器
              </button>
              <button class="quick-action-btn" onclick="openTab('spec','spec-auto-fix')">
                <span class="qa-icon">🔧</span> 自动修复
              </button>
            </div>
          </div>
        </div>
        <div class="section-panel">
          <div class="section-panel-header">
            🕐 最近项目
          </div>
          <div class="section-panel-body">
            <ul class="recent-list">${recentHtml}</ul>
          </div>
        </div>
      </div>
    </div>
  `;
}
