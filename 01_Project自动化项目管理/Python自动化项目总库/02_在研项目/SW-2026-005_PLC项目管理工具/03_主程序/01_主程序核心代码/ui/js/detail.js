/**
 * 项目详情页模块 — 6大信息块 + 变更列表
 */
const DetailModule = {
  _projectId: "",

  render(container, params) {
    this._projectId = params;
    container.innerHTML = '<div class="loading-spinner">加载项目详情...</div>';
    this._loadData(container);
  },

  destroy() {},

  async _loadData(container) {
    try {
      const [project, changes] = await Promise.all([
        Api.getProjectDetail(this._projectId),
        Api.getProjectChanges(this._projectId),
      ]);
      this._renderDetail(container, project, changes);
    } catch (err) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">&#9888;</div>
          <div class="empty-state__text">加载失败: ${escapeHtml(err.message || "未知错误")}</div>
        </div>`;
    }
  },

  _renderDetail(container, project, changes) {
    const phaseLabel = PHASE_LABELS[project.phase] || project.phase || "未知";

    let html = `
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <a href="#/dashboard">总览</a>
        <span class="sep">/</span>
        <span class="current">${escapeHtml(project.project_id)}</span>
      </div>

      <!-- 页面头部 -->
      <div class="page-header">
        <h1><span class="code">${escapeHtml(project.project_id)}</span>${escapeHtml(project.name)}</h1>
        <div>${statusBadge(project.phase === "developing" ? "implementing" : project.phase === "commissioning" ? "under_review" : "closed")}</div>
      </div>

      <!-- 6大信息块 -->
      <div class="info-grid">
        <!-- 业务身份 -->
        <div class="card">
          <div class="card__title">业务身份</div>
          ${this._infoRow("业务描述", project.business_desc)}
          ${this._infoRow("重要说明", project.important_note)}
          ${this._infoRow("工艺范围", project.process_scope)}
          ${this._infoRow("客户", project.customer)}
        </div>

        <!-- 技术环境 -->
        <div class="card">
          <div class="card__title">技术环境</div>
          ${this._infoRow("编程平台", project.platform)}
          ${this._infoRow("PLC型号", project.plc_model)}
          ${this._infoRow("HMI型号", project.hmi_model)}
          ${this._infoRow("驱动器", project.driver)}
          ${this._infoRow("通信方式", project.communication)}
          ${this._infoRow("运动轴", project.axes)}
          ${this._infoRow("定位精度", project.precision)}
          ${this._infoRow("安全保护", project.safety_protection)}
        </div>

        <!-- 工程规模 -->
        <div class="card">
          <div class="card__title">工程规模</div>
          ${this._infoRow("模块数量", project.module_count)}
          ${this._infoRow("模块名称", project.module_names)}
          ${this._infoRow("项目范围", project.project_scope)}
        </div>

        <!-- 工程状态 -->
        <div class="card">
          <div class="card__title">工程状态</div>
          ${this._infoRow("当前阶段", phaseLabel)}
          ${this._infoRow("开始日期", project.start_date)}
          ${this._infoRow("预计完成", project.end_date)}
          ${this._infoRow("总工期", project.duration_days)}
        </div>

        <!-- 风险评估 -->
        <div class="card">
          <div class="card__title">风险评估</div>
          ${this._renderRisks(project.risks)}
        </div>

        <!-- 团队信息 -->
        <div class="card">
          <div class="card__title">团队信息</div>
          ${this._infoRow("团队", project.team)}
        </div>
      </div>

      <!-- 变更单列表 -->
      <div class="card mt-24">
        <div class="card__header">
          <div class="card__title">变更单</div>
          <span class="text-muted" style="font-size:12px;">共 ${escapeHtml(changes.length)} 条</span>
        </div>
        ${this._renderChangeTable(changes)}
      </div>`;

    container.innerHTML = html;

    // 绑定变更行点击
    container.querySelectorAll(".change-row").forEach((row) => {
      row.addEventListener("click", () => {
        const num = row.dataset.changeNumber;
        if (num) location.hash = `#/change/${num}`;
      });
    });
  },

  _infoRow(label, value) {
    return `<div class="info-row"><span class="info-row__label">${escapeHtml(label)}</span><span class="info-row__value">${escapeHtml(value || "待补充")}</span></div>`;
  },

  _renderRisks(risks) {
    if (!risks || risks.length === 0) {
      return '<div class="text-muted" style="font-size:13px;">暂无风险评估</div>';
    }
    return `<table class="data-table">
      <thead><tr><th>风险项</th><th>等级</th><th>应对措施</th></tr></thead>
      <tbody>${risks.map((r) => `<tr><td>${escapeHtml(r.risk_item || "待补充")}</td><td>${escapeHtml(r.level || "待补充")}</td><td>${escapeHtml(r.measure || "待补充")}</td></tr>`).join("")}</tbody>
    </table>`;
  },

  _renderChangeTable(changes) {
    if (!changes || changes.length === 0) {
      return '<div class="empty-state"><div class="empty-state__text">暂无变更单</div></div>';
    }
    return `<table class="data-table">
      <thead><tr><th>变更编号</th><th>领域</th><th>性质</th><th>状态</th><th>申请人</th><th>申请日期</th></tr></thead>
      <tbody>${changes.map((c) => `<tr class="clickable change-row" data-change-number="${escapeHtml(c.change_number)}">
        <td class="text-accent">${escapeHtml(c.change_number)}</td>
        <td>${escapeHtml(DOMAIN_LABELS[c.domain] || c.domain)}</td>
        <td>${escapeHtml(NATURE_LABELS[c.business_nature] || c.business_nature)}</td>
        <td>${statusBadge(c.status)}</td>
        <td>${escapeHtml(c.applicant || "待补充")}</td>
        <td>${escapeHtml(formatDate(c.apply_date))}</td>
      </tr>`).join("")}</tbody>
    </table>`;
  },
};
