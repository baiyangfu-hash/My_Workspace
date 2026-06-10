/**
 * 总览页模块 — 项目卡片 + 统计栏
 *
 * 数据加载方式: Python 端通过 evaluate_js 推送数据到 window.__dashboardData，
 * 前端监听数据到达后渲染。不再使用 await Api.getWorkspaceProjects()。
 */
const DashboardModule = {
  _rendered: false,
  _container: null,
  _allProjects: [],  // 缓存全量项目数据，用于筛选

  render(container, params) {
    this._container = container;
    this._rendered = false;

    // 显示加载状态
    container.innerHTML = '<div class="loading-spinner">加载中...</div>';

    // 检查是否已有推送数据（Python端可能在路由注册前就推送了）
    if (window.__dashboardData) {
      this._onDataReceived(window.__dashboardData);
      return;
    }

    // 注册数据接收回调（Python端通过 evaluate_js 调用）
    window.__onDashboardData = (data) => {
      this._onDataReceived(data);
    };

    // 安全超时：如果5秒后仍无数据，显示提示（不阻塞，允许后续重试）
    setTimeout(() => {
      if (!this._rendered && this._container) {
        this._container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state__icon">&#9203;</div>
            <div class="empty-state__text">等待数据加载中...</div>
            <div style="margin-top:8px;color:var(--text-muted);font-size:13px;">
              如果持续显示此消息，请点击 <strong>总览</strong> 刷新
            </div>
          </div>`;
      }
    }, 5000);
  },

  destroy() {
    window.__onDashboardData = null;
    this._rendered = false;
    this._container = null;
  },

  _onDataReceived(data) {
    if (!this._container || this._rendered) return;
    this._rendered = true;

    const projects = Array.isArray(data) ? data : [];
    this._allProjects = projects.filter((p) => p != null);
    this._renderDashboard(this._container, this._allProjects);
  },

  /** 根据筛选条件重新渲染卡片区域 */
  _applyFilter(phase) {
    const filtered = phase
      ? this._allProjects.filter((p) => p.phase === phase)
      : this._allProjects;
    // 只更新卡片网格区域，不重建整个页面
    const gridEl = this._container.querySelector(".info-grid");
    if (gridEl) {
      gridEl.innerHTML = this._renderCards(filtered);
      this._bindCardClicks(gridEl);
    }
  },

  _renderCards(projects) {
    if (projects.length === 0) {
      return `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-state__icon">&#128193;</div>
          <div class="empty-state__text">暂无匹配的项目</div>
        </div>`;
    }
    return projects.map((p) => {
      const phaseLabel = PHASE_LABELS[p.phase] || p.phase || "未知";
      return `
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
    }).join("");
  },

  _bindCardClicks(root) {
    root.querySelectorAll(".card--clickable").forEach((card) => {
      card.addEventListener("click", () => {
        const pid = card.dataset.projectId;
        if (pid) location.hash = `#/detail/${pid}`;
      });
    });
  },

  _renderDashboard(container, projects) {
    // 防御：过滤可能的 null/undefined 元素（PyWebView 序列化边界情况）
    const safeProjects = projects.filter((p) => p != null);

    const total = safeProjects.length;
    const developing = safeProjects.filter((p) => p.phase === "developing").length;
    const commissioning = safeProjects.filter((p) => p.phase === "commissioning").length;
    const pendingChanges = safeProjects.reduce((sum, p) => sum + (p.pending_change_count || 0), 0);
    const totalChanges = safeProjects.reduce((sum, p) => sum + (p.change_count || 0), 0);

    // 构建阶段筛选下拉选项
    const phaseOptions = Object.entries(PHASE_LABELS)
      .map(([key, label]) => `<option value="${escapeHtml(key)}">${escapeHtml(label)}</option>`)
      .join("");

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

      <!-- 筛选栏 -->
      <div class="filter-bar" style="margin-bottom:16px;display:flex;align-items:center;gap:12px;">
        <label style="font-size:13px;color:var(--text-muted);">按阶段筛选:</label>
        <select class="form-select" id="filter-phase" style="min-width:140px;">
          <option value="">全部阶段</option>
          ${phaseOptions}
        </select>
      </div>

      <!-- 项目卡片网格 -->
      <div class="info-grid">${this._renderCards(safeProjects)}</div>`;

    container.innerHTML = html;

    // 绑定筛选事件
    const filterSelect = container.querySelector("#filter-phase");
    if (filterSelect) {
      filterSelect.addEventListener("change", (e) => {
        this._applyFilter(e.target.value || null);
      });
    }

    // 绑定卡片点击事件
    this._bindCardClicks(container);
  },
};
