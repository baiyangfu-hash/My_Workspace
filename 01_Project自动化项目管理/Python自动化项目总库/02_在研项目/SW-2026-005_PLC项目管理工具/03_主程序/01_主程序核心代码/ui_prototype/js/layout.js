function toggleSidebar() {
  state.sidebarCollapsed = !state.sidebarCollapsed;
  document.getElementById('sidebar').classList.toggle('collapsed', state.sidebarCollapsed);
}

function toggleSection(sectionId) {
  state.collapseState[sectionId] = !state.collapseState[sectionId];
  const body = document.getElementById('body-' + sectionId);
  const arrow = document.getElementById('arrow-' + sectionId);
  if (body) body.classList.toggle('collapsed', !state.collapseState[sectionId]);
  if (arrow) arrow.classList.toggle('open', state.collapseState[sectionId]);
}

function toggleBottomPanel() {
  state.bottomPanelOpen = !state.bottomPanelOpen;
  document.getElementById('bottomPanel').classList.toggle('open', state.bottomPanelOpen);
  document.getElementById('bottomPanel').classList.toggle('closed', !state.bottomPanelOpen);
}

function switchBottomTab(tab) {
  state.bottomPanelActiveTab = tab;
  document.querySelectorAll('.bottom-panel-tab').forEach(t => {
    t.classList.toggle('active', t.textContent.includes(tab === 'output' ? '输出' : tab === 'problems' ? '问题' : '终端'));
  });
  const body = document.getElementById('bottomPanelBody');
  if (tab === 'problems') {
    body.innerHTML = `
      <div class="panel-output">
<span class="output-warn">⚠️ [警告] OB1.scl:45 - COM-002: 注释包含中文标点 "，"</span>
<span class="output-warn">⚠️ [警告] OB1.scl:78 - COM-002: 注释包含中文标点 "。"</span>
<span class="output-warn">⚠️ [警告] FB_Valve.scl:23 - VAR-001: 变量 "tmp" 命名不明确</span>
      </div>`;
  } else if (tab === 'terminal') {
    body.innerHTML = `
      <div class="panel-output">
<span style="color:var(--success);">PS C:\\Workspace\\DJ-2026-005></span> <span style="color:var(--info);">specmgr check</span>
<span class="output-info">[INFO] 规范健康检查完成: 5/7 检查器通过, 5 警告</span>
      </div>`;
  } else {
    body.innerHTML = `
      <div class="panel-output">
<span class="output-info">[06:59:32]</span> 显示器采样: 2880x1800 @ dpr=2.00
<span class="output-info">[06:59:32]</span> UI缩放配置: scale_factor=1.32, base_font=15pt
<span class="output-success">[06:59:33]</span> 主窗口初始化完成 (IDE布局)
<span class="output-success">[06:59:33]</span> 字体: Microsoft YaHei UI 15pt
<span class="output-success">[06:59:33]</span> GUI应用启动成功
      </div>`;
  }
}

function updateStatusBarProject(pid) {
  const el = document.querySelector('.status-project');
  if (el) el.textContent = '\u{1F4C1} ' + (pid || '-');
}
