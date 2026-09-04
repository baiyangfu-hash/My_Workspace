/**
 * 标准化管理页模块 — 合规仪表盘 + 项目列表 + 检查详情 + 修复交互
 *
 * V9.0.0 新增功能：
 * - 批量扫描工作空间所有项目的结构合规性
 * - 展示合规性仪表盘（总数/通过/警告/失败/合规率）
 * - 项目列表表格（项目名/类型/状态/通过数/警告数/失败数）
 * - 检查详情面板（逐项 pass/warn/fail + 修复建议）
 * - 一键修复 + 文档标准化
 */
const StandardizeModule = {
  _checkData: null,      // 批量检查结果缓存
  _selectedProject: null, // 当前选中的项目路径

  render(container) {
    this._renderMain(container);
  },

  destroy() {
    this._selectedProject = null;
  },

  /* ========== 主视图 ========== */
  _renderMain(container) {
    container.innerHTML = `
      <div class="standardize-page">
        <div class="page-header">
          <h2>标准化管理</h2>
          <div class="page-actions">
            <button class="btn btn-primary" id="std-btn-scan">扫描全部</button>
            <button class="btn" id="std-btn-init">新建项目</button>
          </div>
        </div>
        <div id="std-dashboard" class="std-dashboard">
          <div class="loading-spinner">点击「扫描全部」开始检查...</div>
        </div>
        <div id="std-project-list" class="std-project-list"></div>
        <div id="std-detail-panel" class="std-detail-panel"></div>
      </div>
    `;

    // 绑定事件
    document.getElementById("std-btn-scan").addEventListener("click", () => this._scanAll());
    document.getElementById("std-btn-init").addEventListener("click", () => this._showInitWizard());
  },

  /* ========== 扫描全部 ========== */
  async _scanAll() {
    const dashboard = document.getElementById("std-dashboard");
    dashboard.innerHTML = '<div class="loading-spinner">扫描中...</div>';

    try {
      this._checkData = await Api.plcCheckAll();
      this._renderDashboard();
      this._renderProjectList();
    } catch (err) {
      dashboard.innerHTML = `<div class="error-msg">扫描失败: ${escapeHtml(err.message || err.type)}</div>`;
    }
  },

  /* ========== 合规仪表盘 ========== */
  _renderDashboard() {
    if (!this._checkData) return;
    const d = this._checkData;
    const dashboard = document.getElementById("std-dashboard");
    dashboard.innerHTML = `
      <div class="std-stats">
        <div class="stat-card stat-total">
          <div class="stat-value">${d.total}</div>
          <div class="stat-label">总项目数</div>
        </div>
        <div class="stat-card stat-pass">
          <div class="stat-value">${d.pass_count}</div>
          <div class="stat-label">通过</div>
        </div>
        <div class="stat-card stat-warn">
          <div class="stat-value">${d.warn_count}</div>
          <div class="stat-label">警告</div>
        </div>
        <div class="stat-card stat-fail">
          <div class="stat-value">${d.fail_count}</div>
          <div class="stat-label">失败</div>
        </div>
        <div class="stat-card stat-rate">
          <div class="stat-value">${d.compliance_rate}%</div>
          <div class="stat-label">合规率</div>
        </div>
      </div>
    `;
  },

  /* ========== 项目列表 ========== */
  _renderProjectList() {
    if (!this._checkData) return;
    const listEl = document.getElementById("std-project-list");

    if (!this._checkData.projects || this._checkData.projects.length === 0) {
      listEl.innerHTML = '<div class="empty-msg">未发现任何项目</div>';
      return;
    }

    const rows = this._checkData.projects.map(p => {
      const statusClass = p.all_pass ? "status-pass" : (p.fail_count > 0 ? "status-fail" : "status-warn");
      const statusText = p.all_pass ? "PASS" : (p.fail_count > 0 ? "FAIL" : "WARN");
      return `
        <tr class="project-row" data-path="${escapeHtml(p.project_path)}">
          <td>${escapeHtml(p.project_name)}</td>
          <td>${escapeHtml(p.project_type)}</td>
          <td class="${statusClass}">${statusText}</td>
          <td>${p.pass_count}</td>
          <td>${p.warn_count}</td>
          <td>${p.fail_count}</td>
          <td><button class="btn btn-sm" data-action="detail" data-path="${escapeHtml(p.project_path)}">详情</button></td>
        </tr>
      `;
    }).join("");

    listEl.innerHTML = `
      <table class="std-table">
        <thead>
          <tr>
            <th>项目名</th>
            <th>类型</th>
            <th>状态</th>
            <th>通过</th>
            <th>警告</th>
            <th>失败</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;

    // 绑定详情按钮
    listEl.querySelectorAll("[data-action='detail']").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const path = btn.getAttribute("data-path");
        this._showDetail(path);
      });
    });
  },

  /* ========== 检查详情面板 ========== */
  _showDetail(projectPath) {
    this._selectedProject = projectPath;
    const panel = document.getElementById("std-detail-panel");

    // 从缓存中查找项目检查结果
    const project = this._checkData.projects.find(p => p.project_path === projectPath);
    if (!project) {
      panel.innerHTML = '<div class="error-msg">未找到项目检查结果</div>';
      return;
    }

    const itemsHtml = project.items.map(item => {
      const icon = { pass: "OK", warn: "WARN", fail: "FAIL" }[item.status] || "??";
      const cls = `check-item check-${item.status}`;
      let actionBtn = "";
      if (item.status === "fail") {
        actionBtn = `<button class="btn btn-sm btn-repair" data-item="${escapeHtml(item.item)}">修复</button>`;
      } else if (item.status === "warn" && (item.message.includes("命名不匹配") || item.message.includes("命名不规范"))) {
        actionBtn = `<button class="btn btn-sm btn-standardize" data-item="${escapeHtml(item.item)}">标准化</button>`;
      }
      return `
        <div class="${cls}">
          <span class="check-icon">[${icon}]</span>
          <span class="check-name">${escapeHtml(item.item)}</span>
          <span class="check-msg">${escapeHtml(item.message)}</span>
          ${actionBtn}
        </div>
      `;
    }).join("");

    const repairAllBtn = project.fail_count > 0
      ? `<button class="btn btn-primary" id="std-btn-repair-all">一键修复全部 (${project.fail_count}项)</button>`
      : "";

    panel.innerHTML = `
      <div class="detail-header">
        <h3>${escapeHtml(project.project_name)} - 检查详情</h3>
        <button class="btn btn-sm" id="std-btn-close-detail">关闭</button>
      </div>
      <div class="detail-items">${itemsHtml}</div>
      <div class="detail-actions">
        ${repairAllBtn}
      </div>
    `;

    // 绑定关闭按钮
    document.getElementById("std-btn-close-detail").addEventListener("click", () => {
      panel.innerHTML = "";
      this._selectedProject = null;
    });

    // 绑定单个修复按钮
    panel.querySelectorAll(".btn-repair").forEach(btn => {
      btn.addEventListener("click", () => this._repairProject(false));
    });

    // 绑定单个标准化按钮
    panel.querySelectorAll(".btn-standardize").forEach(btn => {
      btn.addEventListener("click", () => this._standardizeProject(false));
    });

    // 绑定一键修复全部
    const repairAllBtnEl = document.getElementById("std-btn-repair-all");
    if (repairAllBtnEl) {
      repairAllBtnEl.addEventListener("click", () => this._repairProject(false));
    }
  },

  /* ========== 修复项目 ========== */
  async _repairProject(renameConfirm) {
    if (!this._selectedProject) return;

    if (!renameConfirm) {
      // 检查是否有破坏性操作（命名不匹配的WARN项）
      const project = this._checkData.projects.find(p => p.project_path === this._selectedProject);
      const hasRename = project && project.items.some(
        i => i.status === "warn" && (i.message.includes("命名不匹配") || i.message.includes("命名不规范"))
      );
      if (hasRename) {
        const confirmed = confirm("该项目存在命名不匹配的文件（破坏性操作）。\n点击「确定」将同时执行重命名（会自动备份），\n点击「取消」仅修复非破坏性项。");
        if (confirmed) {
          renameConfirm = true;
        }
      }
    }

    const panel = document.getElementById("std-detail-panel");
    panel.innerHTML = '<div class="loading-spinner">修复中...</div>';

    try {
      const result = await Api.plcRepairProject(this._selectedProject, renameConfirm);
      this._renderRepairResult(result);
      // 修复后重新扫描
      setTimeout(() => this._scanAll(), 1000);
    } catch (err) {
      panel.innerHTML = `<div class="error-msg">修复失败: ${escapeHtml(err.message || err.type)}</div>`;
    }
  },

  _renderRepairResult(result) {
    const panel = document.getElementById("std-detail-panel");
    const actionsHtml = result.actions.map(a => {
      const cls = `repair-action action-${a.status}`;
      const destructive = a.destructive ? " [破坏性]" : "";
      return `
        <div class="${cls}">
          <span class="action-status">[${a.status.toUpperCase()}]</span>
          <span class="action-item">${escapeHtml(a.item)}${destructive}</span>
          <span class="action-detail">${escapeHtml(a.detail)}</span>
        </div>
      `;
    }).join("");

    const before = result.before_check || {};
    const after = result.after_check || {};

    panel.innerHTML = `
      <div class="detail-header">
        <h3>修复报告: ${escapeHtml(result.project_name)}</h3>
        <button class="btn btn-sm" id="std-btn-close-detail">关闭</button>
      </div>
      <div class="repair-summary">
        <span class="repair-stat">修复: ${result.fixed_count}</span>
        <span class="repair-stat">跳过: ${result.skipped_count}</span>
        <span class="repair-stat">失败: ${result.failed_count}</span>
      </div>
      <div class="repair-actions">${actionsHtml}</div>
      <div class="repair-comparison">
        <div>修复前: pass=${before.pass_count || 0} warn=${before.warn_count || 0} fail=${before.fail_count || 0}</div>
        <div>修复后: pass=${after.pass_count || 0} warn=${after.warn_count || 0} fail=${after.fail_count || 0}</div>
        ${after.all_pass ? '<div class="success-msg">项目已全部通过检查</div>' : `<div class="warn-msg">仍有 ${after.fail_count || 0} 项未通过</div>`}
      </div>
    `;

    document.getElementById("std-btn-close-detail").addEventListener("click", () => {
      panel.innerHTML = "";
    });
  },

  /* ========== 文档标准化 ========== */
  async _standardizeProject(apply) {
    if (!this._selectedProject) return;

    if (!apply) {
      // 先检测预览
      const panel = document.getElementById("std-detail-panel");
      panel.innerHTML = '<div class="loading-spinner">检测中...</div>';

      try {
        const result = await Api.plcStandardizeProject(this._selectedProject, false);
        this._renderStandardizePreview(result);
      } catch (err) {
        panel.innerHTML = `<div class="error-msg">检测失败: ${escapeHtml(err.message || err.type)}</div>`;
      }
    }
  },

  _renderStandardizePreview(result) {
    const panel = document.getElementById("std-detail-panel");

    if (!result.plans || result.plans.length === 0) {
      panel.innerHTML = '<div class="info-msg">无需标准化（所有文档命名已符合规范）</div>';
      return;
    }

    const plansHtml = result.plans.map(p => `
      <div class="rename-plan">
        <span class="plan-type">[${p.doc_type}]</span>
        <span class="plan-old">${escapeHtml(p.old_name)}</span>
        <span class="plan-arrow">→</span>
        <span class="plan-new">${escapeHtml(p.new_name)}</span>
      </div>
    `).join("");

    panel.innerHTML = `
      <div class="detail-header">
        <h3>文档标准化预览: ${escapeHtml(result.project_name)}</h3>
        <button class="btn btn-sm" id="std-btn-close-detail">关闭</button>
      </div>
      <div class="standardize-plans">${plansHtml}</div>
      <div class="detail-actions">
        <button class="btn btn-primary" id="std-btn-apply-standardize">执行重命名（自动备份）</button>
      </div>
    `;

    document.getElementById("std-btn-close-detail").addEventListener("click", () => {
      panel.innerHTML = "";
    });

    document.getElementById("std-btn-apply-standardize").addEventListener("click", async () => {
      const confirmed = confirm("确认执行重命名？将自动备份原文件（.bak后缀）。");
      if (confirmed) {
        panel.innerHTML = '<div class="loading-spinner">执行中...</div>';
        try {
          const applyResult = await Api.plcStandardizeProject(this._selectedProject, true);
          this._renderStandardizeResult(applyResult);
          setTimeout(() => this._scanAll(), 1000);
        } catch (err) {
          panel.innerHTML = `<div class="error-msg">执行失败: ${escapeHtml(err.message || err.type)}</div>`;
        }
      }
    });
  },

  _renderStandardizeResult(result) {
    const panel = document.getElementById("std-detail-panel");
    const plansHtml = result.plans.map(p => `
      <div class="rename-plan ${p.applied ? "applied" : "skipped"}">
        <span class="plan-type">[${p.doc_type}]</span>
        <span class="plan-old">${escapeHtml(p.old_name)}</span>
        <span class="plan-arrow">→</span>
        <span class="plan-new">${escapeHtml(p.new_name)}</span>
        <span class="plan-status">${p.applied ? "已执行" : "未执行"}</span>
      </div>
    `).join("");

    const refUpdatesHtml = result.reference_updates && result.reference_updates.length > 0
      ? `<div class="ref-updates"><h4>关联引用更新 (${result.reference_updates.length} 处)</h4>${result.reference_updates.map(u => `<div class="ref-update">${escapeHtml(u)}</div>`).join("")}</div>`
      : "";

    panel.innerHTML = `
      <div class="detail-header">
        <h3>标准化结果: ${escapeHtml(result.project_name)}</h3>
        <button class="btn btn-sm" id="std-btn-close-detail">关闭</button>
      </div>
      <div class="repair-summary">
        <span class="repair-stat">已执行: ${result.applied_count}</span>
        <span class="repair-stat">跳过: ${result.skipped_count}</span>
      </div>
      <div class="standardize-plans">${plansHtml}</div>
      ${refUpdatesHtml}
    `;

    document.getElementById("std-btn-close-detail").addEventListener("click", () => {
      panel.innerHTML = "";
    });
  },

  /* ========== 新建项目向导 ========== */
  _showInitWizard() {
    const modal = document.getElementById("modal-content");
    modal.innerHTML = `
      <div class="wizard">
        <h3>新建项目</h3>
        <div class="wizard-step">
          <label>项目类型:</label>
          <select id="init-type">
            <option value="standard">标准PLC项目</option>
            <option value="syslib_fb">SysLib功能块</option>
          </select>
        </div>
        <div class="wizard-step">
          <label>项目编号:</label>
          <input type="text" id="init-id" placeholder="如 DJ-2026-010">
        </div>
        <div class="wizard-step">
          <label>项目名称:</label>
          <input type="text" id="init-name" placeholder="如 边框缓存机">
        </div>
        <div class="wizard-step">
          <label>项目描述:</label>
          <input type="text" id="init-desc" placeholder="可选，默认使用项目名称">
        </div>
        <div class="wizard-actions">
          <button class="btn" id="init-cancel">取消</button>
          <button class="btn btn-primary" id="init-confirm">创建</button>
        </div>
      </div>
    `;

    document.getElementById("modal-overlay").classList.add("active");

    document.getElementById("init-cancel").addEventListener("click", () => {
      document.getElementById("modal-overlay").classList.remove("active");
    });

    document.getElementById("init-confirm").addEventListener("click", async () => {
      const projectId = document.getElementById("init-id").value.trim();
      const projectName = document.getElementById("init-name").value.trim();
      const projectType = document.getElementById("init-type").value;
      const description = document.getElementById("init-desc").value.trim();

      if (!projectId || !projectName) {
        alert("请填写项目编号和名称");
        return;
      }

      try {
        const result = await Api.plcInitProject(projectId, projectName, projectType, description);
        document.getElementById("modal-overlay").classList.remove("active");
        alert(`项目创建成功: ${result.project_id}\n创建文件数: ${result.created_files.length}`);
        this._scanAll();
      } catch (err) {
        alert(`创建失败: ${err.message || err.type}`);
      }
    });
  },
};
