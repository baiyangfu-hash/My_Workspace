function renderDocumentEditor() {
  return `
    <div class="editor-layout">
      <div class="editor-main">
        <div class="editor-toolbar">
          <span style="font-size:12px;color:var(--text-secondary);">📄 文档编辑器</span>
          <span class="editor-toolbar-spacer"></span>
          <button class="editor-toolbar-btn" onclick="onInsertVariable()">📋 变量</button>
          <button class="editor-toolbar-btn" onclick="showToast('预览功能开发中', 'info')">👁 预览</button>
          <button class="btn btn-primary btn-sm" onclick="onSaveDocument()">💾 保存</button>
        </div>
        <textarea class="editor-content" id="docContent" placeholder="在此编辑文档内容...">${state.currentProject ? '# ' + _escHtml(state.currentProject.name || '') + ' 文档\\n\\n## 1. 概述\\n- **项目编号**: ' + _escHtml(state.currentProject.project_id || '') + '\\n- **项目类型**: ' + _escHtml(state.currentProject.project_type || '') + '\\n\\n## 2. 详细内容\\n' : '请先打开项目后编辑文档'}</textarea>
      </div>
      <div class="editor-sidebar">
        <div class="tree-header">📋 模板变量</div>
        <div class="variable-list">
          <div class="variable-item" onclick="onInsertVariable('PROJECT_NAME')">
            <span class="variable-key">{{PROJECT_NAME}}</span>
            <span class="variable-val">${_escHtml(state.currentProject?.name || '-')}</span>
          </div>
          <div class="variable-item" onclick="onInsertVariable('PROJECT_ID')">
            <span class="variable-key">{{PROJECT_ID}}</span>
            <span class="variable-val">${_escHtml(state.currentProject?.project_id || '-')}</span>
          </div>
          <div class="variable-item" onclick="onInsertVariable('PROJECT_TYPE')">
            <span class="variable-key">{{PROJECT_TYPE}}</span>
            <span class="variable-val">${_escHtml(state.currentProject?.project_type || '-')}</span>
          </div>
          <div class="variable-item" onclick="onInsertVariable('PROJECT_OWNER')">
            <span class="variable-key">{{PROJECT_OWNER}}</span>
            <span class="variable-val">${_escHtml(state.currentProject?.manager || '-')}</span>
          </div>
          <div class="variable-item" onclick="onInsertVariable('CREATE_DATE')">
            <span class="variable-key">{{CREATE_DATE}}</span>
            <span class="variable-val">${new Date().toISOString().split('T')[0]}</span>
          </div>
        </div>
      </div>
    </div>
  `;
}
