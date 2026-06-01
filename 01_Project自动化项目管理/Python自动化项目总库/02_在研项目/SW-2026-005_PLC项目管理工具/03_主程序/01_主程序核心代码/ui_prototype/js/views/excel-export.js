function renderExcelExport() {
  return `
    <div style="display:flex;flex-direction:column;gap:12px;">
      <div style="display:flex;gap:8px;align-items:center;">
        <button class="btn btn-primary" onclick="onExportExcelSingle()">📊 导出单个FB</button>
        <button class="btn btn-secondary" onclick="onExportExcelBatch()">📦 批量导出</button>
      </div>
      <div style="color:var(--text-muted);padding:16px;text-align:center;">
        选择FB源文件(.scl)导出接口变量表到Excel(9列格式)
      </div>
    </div>
  `;
}
