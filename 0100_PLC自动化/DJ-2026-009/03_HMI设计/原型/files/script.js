/* ============================================================
 * DJ-2026-009 长边框自动码垛机 HMI 原型 —— 页面切换 & 逻辑
 * 说明：真实码垛机只与上游输送机交互，不包含打胶机和机器人。
 * ============================================================ */

// 顶部导航 Tab 对应的真实画面清单
const pages = [
  { id: 'login',   name: '01 登录' },
  { id: 'main',    name: '02 主画面' },
  { id: 'infeed',  name: '03 上游输送交互' },
  { id: 'recipe',  name: '04 叠垛配方' },
  { id: 'alarm',   name: '05 报警管理' },
];

const CLOCK_IDS = ['clockMain'];

function renderNavTabs() {
  const navTabs = document.getElementById('navTabs');
  if (!navTabs) return;
  navTabs.innerHTML = '';
  pages.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'nav-tab' + (p.id === 'login' ? ' active' : '');
    btn.textContent = p.name;
    btn.onclick = () => goPage(p.id);
    navTabs.appendChild(btn);
  });
}

function goPage(id) {
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach((el, i) => {
    el.classList.toggle('active', pages[i] && pages[i].id === id);
  });
  const target = document.getElementById('page-' + id);
  if (target) target.classList.add('active');
}

function tick() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const date = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const time = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  const full = `${date} ${time}`;

  CLOCK_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = full;
  });
}

function fitToScreen() {
  const DESIGN_W = 1280;
  const DESIGN_H = 800;
  const inner = document.getElementById('appScaleInner');
  if (!inner) return;
  const sw = window.innerWidth / DESIGN_W;
  const sh = window.innerHeight / DESIGN_H;
  const scale = Math.min(sw, sh, 1);
  inner.style.transform = `scale(${scale})`;
}

window.addEventListener('resize', fitToScreen);
window.addEventListener('load', () => {
  renderNavTabs();
  fitToScreen();
  setInterval(tick, 1000);
  tick();
});
