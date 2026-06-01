function renderSpecCheck() {
  const sel = state.checkerSelections;
  const total = Object.values(sel).filter(Boolean).length;
  const max  = Object.keys(sel).length;

  const cards = [
    { id:'syntax',   icon:'📝', name:'语法检查',     engine:'Trae插件', engineClass:'trae',   desc:'SCL语法错误检测 · 关键字 · 括号匹配 · 类型推断' },
    { id:'comment',  icon:'💬', name:'注释检查',     engine:'Trae插件', engineClass:'trae',   desc:'中文标点 · 嵌套注释 · 注释完整性 · 文档注释规范' },
    { id:'naming',   icon:'🏷', name:'命名规范检查', engine:'Python内置', engineClass:'python', desc:'变量/函数块/常量命名 · 前缀后缀规则 · 长度限制' },
    { id:'variable', icon:'📦', name:'变量检查',     engine:'混合',     engineClass:'hybrid',  desc:'声明未使用 · 类型一致性 · 作用域分析 · 全局变量引用' },
    { id:'config',   icon:'⚙', name:'配置检查',     engine:'Python内置', engineClass:'python', desc:'项目配置完整性 · 路径有效性 · 依赖版本 · 环境一致性' },
    { id:'timer',    icon:'⏱', name:'定时器检查',   engine:'Python内置', engineClass:'python', desc:'TON/TOF/TP使用模式 · 预设值范围 · 复位逻辑 · 级联嵌套' },
    { id:'fb_iface', icon:'🔗', name:'FB接口调用检查', engine:'混合',   engineClass:'hybrid',  desc:'OB1调用参数匹配 · 输入缺参/多参 · 输出接出 · IN_OUT对齐' },
  ];

  const sr = state.specResults;
  let resultHtml = '';
  if (sr && sr.results && sr.results.length > 0) {
    const summary = sr.summary || {};
    resultHtml = `
      <div class="result-header">
        📋 检查结果
        <div class="result-summary">
          <span class="rs-error">🔴 ${summary.error || 0} 错误</span>
          <span class="rs-warn">🟡 ${summary.warning || 0} 警告</span>
          <span class="rs-info">🔵 ${summary.info || 0} 提示</span>
        </div>
      </div>
      <table class="result-table">
        <thead>
          <tr>
            <th>严重度</th>
            <th>文件</th>
            <th>行</th>
            <th>规则</th>
            <th>描述</th>
          </tr>
        </thead>
        <tbody>
          ${sr.results.map(r => {
            const sevClass = r.severity === 'error' ? 'error' : r.severity === 'warning' ? 'warning' : 'info';
            const sevIcon = r.severity === 'error' ? '🔴' : r.severity === 'warning' ? '⚠️' : '🔵';
            return `<tr>
              <td><span class="severity-icon ${sevClass}">${sevIcon}</span> ${r.severity || ''}</td>
              <td style="color:var(--info);">${_escHtml(r.file || '')}</td>
              <td>${r.line || '-'}</td>
              <td>${_escHtml(r.rule || '')}</td>
              <td>${_escHtml(r.message || '')}</td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    `;
  } else {
    resultHtml = `
      <div class="result-header">
        📋 检查结果
        <div class="result-summary">
          <span class="rs-info">选择检查器后点击"开始检查"</span>
        </div>
      </div>
    `;
  }

  return `
    <div class="spec-layout">

      <div class="checker-grid">
        ${cards.map(c => `
          <div class="checker-card ${sel[c.id] ? 'selected' : 'unselected'}"
               onclick="toggleChecker('${c.id}')"
               title="${c.desc}">
            <div class="check-toggle">✓</div>
            <span class="check-icon">${c.icon}</span>
            <div class="check-info">
              <div class="check-name">${c.name}</div>
              <div class="check-count">${c.desc}</div>
            </div>
            <span class="check-engine ${c.engineClass}">${c.engine}</span>
          </div>
        `).join('')}
      </div>

      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <button class="btn btn-primary" onclick="runCheck()">🔍 开始检查 (${total}/${max})</button>
        <button class="btn btn-secondary" onclick="selectAllCheckers()">✅ 全选</button>
        <button class="btn btn-secondary" onclick="deselectAllCheckers()">☐ 取消全选</button>
        <span style="flex:1;"></span>
        <button class="btn btn-secondary" onclick="openTab('spec','spec-auto-fix')">🔧 自动修复</button>
        <button class="btn btn-secondary" onclick="openTab('spec','spec-excel')">📊 导出Excel</button>
      </div>

      <div class="result-panel">
        ${resultHtml}
      </div>
    </div>
  `;
}
