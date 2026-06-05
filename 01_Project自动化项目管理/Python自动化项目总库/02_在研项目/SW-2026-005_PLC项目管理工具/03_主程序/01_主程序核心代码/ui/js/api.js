/**
 * Bridge API 封装层
 * 统一 PyWebView IPC 调用方式，处理异步等待、错误解析
 */
const Api = {
  _ready: false,

  /** 等待 pywebview.api 就绪 */
  async _ensureReady() {
    if (this._ready) return;
    await new Promise((resolve) => {
      if (window.pywebview && window.pywebview.api) {
        this._ready = true;
        resolve();
      } else {
        window.addEventListener("pywebviewready", () => {
          this._ready = true;
          resolve();
        });
      }
    });
  },

  /**
   * 统一调用入口
   * @param {string} method - Bridge 方法名
   * @param  {...any} args - 参数
   * @returns {Promise<any>} 返回值
   * @throws {{type: string, message: string}} Bridge 错误
   */
  async _call(method, ...args) {
    await this._ensureReady();
    const api = window.pywebview.api;
    if (!api || typeof api[method] !== "function") {
      throw { type: "InternalError", message: `API 方法 ${method} 不可用` };
    }
    // 超时保护：防止 Bridge 调用卡死导致前端永久转圈
    const TIMEOUT_MS = 15000;
    const result = await Promise.race([
      api[method](...args),
      new Promise((_, reject) =>
        setTimeout(() => reject({ type: "TimeoutError", message: `调用 ${method} 超时(${TIMEOUT_MS / 1000}s)` }), TIMEOUT_MS)
      ),
    ]);
    // Bridge 返回 {error, message} 表示业务错误
    if (result && result.error) {
      throw { type: result.error, message: result.message };
    }
    return result;
  },

  // ---- 项目总览 ----
  getWorkspaceProjects() {
    return this._call("get_workspace_projects");
  },
  getProjectDetail(projectId) {
    return this._call("get_project_detail", projectId);
  },
  getProjectChanges(projectId) {
    return this._call("get_project_changes", projectId);
  },
  refreshCache(projectId) {
    return this._call("refresh_cache", projectId || null);
  },

  // ---- 变更管理 ----
  createChangeRequest(projectId, fields) {
    return this._call("create_change_request", projectId, fields);
  },
  listChangeRequests(projectId, filters) {
    return this._call("list_change_requests", projectId, filters);
  },
  getChangeRequest(changeNumber) {
    return this._call("get_change_request", changeNumber);
  },
  transitionStatus(changeNumber, newStatus, kwargs) {
    return this._call("transition_status", changeNumber, newStatus, kwargs);
  },

  // ---- 规范常量 ----
  getSpecConstants() {
    return this._call("get_spec_constants");
  },

  // ---- 工作空间管理 ----
  getWorkspaceInfo() {
    return this._call("get_workspace_info");
  },
  setWorkspace(path) {
    return this._call("set_workspace", path);
  },
  selectWorkspace() {
    return this._call("select_workspace");
  },
};
