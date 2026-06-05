/**
 * SPA 核心：路由管理 + 导航渲染 + 页面切换 + 全局组件
 */

/* ========== 全局状态 ========== */
let currentModule = null;
let currentRoute = "";

const contentEl = document.getElementById("content");
const toastContainer = document.getElementById("toast-container");
const modalOverlay = document.getElementById("modal-overlay");
const modalContent = document.getElementById("modal-content");

/* ========== 路由表 ========== */
const routes = {
  dashboard: { module: null, title: "总览" },
  detail: { module: null, title: "项目详情" },
  change: { module: null, title: "变更管理" },
};

/* ========== 路由初始化 ========== */
function initRouter() {
  // 延迟绑定模块（确保各模块 JS 已加载）
  routes.dashboard.module = DashboardModule;
  routes.detail.module = DetailModule;
  routes.change.module = ChangeModule;

  // 监听 hash 变化
  window.addEventListener("hashchange", () => navigate(location.hash));

  // 初始导航
  if (!location.hash || location.hash === "#/") {
    location.hash = "#/dashboard";
  } else {
    navigate(location.hash);
  }
}

/**
 * 导航到指定路由
 * @param {string} hash - 如 "#/dashboard" 或 "#/detail/DJ-2026-005"
 */
function navigate(hash) {
  const path = hash.replace("#", "");
  const parts = path.split("/").filter(Boolean);
  const routeName = parts[0] || "dashboard";
  const params = parts.slice(1).join("/");

  const route = routes[routeName];
  if (!route) {
    // 未知路由回首页
    location.hash = "#/dashboard";
    return;
  }

  // 销毁旧模块
  if (currentModule && typeof currentModule.destroy === "function") {
    currentModule.destroy();
  }

  // 切换模块
  currentRoute = routeName;
  currentModule = route.module;

  // 显示加载状态
  contentEl.innerHTML = '<div class="loading-spinner">加载中...</div>';

  // 渲染新模块
  if (currentModule && typeof currentModule.render === "function") {
    currentModule.render(contentEl, params);
  }

  // 更新导航高亮
  updateNavActive(routeName);
}

/** 更新导航栏高亮 */
function updateNavActive(routeName) {
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === routeName);
  });
}

/* ========== Toast 通知 ========== */
/**
 * 显示 Toast 通知
 * @param {string} message - 消息文本
 * @param {"success"|"error"|"warning"|"info"} type - 类型
 * @param {number} duration - 自动消失时间(ms)，0=不自动消失
 */
function showToast(message, type = "info", duration = 3000) {
  const toast = document.createElement("div");
  toast.className = `toast toast--${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

/* ========== Modal 模态框 ========== */
/**
 * 显示模态框
 * @param {object} options
 * @param {string} options.icon - 图标字符
 * @param {string} options.title - 标题
 * @param {string} options.body - HTML 内容
 * @param {Array<{label:string, class:string, onClick:Function}>} options.buttons - 按钮
 */
function showModal({ icon = "", title = "", body = "", buttons = [] } = {}) {
  let html = '<div class="modal__header">';
  if (icon) html += `<span class="modal__icon">${icon}</span>`;
  html += `<span class="modal__title">${title}</span></div>`;
  html += `<div class="modal__body">${body}</div>`;

  if (buttons.length) {
    html += '<div class="modal__footer">';
    buttons.forEach((btn, i) => {
      html += `<button class="${btn.class || "btn-secondary"}" data-btn-idx="${i}">${btn.label}</button>`;
    });
    html += "</div>";
  }

  modalContent.innerHTML = html;
  modalOverlay.classList.add("visible");

  // 绑定按钮事件
  buttons.forEach((btn, i) => {
    const el = modalContent.querySelector(`[data-btn-idx="${i}"]`);
    if (el && typeof btn.onClick === "function") {
      el.addEventListener("click", () => {
        btn.onClick();
      });
    }
  });
}

/** 关闭模态框 */
function closeModal() {
  modalOverlay.classList.remove("visible");
  modalContent.innerHTML = "";
}

// 点击遮罩关闭
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

/* ========== 全局事件 ========== */

// 刷新按钮
document.getElementById("btn-refresh").addEventListener("click", async () => {
  try {
    await Api.refreshCache();
    showToast("缓存已刷新", "success");
    // 重新渲染当前页面
    if (currentModule && typeof currentModule.render === "function") {
      currentModule.render(contentEl, "");
    }
  } catch (err) {
    showToast("刷新失败: " + (err.message || "未知错误"), "error");
  }
});

/* ========== 工具函数 ========== */

/** 状态显示名映射 */
const STATUS_LABELS = {
  draft: "草稿",
  submitted: "已提交",
  under_review: "审核中",
  approved: "已批准",
  conditionally_approved: "有条件批准",
  rejected: "已驳回",
  implementing: "实施中",
  completed: "已完成",
  closed: "已关闭",
};

/** 领域显示名映射 */
const DOMAIN_LABELS = {
  ELEC: "电气设计",
  MECH: "机械结构",
  PLC: "PLC程序",
  HMI: "HMI程序",
  SCPT: "Python脚本",
  DOCU: "工程文档",
  SAFE: "安全功能",
};

/** 业务性质显示名映射 */
const NATURE_LABELS = {
  REQ: "需求变更",
  DEF: "缺陷修复",
  OPT: "优化改进",
  CFG: "配置调整",
  EMRG: "紧急变更",
};

/** 紧急程度显示名映射 */
const URGENCY_LABELS = {
  normal: "一般",
  urgent: "紧急",
  critical: "非常紧急",
};

/** 阶段显示名映射 */
const PHASE_LABELS = {
  developing: "开发中",
  commissioning: "调试中",
  production: "生产中",
  archived: "已归档",
};

/** 生成状态徽章 HTML */
function statusBadge(status) {
  const label = STATUS_LABELS[status] || status;
  return `<span class="status-badge status-${status}">${label}</span>`;
}

/** 格式化日期 */
function formatDate(dateStr) {
  if (!dateStr || dateStr === "待补充") return "待补充";
  return dateStr;
}

/** 启动应用 */
document.addEventListener("DOMContentLoaded", () => {
  initRouter();
});
