document.querySelectorAll('.activity-item').forEach(item => {
  item.addEventListener('click', () => switchActivity(item.dataset.view));
});

document.getElementById('sidebarContent').innerHTML = sidebarTemplates['dashboard'];
document.getElementById('contentMain').innerHTML = renderDashboard();

async function _initApp() {
  const s = await _pyapi('get_settings');
  if (s) state.settings = s;
  await ipcGetDashboardStats();
  await ipcListChangeRequests();
  renderContent('dashboard');
}

setTimeout(() => {
  _ipcAutoPing();
  setTimeout(_initApp, 500);
}, 1500);
