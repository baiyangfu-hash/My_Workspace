function renderSettings() {
  const s = state.settings;
  return `
    <div class="settings-layout">
      <div class="settings-section">
        <div class="settings-section-header">🖥 常规设置</div>
        <div class="settings-section-body">
          <div class="settings-row">
            <div>
              <div class="settings-row-label">默认项目路径</div>
              <div class="settings-row-desc">新建项目的默认存储位置</div>
            </div>
            <div style="display:flex;gap:4px;align-items:center;">
              <input class="form-input" id="settProjectPath" value="${_escHtml(s.default_project_path || '')}" style="width:240px;">
              <button class="btn btn-sm btn-secondary" onclick="onBrowseSettingPath('settProjectPath')">📂</button>
            </div>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-row-label">自动保存</div>
              <div class="settings-row-desc">编辑文档时自动保存变更</div>
            </div>
            <input type="checkbox" id="settAutoSave" ${s.auto_save !== false ? 'checked' : ''} style="width:16px;height:16px;accent-color:var(--accent);">
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-row-label">日志级别</div>
            </div>
            <select class="form-input" id="settLogLevel" style="width:140px;">
              <option ${s.log_level === 'DEBUG' ? 'selected' : ''}>DEBUG</option>
              <option ${s.log_level === 'INFO' || !s.log_level ? 'selected' : ''}>INFO</option>
              <option ${s.log_level === 'WARNING' ? 'selected' : ''}>WARNING</option>
              <option ${s.log_level === 'ERROR' ? 'selected' : ''}>ERROR</option>
            </select>
          </div>
        </div>
      </div>

      <div class="settings-section">
        <div class="settings-section-header">📝 编辑器</div>
        <div class="settings-section-body">
          <div class="settings-row">
            <div>
              <div class="settings-row-label">字体</div>
            </div>
            <select class="form-input" id="settFont" style="width:200px;">
              <option selected>Microsoft YaHei UI</option>
              <option>Consolas</option>
              <option>Cascadia Code</option>
            </select>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-row-label">字号</div>
            </div>
            <input class="form-input" id="settFontSize" value="${s.font_size || 15}" type="number" style="width:80px;">
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-row-label">制表符宽度</div>
            </div>
            <input class="form-input" id="settTabWidth" value="${s.tab_width || 4}" type="number" style="width:80px;">
          </div>
        </div>
      </div>

      <div class="settings-section">
        <div class="settings-section-header">🎨 外观</div>
        <div class="settings-section-body">
          <div class="settings-row">
            <div>
              <div class="settings-row-label">主题</div>
            </div>
            <select class="form-input" id="settTheme" style="width:140px;">
              <option ${s.theme === 'dark' || !s.theme ? 'selected' : ''} value="dark">深色工业风</option>
              <option ${s.theme === 'light' ? 'selected' : ''} value="light">浅色专业风</option>
            </select>
          </div>
          <div class="settings-row">
            <div>
              <div class="settings-row-label">UI密度</div>
            </div>
            <select class="form-input" id="settDensity" style="width:140px;">
              <option>紧凑</option>
              <option>标准</option>
              <option>舒适</option>
              <option selected>工控机模式</option>
            </select>
          </div>
        </div>
      </div>

      <div style="display:flex;gap:8px;justify-content:flex-end;">
        <button class="btn btn-secondary" onclick="onResetSettings()">恢复默认</button>
        <button class="btn btn-primary" onclick="onSaveSettings()">💾 保存设置</button>
      </div>

      <div class="settings-section" style="margin-top:16px;">
        <div class="settings-section-header">🔧 IPC通信测试</div>
        <div class="settings-section-body">
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            <button class="btn btn-primary" onclick="runIpcTest('ping')">Ping</button>
            <button class="btn btn-secondary" onclick="runIpcTest('app_info')">应用信息</button>
            <button class="btn btn-secondary" onclick="runIpcTest('recent_projects')">最近项目</button>
            <button class="btn btn-secondary" onclick="runIpcTest('checkers')">检查器列表</button>
            <button class="btn btn-secondary" onclick="runIpcTest('spec_check')">规范检查</button>
            <button class="btn btn-secondary" onclick="runIpcTest('diagnosis')">诊断分析</button>
            <button class="btn btn-secondary" onclick="runIpcTest('version_check')">版本检查</button>
            <button class="btn btn-secondary" onclick="runIpcTest('settings')">获取设置</button>
          </div>
          <pre id="ipcTestOutput" style="background:#1A1A1A;border:1px solid #3E3E42;border-radius:4px;padding:12px;font-size:11px;color:#4EC9B0;max-height:240px;overflow:auto;min-height:60px;">点击上方按钮测试IPC通信...</pre>
        </div>
      </div>
    </div>
  `;
}
