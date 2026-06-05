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
    const result = await api[method](...args);
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
};
