/* ============================================================
 * DJ-2026-005 边框缓存机 HMI 原型 —— 页面切换 & 时钟逻辑
 * 说明：本文件只负责“画面导航”和“页头时钟”两件事，
 * 目前仅为静态原型演示，不含真实 PLC 通信逻辑。
 * ============================================================ */

// 顶部导航 Tab 对应的 11 个画面（id 需与 <div class="page" id="page-xxx"> 一一对应）
const pages = [
  { id: 'login',   name: '01 登录' },
  { id: 'main',    name: '02 主画面' },
  { id: 'manual',  name: '03 手动控制' },
  { id: 'auto',    name: '04 自动运行' },
  { id: 'param',   name: '05 参数设置' },
  { id: 'status',  name: '06 状态监控' },
  { id: 'io',      name: '07 IO监控 ✦' },
  { id: 'alarm',   name: '08 报警管理' },
  { id: 'glue',    name: '09 打胶机交互' },
  { id: 'robot',   name: '10 机器人交互' },
  { id: 'system',  name: '11 系统设置' },
];

// 需要每秒刷新的时钟元素 id 列表（主画面显示完整日期+时间，其余画面只显示时间）
const CLOCK_IDS = [
  'clockMain', 'clockManual', 'clockAuto', 'clockParam', 'clockStatus',
  'clockIo', 'clockAlarm', 'clockGlue', 'clockRobot', 'clockSystem',
];

/** 根据 pages 数组动态生成顶部导航 Tab 按钮 */
function renderNavTabs() {
  const navTabs = document.getElementById('navTabs');
  if (!navTabs) return;
  pages.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'nav-tab' + (p.id === 'login' ? ' active' : '');
    btn.textContent = p.name;
    btn.onclick = () => goPage(p.id);
    navTabs.appendChild(btn);
  });
}

/** 切换到指定画面：id 为 pages 中的 id（不带 "page-" 前缀） */
function goPage(id) {
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach((el, i) => {
    el.classList.toggle('active', pages[i].id === id);
  });
  const target = document.getElementById('page-' + id);
  if (target) target.classList.add('active');
}

/** 每秒更新一次所有画面页头的时钟显示 */
function tick() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const date = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const time = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  const full = `${date} ${time}`;

  CLOCK_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = id === 'clockMain' ? full : time;
  });
}

/* ============================================================
 * 整体自适应缩放：让固定 1280 宽的原型在任意窗口/屏幕尺寸下
 * 都能完整显示，不会出现"界面比屏幕大、看不全"的情况。
 * 做法：measure 出未缩放时的真实宽高，按可视区域算出缩放比例
 * （不超过 1，即只缩小不放大），用 transform:scale 应用到内层容器，
 * 外层容器的尺寸同步设为"缩放后的尺寸"，避免布局上留出多余空白。
 * ============================================================ */
function fitToScreen() {
  const inner = document.getElementById('appScaleInner');
  if (!inner) return;
  const outer = inner.parentElement;

  // 先重置缩放，测量真实（未缩放）尺寸
  inner.style.transform = 'none';
  const naturalWidth = inner.offsetWidth;
  const naturalHeight = inner.offsetHeight;

  const margin = 32; // 留一点呼吸空间，避免贴边
  const availWidth = window.innerWidth - margin;
  const availHeight = window.innerHeight - margin;

  // 只缩小、不放大：屏幕比原型大时保持 1:1 原始像素
  const scale = Math.min(availWidth / naturalWidth, availHeight / naturalHeight, 1);

  inner.style.transform = `scale(${scale})`;
  outer.style.width = `${naturalWidth * scale}px`;
  outer.style.height = `${naturalHeight * scale}px`;
}

let resizeTimer = null;
function onWindowResize() {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(fitToScreen, 100);
}

renderNavTabs();
fitToScreen();
window.addEventListener('resize', onWindowResize);
setInterval(tick, 1000);
tick();
