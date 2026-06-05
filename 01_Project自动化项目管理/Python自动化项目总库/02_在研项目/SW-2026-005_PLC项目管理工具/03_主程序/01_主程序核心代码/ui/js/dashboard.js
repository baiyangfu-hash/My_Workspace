/**
 * 总览页模块 — 项目卡片 + 统计栏
 */
const DashboardModule = {
  render(container, params) {
    container.innerHTML = '<div class="loading-spinner">加载项目数据...</div>';
    this._loadData(container);
  },

  destroy() {
    // 清理事件监听（如有）
  },

  async _loadData(container) {
    try {
      const projects = await Api.getWorkspaceProjects();
      if (!Array.isArray(projects)) {
        throw new Error("返回数据格式异常: 期望数组");
      }
      this._renderDashboard(container, projects);
    } catch (err) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">&#9888;</div>
          <div class="empty-state__text">加载失败: ${escapeHtml(err.message || "未知错误")}</div>
        </div>`;
    }
  },

  _renderDashboard(container, projects) {
    // 防御：过滤可能的 null/undefined 元素（PyWebView 序列化边界情况）
    const safeProjects = Array.isArray(projects) ? projects.filter((p) => p != null) : [];

    const total = safeProjects.length;
    const developing = safeProjects.filter((p) => p.phase === "developing").length;
    const commissioning = safeProjects.filter((p) => p.phase === "commissioning").length;
    const pendingChanges = safeProjects.reduce((sum, p) => sum + (p.pending_change_count || 0), 0);
    const totalChanges = safeProjects.reduce((sum, p) => sum + (p.change_count || 0), 0);

    let html = `
      <!-- 统计栏 -->
      <div class="stat-bar">
        <div class="stat-item">
          <div class="stat-item__value">${escapeHtml(total)}</div>
          <div class="stat-item__label">项目总数</div>
        </div>
        <div class="stat-item stat-item--accent">
          <div class="stat-item__value">${escapeHtml(developing)}</div>
          <div class="stat-item__label">开发中</div>
        </div>
        <div class="stat-item stat-item--warning">
          <div class="stat-item__value">${escapeHtml(commissioning)}</div>
          <div class="stat-item__label">调试中</div>
        </div>
        <div class="stat-item">
          <div class="stat-item__value">${escapeHtml(totalChanges)}</div>
          <div class="stat-item__label">变更总数</div>
        </div>
        <div class="stat-item stat-item--error">
          <div class="stat-item__value">${escapeHtml(pendingChanges)}</div>
          <div class="stat-item__label">待处理变更</div>
        </div>
      </div>

      <!-- 项目卡片网格 -->
      <div class="info-grid">`;

    if (safeProjects.length === 0) {
      html += `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-state__icon">&#128193;</div>
          <div class="empty-state__text">暂无项目数据</div>
        </div>`;
    } else {
      safeProjects.forEach((p) => {
        const phaseLabel = PHASE_LABELS[p.phase] || p.phase || "未知";
        html += `
        <div class="card card--clickable" data-project-id="${escapeHtml(p.project_id)}">
          <div class="card__header">
            <div class="card__title">${escapeHtml(p.project_id)}</div>
            ${statusBadge(p.phase === "developing" ? "implementing" : p.phase === "commissioning" ? "under_review" : "closed")}
          </div>
          <div style="font-size:16px;font-weight:600;color:#fff;margin-bottom:8px;">${escapeHtml(p.name)}</div>
          <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">${escapeHtml(p.platform || "待补充")} / ${escapeHtml(p.plc_model || "待补充")}</div>
          <div style="display:flex;justify-content:space-between;font-size:12px;">
            <span class="text-muted">${escapeHtml(phaseLabel)}</span>
            <span>变更: <strong class="text-accent">${escapeHtml(p.change_count || 0)}</strong> / 待处理 <strong class="text-error">${escapeHtml(p.pending_change_count || 0)}</strong></span>
          </div>
        </div>`;
      });
    }

    html += "</div>";
    container.innerHTML = html;

    // 绑定卡片点击事件
    container.querySelectorAll(".card--clickable").forEach((card) => {
      card.addEventListener("click", () => {
        const pid = card.dataset.projectId;
        if (pid) location.hash = `#/detail/${pid}`;
      });
    });
  },
};
