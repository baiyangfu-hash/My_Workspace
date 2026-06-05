/**
 * 变更管理页模块 — 列表 + 创建向导 + 详情 + 状态流转 + 门禁提示
 */
const ChangeModule = {
  _view: "list",       // list | create | detail
  _changeNumber: "",   // 详情视图的变更编号
  _projects: [],       // 项目列表缓存
  _wizardStep: 0,      // 创建向导当前步骤
  _wizardData: {},      // 创建向导表单数据

  render(container, params) {
    if (params) {
      // 从路由参数进入详情视图
      this._view = "detail";
      this._changeNumber = params;
    } else {
      this._view = "list";
      this._changeNumber = "";
    }
    this._renderView(container);
  },

  destroy() {
    this._wizardStep = 0;
    this._wizardData = {};
  },

  _renderView(container) {
    switch (this._view) {
      case "list":
        this._renderList(container);
        break;
      case "create":
        this._renderCreate(container);
        break;
      case "detail":
        this._renderDetail(container);
        break;
    }
  },

  /* ========== 列表视图 ========== */
  async _renderList(container) {
    container.innerHTML = '<div class="loading-spinner">加载变更列表...</div>';
    try {
      // 先获取项目列表（用于筛选下拉）
      this._projects = await Api.getWorkspaceProjects();
      // 默认加载第一个项目的变更单
      const defaultPid = this._projects.length > 0 ? this._projects[0].project_id : "";
      const changes = defaultPid ? await Api.listChangeRequests(defaultPid, {}) : [];
      this._renderListContent(container, this._projects, defaultPid, changes);
    } catch (err) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">&#9888;</div>
          <div class="empty-state__text">加载失败: ${err.message || "未知错误"}</div>
        </div>`;
    }
  },

  _renderListContent(container, projects, selectedPid, changes) {
    let html = `
      <div class="page-header">
        <h1>变更管理中心</h1>
        <button class="btn-primary" id="btn-create-change">+ 新建变更单</button>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <select class="form-select" id="filter-project">
          <option value="">全部项目</option>
          ${projects.map((p) => `<option value="${p.project_id}" ${p.project_id === selectedPid ? "selected" : ""}>${p.project_id} - ${p.name}</option>`).join("")}
        </select>
        <select class="form-select" id="filter-status">
          <option value="">全部状态</option>
          ${Object.entries(STATUS_LABELS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}
        </select>
        <select class="form-select" id="filter-domain">
          <option value="">全部领域</option>
          ${Object.entries(DOMAIN_LABELS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}
        </select>
      </div>

      <!-- 变更单列表 -->
      <div class="card">
        ${this._renderChangeList(changes)}
      </div>`;

    container.innerHTML = html;

    // 绑定事件
    container.querySelector("#btn-create-change").addEventListener("click", () => {
      this._view = "create";
      this._wizardStep = 0;
      this._wizardData = {};
      this._renderView(container);
    });

    container.querySelector("#filter-project").addEventListener("change", (e) => {
      this._onFilterChange(container, e.target.value);
    });
    container.querySelector("#filter-status").addEventListener("change", (e) => {
      this._onFilterChange(container, container.querySelector("#filter-project").value);
    });
    container.querySelector("#filter-domain").addEventListener("change", (e) => {
      this._onFilterChange(container, container.querySelector("#filter-project").value);
    });

    // 绑定行点击
    container.querySelectorAll(".change-row").forEach((row) => {
      row.addEventListener("click", () => {
        this._changeNumber = row.dataset.changeNumber;
        this._view = "detail";
        this._renderView(container);
      });
    });
  },

  async _onFilterChange(container, projectId) {
    if (!projectId) {
      container.querySelector(".card").innerHTML = '<div class="empty-state"><div class="empty-state__text">请选择项目</div></div>';
      return;
    }
    const status = container.querySelector("#filter-status").value;
    const domain = container.querySelector("#filter-domain").value;
    const filters = {};
    if (status) filters.status = status;
    if (domain) filters.domain = domain;

    try {
      const changes = await Api.listChangeRequests(projectId, filters);
      container.querySelector(".card").innerHTML = this._renderChangeList(changes);
      container.querySelectorAll(".change-row").forEach((row) => {
        row.addEventListener("click", () => {
          this._changeNumber = row.dataset.changeNumber;
          this._view = "detail";
          this._renderView(container);
        });
      });
    } catch (err) {
      showToast("筛选失败: " + (err.message || ""), "error");
    }
  },

  _renderChangeList(changes) {
    if (!changes || changes.length === 0) {
      return '<div class="empty-state"><div class="empty-state__text">暂无变更单</div></div>';
    }
    return `<table class="data-table">
      <thead><tr><th>变更编号</th><th>项目</th><th>领域</th><th>性质</th><th>状态</th><th>申请人</th><th>申请日期</th><th>摘要</th></tr></thead>
      <tbody>${changes.map((c) => `<tr class="clickable change-row" data-change-number="${c.change_number}">
        <td class="text-accent">${c.change_number}</td>
        <td>${c.project_id}</td>
        <td>${DOMAIN_LABELS[c.domain] || c.domain}</td>
        <td>${NATURE_LABELS[c.business_nature] || c.business_nature}</td>
        <td>${statusBadge(c.status)}</td>
        <td>${c.applicant || "待补充"}</td>
        <td>${formatDate(c.apply_date)}</td>
        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${c.title || ""}</td>
      </tr>`).join("")}</tbody>
    </table>`;
  },

  /* ========== 创建向导 ========== */
  async _renderCreate(container) {
    if (this._projects.length === 0) {
      this._projects = await Api.getWorkspaceProjects();
    }

    const steps = ["选择项目", "基本信息", "申请信息", "补充信息", "确认提交"];
    let html = `
      <div class="page-header">
        <h1>新建变更单</h1>
        <button class="btn-secondary" id="btn-cancel-create">取消</button>
      </div>

      <!-- 步骤指示器 -->
      <div class="wizard-steps">
        ${steps.map((s, i) => `<div class="wizard-step ${i === this._wizardStep ? "active" : i < this._wizardStep ? "done" : ""}">${i + 1}. ${s}</div>`).join("")}
      </div>

      <!-- 步骤内容 -->
      <div class="card" id="wizard-content">
        ${this._renderWizardStep()}
      </div>

      <!-- 导航按钮 -->
      <div style="display:flex;justify-content:space-between;margin-top:20px;">
        <button class="btn-secondary" id="btn-wizard-prev" ${this._wizardStep === 0 ? "disabled" : ""}>上一步</button>
        <button class="btn-primary" id="btn-wizard-next">${this._wizardStep === 4 ? "提交" : "下一步"}</button>
      </div>`;

    container.innerHTML = html;

    // 绑定事件
    container.querySelector("#btn-cancel-create").addEventListener("click", () => {
      this._view = "list";
      this._renderView(container);
    });
    container.querySelector("#btn-wizard-prev").addEventListener("click", () => {
      if (this._wizardStep > 0) {
        this._wizardStep--;
        this._renderCreate(container);
      }
    });
    container.querySelector("#btn-wizard-next").addEventListener("click", () => {
      this._onWizardNext(container);
    });
  },

  _renderWizardStep() {
    const d = this._wizardData;
    switch (this._wizardStep) {
      case 0: // 选择项目
        return `
          <div class="form-group">
            <label class="form-label">项目 <span class="required">*</span></label>
            <select class="form-select" id="wiz-project">
              <option value="">请选择项目</option>
              ${this._projects.map((p) => `<option value="${p.project_id}" ${d.project_id === p.project_id ? "selected" : ""}>${p.project_id} - ${p.name}</option>`).join("")}
            </select>
          </div>`;

      case 1: // 基本信息
        return `
          <div class="form-group">
            <label class="form-label">技术领域 <span class="required">*</span></label>
            <select class="form-select" id="wiz-domain">
              <option value="">请选择领域</option>
              ${Object.entries(DOMAIN_LABELS).map(([k, v]) => `<option value="${k}" ${d.domain === k ? "selected" : ""}>${v} (${k})</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">业务性质 <span class="required">*</span></label>
            <select class="form-select" id="wiz-nature">
              <option value="">请选择性质</option>
              ${Object.entries(NATURE_LABELS).map(([k, v]) => `<option value="${k}" ${d.business_nature === k ? "selected" : ""}>${v} (${k})</option>`).join("")}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">影响范围 <span class="required">*</span>（可多选）</label>
            <div class="form-checkbox-group">
              ${Object.entries(DOMAIN_LABELS).map(([k, v]) => ``).join("")}
              ${Object.entries({
                LOCAL: "局部变更", MODULE: "模块级变更", SYSTEM: "系统级变更",
                CROSS: "跨系统变更", SAFE: "安全相关变更",
              }).map(([k, v]) => `<label class="form-checkbox-label"><input type="checkbox" value="${k}" ${(d.impact_scope || []).includes(k) ? "checked" : ""}>${v}</label>`).join("")}
            </div>
          </div>`;

      case 2: // 申请信息
        return `
          <div class="form-group">
            <label class="form-label">申请人 <span class="required">*</span></label>
            <input class="form-input" id="wiz-applicant" value="${d.applicant || ""}" placeholder="请输入申请人姓名">
          </div>
          <div class="form-group">
            <label class="form-label">变更背景 <span class="required">*</span></label>
            <textarea class="form-textarea" id="wiz-background" placeholder="描述变更背景">${d.background || ""}</textarea>
          </div>
          <div class="form-group">
            <label class="form-label">变更必要性 <span class="required">*</span></label>
            <textarea class="form-textarea" id="wiz-necessity" placeholder="说明变更的必要性">${d.necessity || ""}</textarea>
          </div>`;

      case 3: // 补充信息
        return `
          <div class="form-group">
            <label class="form-label">参考依据</label>
            <input class="form-input" id="wiz-references" value="${d.references || ""}" placeholder="可选，如规范编号、需求文档等">
          </div>
          <div class="form-group">
            <label class="form-label">预计实施日期</label>
            <input class="form-input" id="wiz-planned-date" type="date" value="${d.planned_date || ""}">
          </div>
          <div class="form-group">
            <label class="form-label">紧急程度</label>
            <select class="form-select" id="wiz-urgency">
              ${Object.entries(URGENCY_LABELS).map(([k, v]) => `<option value="${k}" ${(d.urgency || "normal") === k ? "selected" : ""}>${v}</option>`).join("")}
            </select>
          </div>`;

      case 4: // 确认提交
        return `
          <div style="font-size:14px;line-height:2;">
            <p><strong>项目:</strong> ${d.project_id || "未选择"}</p>
            <p><strong>技术领域:</strong> ${DOMAIN_LABELS[d.domain] || d.domain || "未选择"}</p>
            <p><strong>业务性质:</strong> ${NATURE_LABELS[d.business_nature] || d.business_nature || "未选择"}</p>
            <p><strong>影响范围:</strong> ${(d.impact_scope || []).map((s) => {
              const map = { LOCAL: "局部变更", MODULE: "模块级变更", SYSTEM: "系统级变更", CROSS: "跨系统变更", SAFE: "安全相关变更" };
              return map[s] || s;
            }).join(", ") || "未选择"}</p>
            <p><strong>申请人:</strong> ${d.applicant || "未填写"}</p>
            <p><strong>变更背景:</strong> ${d.background || "未填写"}</p>
            <p><strong>变更必要性:</strong> ${d.necessity || "未填写"}</p>
            <p><strong>参考依据:</strong> ${d.references || "无"}</p>
            <p><strong>预计实施日期:</strong> ${d.planned_date || "未指定"}</p>
            <p><strong>紧急程度:</strong> ${URGENCY_LABELS[d.urgency || "normal"]}</p>
          </div>`;

      default:
        return "";
    }
  },

  _collectWizardData() {
    const d = this._wizardData;
    switch (this._wizardStep) {
      case 0: {
        const el = document.getElementById("wiz-project");
        if (el) d.project_id = el.value;
        break;
      }
      case 1: {
        const domainEl = document.getElementById("wiz-domain");
        const natureEl = document.getElementById("wiz-nature");
        if (domainEl) d.domain = domainEl.value;
        if (natureEl) d.business_nature = natureEl.value;
        const checkboxes = document.querySelectorAll(".form-checkbox-group input[type=checkbox]:checked");
        d.impact_scope = Array.from(checkboxes).map((cb) => cb.value);
        break;
      }
      case 2: {
        const applicantEl = document.getElementById("wiz-applicant");
        const bgEl = document.getElementById("wiz-background");
        const necEl = document.getElementById("wiz-necessity");
        if (applicantEl) d.applicant = applicantEl.value;
        if (bgEl) d.background = bgEl.value;
        if (necEl) d.necessity = necEl.value;
        break;
      }
      case 3: {
        const refEl = document.getElementById("wiz-references");
        const dateEl = document.getElementById("wiz-planned-date");
        const urgEl = document.getElementById("wiz-urgency");
        if (refEl) d.references = refEl.value;
        if (dateEl) d.planned_date = dateEl.value || null;
        if (urgEl) d.urgency = urgEl.value;
        break;
      }
    }
  },

  _validateWizardStep() {
    const d = this._wizardData;
    switch (this._wizardStep) {
      case 0:
        if (!d.project_id) { showToast("请选择项目", "warning"); return false; }
        break;
      case 1:
        if (!d.domain) { showToast("请选择技术领域", "warning"); return false; }
        if (!d.business_nature) { showToast("请选择业务性质", "warning"); return false; }
        if (!d.impact_scope || d.impact_scope.length === 0) { showToast("请选择影响范围", "warning"); return false; }
        break;
      case 2:
        if (!d.applicant) { showToast("请填写申请人", "warning"); return false; }
        if (!d.background) { showToast("请填写变更背景", "warning"); return false; }
        if (!d.necessity) { showToast("请填写变更必要性", "warning"); return false; }
        break;
    }
    return true;
  },

  async _onWizardNext(container) {
    this._collectWizardData();
    if (this._wizardStep < 4) {
      if (!this._validateWizardStep()) return;
      this._wizardStep++;
      this._renderCreate(container);
    } else {
      // 提交
      await this._submitCreate(container);
    }
  },

  async _submitCreate(container) {
    const d = this._wizardData;
    try {
      const result = await Api.createChangeRequest(d.project_id, {
        domain: d.domain,
        business_nature: d.business_nature,
        impact_scope: d.impact_scope,
        applicant: d.applicant,
        background: d.background,
        necessity: d.necessity,
        references: d.references || "",
        planned_date: d.planned_date || null,
        urgency: d.urgency || "normal",
      });
      showToast(`变更单 ${result.change_number} 创建成功`, "success");
      this._changeNumber = result.change_number;
      this._view = "detail";
      this._renderView(container);
    } catch (err) {
      if (err.type === "SpecViolationError") {
        showModal({
          icon: "&#9888;",
          title: "规范校验失败",
          body: `<p>创建变更单不符合 CHG-040 规范：</p><p><strong>${err.message}</strong></p>`,
          buttons: [{ label: "关闭", class: "btn-secondary", onClick: closeModal }],
        });
      } else {
        showToast("创建失败: " + (err.message || "未知错误"), "error");
      }
    }
  },

  /* ========== 详情视图 ========== */
  async _renderDetail(container) {
    container.innerHTML = '<div class="loading-spinner">加载变更单详情...</div>';
    try {
      const cr = await Api.getChangeRequest(this._changeNumber);
      this._renderDetailContent(container, cr);
    } catch (err) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">&#9888;</div>
          <div class="empty-state__text">加载失败: ${err.message || "未知错误"}</div>
        </div>`;
    }
  },

  _renderDetailContent(container, cr) {
    const scopeLabels = { LOCAL: "局部变更", MODULE: "模块级变更", SYSTEM: "系统级变更", CROSS: "跨系统变更", SAFE: "安全相关变更" };

    let html = `
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <a href="#/change">变更管理</a>
        <span class="sep">/</span>
        <span class="current">${cr.change_number}</span>
      </div>

      <!-- 页面头部 -->
      <div class="page-header">
        <h1><span class="code">${cr.change_number}</span>变更单详情</h1>
        <div>${statusBadge(cr.status)}</div>
      </div>

      <!-- 基本信息 -->
      <div class="info-grid">
        <div class="card">
          <div class="card__title">编号与项目</div>
          ${this._infoRow("变更编号", cr.change_number)}
          ${this._infoRow("项目编号", cr.project_id)}
          ${this._infoRow("项目名称", cr.project_name)}
        </div>
        <div class="card">
          <div class="card__title">分类信息</div>
          ${this._infoRow("技术领域", DOMAIN_LABELS[cr.domain] || cr.domain)}
          ${this._infoRow("业务性质", NATURE_LABELS[cr.business_nature] || cr.business_nature)}
          ${this._infoRow("影响范围", (cr.impact_scope || []).map((s) => scopeLabels[s] || s).join(", "))}
        </div>
        <div class="card">
          <div class="card__title">申请信息</div>
          ${this._infoRow("申请人", cr.applicant)}
          ${this._infoRow("申请日期", formatDate(cr.apply_date))}
          ${this._infoRow("预计实施", formatDate(cr.planned_date))}
          ${this._infoRow("紧急程度", URGENCY_LABELS[cr.urgency] || cr.urgency)}
        </div>
      </div>

      <!-- 变更原因 -->
      <div class="card mt-16">
        <div class="card__title">变更原因</div>
        <div style="font-size:13px;line-height:1.8;color:var(--text-secondary);padding:8px 0;">
          <p><strong>变更背景:</strong> ${cr.background || "待补充"}</p>
          <p><strong>变更必要性:</strong> ${cr.necessity || "待补充"}</p>
          ${cr.references ? `<p><strong>参考依据:</strong> ${cr.references}</p>` : ""}
        </div>
      </div>

      <!-- 状态流转操作 -->
      <div class="card mt-16">
        <div class="card__title">状态流转</div>
        <div id="transition-area" style="margin-top:12px;">
          ${this._renderTransitionButtons(cr)}
        </div>
      </div>`;

    container.innerHTML = html;

    // 绑定流转按钮事件
    container.querySelectorAll(".btn-transition").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetStatus = btn.dataset.targetStatus;
        this._onTransition(container, cr.change_number, targetStatus, cr.status);
      });
    });
  },

  _renderTransitionButtons(cr) {
    // 根据 STATUS_FLOW 定义允许的下一状态
    const FLOW = {
      draft: [{ target: "submitted", label: "提交审批" }],
      submitted: [{ target: "under_review", label: "进入审核" }, { target: "draft", label: "撤回" }],
      under_review: [
        { target: "approved", label: "批准" },
        { target: "conditionally_approved", label: "有条件批准" },
        { target: "rejected", label: "驳回" },
      ],
      approved: [{ target: "implementing", label: "开始实施" }],
      conditionally_approved: [{ target: "implementing", label: "开始实施" }],
      implementing: [{ target: "completed", label: "完成实施" }, { target: "approved", label: "退回已批准" }],
      completed: [{ target: "closed", label: "关闭" }],
      rejected: [{ target: "draft", label: "退回修改" }],
      closed: [],
    };

    const allowed = FLOW[cr.status] || [];
    if (allowed.length === 0) {
      return '<span class="text-muted">当前状态无可用流转操作</span>';
    }

    // 需要审批人的流转
    const needsApprover = ["approved", "conditionally_approved", "rejected"];

    let html = '<div style="display:flex;gap:10px;flex-wrap:wrap;">';
    allowed.forEach((t) => {
      const needApprover = needsApprover.includes(t.target);
      html += `<button class="btn-primary btn-sm btn-transition" data-target-status="${t.target}" data-needs-approver="${needApprover}">${t.label}</button>`;
    });
    html += "</div>";

    // 审批人/备注输入区（初始隐藏）
    html += `
      <div id="transition-form" style="display:none;margin-top:16px;padding:16px;background:var(--bg-input);border-radius:var(--radius-sm);">
        <div class="form-group">
          <label class="form-label">审批人 <span class="required">*</span></label>
          <input class="form-input" id="transition-approver" placeholder="请输入审批人姓名">
        </div>
        <div class="form-group">
          <label class="form-label">备注</label>
          <textarea class="form-textarea" id="transition-comment" placeholder="可选，如附条件、驳回原因等"></textarea>
        </div>
        <div style="display:flex;gap:10px;">
          <button class="btn-primary btn-sm" id="btn-confirm-transition">确认</button>
          <button class="btn-secondary btn-sm" id="btn-cancel-transition">取消</button>
        </div>
      </div>`;

    return html;
  },

  _onTransition(container, changeNumber, targetStatus, currentStatus) {
    const needsApprover = ["approved", "conditionally_approved", "rejected"].includes(targetStatus);
    const formEl = container.querySelector("#transition-form");

    if (needsApprover) {
      // 显示审批人/备注表单
      formEl.style.display = "block";
      const confirmBtn = container.querySelector("#btn-confirm-transition");
      const cancelBtn = container.querySelector("#btn-cancel-transition");

      // 移除旧事件（防止重复绑定）
      const newConfirm = confirmBtn.cloneNode(true);
      const newCancel = cancelBtn.cloneNode(true);
      confirmBtn.parentNode.replaceChild(newConfirm, confirmBtn);
      cancelBtn.parentNode.replaceChild(newCancel, cancelBtn);

      newConfirm.addEventListener("click", async () => {
        const approver = container.querySelector("#transition-approver").value.trim();
        const comment = container.querySelector("#transition-comment").value.trim();
        if (!approver) {
          showToast("请填写审批人", "warning");
          return;
        }
        await this._doTransition(container, changeNumber, targetStatus, { approver, comment });
      });
      newCancel.addEventListener("click", () => {
        formEl.style.display = "none";
      });
    } else {
      // 直接流转
      this._doTransition(container, changeNumber, targetStatus, {});
    }
  },

  async _doTransition(container, changeNumber, targetStatus, kwargs) {
    try {
      await Api.transitionStatus(changeNumber, targetStatus, kwargs);
      showToast(`状态已更新为 ${STATUS_LABELS[targetStatus] || targetStatus}`, "success");
      // 刷新详情
      this._renderDetail(container);
    } catch (err) {
      if (err.type === "TransitionGuardError") {
        // 门禁条件未满足 — 弹出模态框
        showModal({
          icon: "&#9888;",
          title: "门禁条件未满足",
          body: `
            <p>变更单 <strong>${changeNumber}</strong> 不满足 <strong>${STATUS_LABELS[targetStatus] || targetStatus}</strong> 的门禁条件：</p>
            <ul class="guard-violations">
              ${err.message.split("\n").filter((l) => l.trim().startsWith("-")).map((l) => `<li>${l.trim().replace(/^-\s*/, "")}</li>`).join("")}
            </ul>
            <p class="guard-hint">请编辑变更单文件补充以上内容后重试。</p>`,
          buttons: [{ label: "关闭", class: "btn-secondary", onClick: closeModal }],
        });
      } else if (err.type === "SpecViolationError") {
        showModal({
          icon: "&#9888;",
          title: "状态流转不合法",
          body: `<p>${err.message}</p>`,
          buttons: [{ label: "关闭", class: "btn-secondary", onClick: closeModal }],
        });
      } else {
        showToast("流转失败: " + (err.message || "未知错误"), "error");
      }
    }
  },

  _infoRow(label, value) {
    return `<div class="info-row"><span class="info-row__label">${label}</span><span class="info-row__value">${value || "待补充"}</span></div>`;
  },
};
