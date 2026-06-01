function showToast(msg, type) {
  type = type || 'info';
  const container = document.getElementById('toastContainer');
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  container.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, 3000);
}

function _escHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function _statusBadgeHtml(status) {
  const map = {
    draft: '<span class="status-badge draft">📝 草稿</span>',
    review: '<span class="status-badge in-progress">🔍 审核中</span>',
    approved: '<span class="status-badge approved">✅ 已审批</span>',
    in_progress: '<span class="status-badge in-progress">🔄 进行中</span>',
    implemented: '<span class="status-badge approved">✔ 已实施</span>',
    completed: '<span class="status-badge approved">✅ 已完成</span>',
    cancelled: '<span class="status-badge rejected">❌ 已取消</span>',
  };
  return map[status] || '<span class="status-badge draft">' + status + '</span>';
}
