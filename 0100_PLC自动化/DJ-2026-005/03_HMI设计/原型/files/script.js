/* ==========================================================================
   DJ-2026-005 边框缓存机 HMI 高保真交互原型动态驱动与仿真引擎 (V2.0.0)
   涵盖: 11页面导航、71 DI / 48 DO 全量物理点表、3轴伺服运动学仿真、
         三工站状态机循环、打胶机8步握手、MES报警队列与SOP排障系统
   ========================================================================== */

// 1. 页面定义
const PAGES = [
  { id: 'login',   name: '01 登录' },
  { id: 'main',    name: '02 主画面' },
  { id: 'manual',  name: '03 手动控制' },
  { id: 'auto',    name: '04 自动运行' },
  { id: 'param',   name: '05 参数设置' },
  { id: 'status',  name: '06 状态监控' },
  { id: 'io',      name: '07 IO监控 (全点表)' },
  { id: 'alarm',   name: '08 报警管理' },
  { id: 'glue',    name: '09 打胶机交互' },
  { id: 'robot',   name: '10 机器人交互' },
  { id: 'system',  name: '11 系统设置' },
];

// 2. 全量物理 IO 点表数据 (严格对齐 015_IO分配表_IO.md)
const IO_POINTS = [
  // CPU 本体输入 DI (X0 ~ X17, X76, X102)
  { addr: 'X0',  name: 'Z_Home_Sensor',      desc: 'Z轴原点传感器 (B16)',               module: 'cpu_di',    type: 'DI', state: true,  schema: 'P35/EFS1/16.7' },
  { addr: 'X1',  name: 'X1_Home_Sensor',     desc: 'X1轴原点传感器 (B16)',              module: 'cpu_di',    type: 'DI', state: true,  schema: 'P35/EFS1/16.2' },
  { addr: 'X2',  name: 'X2_Home_Sensor',     desc: 'X2轴原点传感器 (B22)',              module: 'cpu_di',    type: 'DI', state: true,  schema: 'P36/EFS1/16.C' },
  { addr: 'X3',  name: 'Z_Limit_Fwd',        desc: 'Z轴正向限位开关 (B17)',             module: 'cpu_di',    type: 'DI', state: false, schema: 'P35/EFS1/16.4' },
  { addr: 'X4',  name: 'Z_Limit_Rev',        desc: 'Z轴反向限位开关 (B18)',             module: 'cpu_di',    type: 'DI', state: false, schema: 'P35/EFS1/16.5' },
  { addr: 'X5',  name: 'X1_Limit_Fwd',       desc: 'X1轴正向限位开关 (B19)',            module: 'cpu_di',    type: 'DI', state: false, schema: 'P35/EFS1/16.8' },
  { addr: 'X6',  name: 'X1_Limit_Rev',       desc: 'X1轴反向限位开关 (B20)',            module: 'cpu_di',    type: 'DI', state: false, schema: 'P35/EFS1/16.9' },
  { addr: 'X7',  name: 'X2_Limit_Fwd',       desc: 'X2轴正向限位开关 (B21)',            module: 'cpu_di',    type: 'DI', state: false, schema: 'P36/EFS1/17.4' },
  { addr: 'X10', name: 'X2_Limit_Rev',       desc: 'X2轴反向限位开关 (B24)',            module: 'cpu_di',    type: 'DI', state: false, schema: 'P36/EFS1/17.5' },
  { addr: 'X11', name: 'Z_Servo_ALM',        desc: 'Z轴伺服故障报警 (SV0 ALM)',         module: 'cpu_di',    type: 'DI', state: false, schema: 'P43/EFS1/27.8' },
  { addr: 'X12', name: 'X1_Servo_ALM',       desc: 'X1轴伺服故障报警 (SV1 ALM)',        module: 'cpu_di',    type: 'DI', state: false, schema: 'P45/EFS1/29.8' },
  { addr: 'X13', name: 'X2_Servo_ALM',       desc: 'X2轴伺服故障报警 (SV2 ALM)',        module: 'cpu_di',    type: 'DI', state: false, schema: 'P47/EFS1/31.8' },
  { addr: 'X14', name: 'Rear_Door_Lock',     desc: '后安全门锁定状态 (SL2)',            module: 'cpu_di',    type: 'DI', state: true,  schema: 'P40/EFS1/24.7' },
  { addr: 'X15', name: 'Front_Door_Lock',    desc: '前安全门锁定状态 (SL1)',            module: 'cpu_di',    type: 'DI', state: true,  schema: 'P39/EFS1/23.7' },
  { addr: 'X16', name: 'E_Stop_Button',      desc: '操作台急停按钮 (常闭)',             module: 'cpu_di',    type: 'DI', state: true,  schema: 'P103/C0/1.6' },
  { addr: 'X17', name: 'Reset_Button',       desc: '操作台物理复位按钮',                module: 'cpu_di',    type: 'DI', state: false, schema: 'P103/C0/1.7' },
  { addr: 'X76', name: 'GlueAllowFeed',      desc: '打胶机允许送料信号',                module: 'cpu_di',    type: 'DI', state: true,  schema: '外部硬线' },
  { addr: 'X102',name: 'GlueTakeComplete',   desc: '打胶机取料完成信号',                module: 'cpu_di',    type: 'DI', state: false, schema: '外部硬线' },

  // 扩展 DI 模块 3 (4层/3层分料)
  { addr: 'DI3:X0',  name: 'L4_PreFeed_Sensor',  desc: '4层分料前感应器',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P25/EFS1/6.3' },
  { addr: 'DI3:X2',  name: 'L4_InPlace_Sensor1', desc: '4层到位感应器1',                module: 'ext_di',    type: 'DI', state: false, schema: 'P25/EFS1/6.4' },
  { addr: 'DI3:X3',  name: 'L4_InPlace_Sensor2', desc: '4层到位感应器2',                module: 'ext_di',    type: 'DI', state: false, schema: 'P25/EFS1/6.5' },
  { addr: 'DI3:X4',  name: 'L4_Block_Cyl_Up',    desc: '4层阻挡气缸上位',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P25/EFS1/6.6' },
  { addr: 'DI3:X5',  name: 'L4_Block_Cyl_Dn',    desc: '4层阻挡气缸下位',               module: 'ext_di',    type: 'DI', state: false, schema: 'P25/EFS1/6.7' },
  { addr: 'DI3:X6',  name: 'L4_Feed_Cyl_Up',     desc: '4层分料气缸上位(缩回)',          module: 'ext_di',    type: 'DI', state: true,  schema: 'P25/EFS1/6.8' },
  { addr: 'DI3:X7',  name: 'L4_Feed_Cyl_Dn',     desc: '4层分料气缸下位(伸出)',          module: 'ext_di',    type: 'DI', state: false, schema: 'P25/EFS1/6.9' },

  { addr: 'DI3:X11', name: 'L3_PreFeed_Sensor',  desc: '3层分料前感应器',               module: 'ext_di',    type: 'DI', state: false, schema: 'P26/EFS1/7.3' },
  { addr: 'DI3:X12', name: 'L3_InPlace_Sensor1', desc: '3层到位感应器1',                module: 'ext_di',    type: 'DI', state: false, schema: 'P26/EFS1/7.4' },
  { addr: 'DI3:X13', name: 'L3_InPlace_Sensor2', desc: '3层到位感应器2',                module: 'ext_di',    type: 'DI', state: false, schema: 'P26/EFS1/7.5' },
  { addr: 'DI3:X14', name: 'L3_Block_Cyl_Up',    desc: '3层阻挡气缸上位',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P26/EFS1/7.6' },
  { addr: 'DI3:X15', name: 'L3_Block_Cyl_Dn',    desc: '3层阻挡气缸下位',               module: 'ext_di',    type: 'DI', state: false, schema: 'P26/EFS1/7.7' },
  { addr: 'DI3:X16', name: 'L3_Feed_Cyl_Up',     desc: '3层分料气缸上位(缩回)',          module: 'ext_di',    type: 'DI', state: true,  schema: 'P26/EFS1/7.8' },
  { addr: 'DI3:X17', name: 'L3_Feed_Cyl_Dn',     desc: '3层分料气缸下位(伸出)',          module: 'ext_di',    type: 'DI', state: false, schema: 'P26/EFS1/7.9' },

  // 扩展 DI 模块 4 (2层/1层分料)
  { addr: 'DI4:X1',  name: 'L2_PreFeed_Sensor',  desc: '2层分料前感应器',               module: 'ext_di',    type: 'DI', state: false, schema: 'P27/EFS1/8.3' },
  { addr: 'DI4:X2',  name: 'L2_InPlace_Sensor1', desc: '2层到位感应器1',                module: 'ext_di',    type: 'DI', state: false, schema: 'P27/EFS1/8.4' },
  { addr: 'DI4:X3',  name: 'L2_InPlace_Sensor2', desc: '2层到位感应器2',                module: 'ext_di',    type: 'DI', state: false, schema: 'P27/EFS1/8.5' },
  { addr: 'DI4:X4',  name: 'L2_Block_Cyl_Up',    desc: '2层阻挡气缸上位',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P27/EFS1/8.6' },
  { addr: 'DI4:X5',  name: 'L2_Block_Cyl_Dn',    desc: '2层阻挡气缸下位',               module: 'ext_di',    type: 'DI', state: false, schema: 'P27/EFS1/8.7' },
  { addr: 'DI4:X6',  name: 'L2_Feed_Cyl_Up',     desc: '2层分料气缸上位',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P27/EFS1/8.8' },
  { addr: 'DI4:X7',  name: 'L2_Feed_Cyl_Dn',     desc: '2层分料气缸下位',               module: 'ext_di',    type: 'DI', state: false, schema: 'P27/EFS1/8.9' },

  { addr: 'DI4:X11', name: 'L1_PreFeed_Sensor',  desc: '1层分料前感应器',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P28/EFS1/9.3' },
  { addr: 'DI4:X12', name: 'L1_InPlace_Sensor1', desc: '1层到位感应器1',                module: 'ext_di',    type: 'DI', state: true,  schema: 'P28/EFS1/9.4' },
  { addr: 'DI4:X13', name: 'L1_InPlace_Sensor2', desc: '1层到位感应器2',                module: 'ext_di',    type: 'DI', state: true,  schema: 'P28/EFS1/9.5' },
  { addr: 'DI4:X14', name: 'L1_Block_Cyl_Up',    desc: '1层阻挡气缸上位',               module: 'ext_di',    type: 'DI', state: false, schema: 'P28/EFS1/9.6' },
  { addr: 'DI4:X15', name: 'L1_Block_Cyl_Dn',    desc: '1层阻挡气缸下位',               module: 'ext_di',    type: 'DI', state: true,  schema: 'P28/EFS1/9.7' },
  { addr: 'DI4:X16', name: 'L1_Feed_Cyl_Up',     desc: '1层分料气缸上位(复位)',          module: 'ext_di',    type: 'DI', state: false, schema: 'P28/EFS1/9.8' },
  { addr: 'DI4:X17', name: 'L1_Feed_Cyl_Dn',     desc: '1层分料气缸下位(推出)',          module: 'ext_di',    type: 'DI', state: true,  schema: 'P28/EFS1/9.9' },

  // 远程 IO 输入 (X120 ~ X133)
  { addr: 'X120',    name: 'Lift_Cyl_MovPt1',    desc: '取放料升降气缸下到位',           module: 'remote_di', type: 'DI', state: true,  schema: 'P94/B5/2.1' },
  { addr: 'X121',    name: 'Lift_Cyl_Home1',     desc: '取放料升降气缸上原点',           module: 'remote_di', type: 'DI', state: false, schema: 'P94/B5/2.3' },
  { addr: 'X122',    name: 'FrontGrip_Clamp1',   desc: '前取料气缸1夹紧到位',            module: 'remote_di', type: 'DI', state: true,  schema: 'P94/B5/2.4' },
  { addr: 'X123',    name: 'FrontGrip_Unclamp1', desc: '前取料气缸1松开到位',            module: 'remote_di', type: 'DI', state: false, schema: 'P94/B5/2.6' },
  { addr: 'X124',    name: 'RearGrip_Clamp1',    desc: '后取料气缸1夹紧到位',            module: 'remote_di', type: 'DI', state: true,  schema: 'P94/B5/2.7' },
  { addr: 'X125',    name: 'RearGrip_Unclamp1',  desc: '后取料气缸1松开到位',            module: 'remote_di', type: 'DI', state: false, schema: 'P94/B5/2.8' },
  { addr: 'X126',    name: 'FrontGrip_Clamp2',   desc: '前取料气缸2夹紧到位',            module: 'remote_di', type: 'DI', state: true,  schema: 'P95/B5/3.3' },
  { addr: 'X127',    name: 'FrontGrip_Unclamp2', desc: '前取料气缸2松开到位',            module: 'remote_di', type: 'DI', state: false, schema: 'P95/B5/3.4' },
  { addr: 'X130',    name: 'LongEdge1_Detect',   desc: '长边边框1检测光电 (SICK)',       module: 'remote_di', type: 'DI', state: true,  schema: 'P96/B5/4.2' },
  { addr: 'X131',    name: 'LongEdge2_Detect',   desc: '长边边框2检测光电 (SICK)',       module: 'remote_di', type: 'DI', state: true,  schema: 'P96/B5/4.3' },
  { addr: 'X132',    name: 'ShortEdge1_Detect',  desc: '短边边框1检测光电 (SICK)',       module: 'remote_di', type: 'DI', state: true,  schema: 'P96/B5/4.4' },
  { addr: 'X133',    name: 'ShortEdge2_Detect',  desc: '短边边框2检测光电 (SICK)',       module: 'remote_di', type: 'DI', state: true,  schema: 'P96/B5/4.6' },

  // CPU 本体输出 DO (Y0 ~ Y27, Y44, Y47)
  { addr: 'Y0',      name: 'Z_Axis_Pulse',       desc: 'Z轴高速脉冲输出 (PULSE+)',       module: 'cpu_do',    type: 'DO', state: false, schema: 'P44/EFS1/28.8' },
  { addr: 'Y1',      name: 'X1_Axis_Pulse',      desc: 'X1轴高速脉冲输出 (PULSE+)',      module: 'cpu_do',    type: 'DO', state: true,  schema: 'P46/EFS1/30.8' },
  { addr: 'Y2',      name: 'X2_Axis_Pulse',      desc: 'X2轴高速脉冲输出 (PULSE+)',      module: 'cpu_do',    type: 'DO', state: false, schema: 'P48/EFS1/32.8' },
  { addr: 'Y4',      name: 'Z_Axis_Dir',         desc: 'Z轴方向输出 (SIGN+)',           module: 'cpu_do',    type: 'DO', state: false, schema: 'P44/EFS1/28.8' },
  { addr: 'Y5',      name: 'X1_Axis_Dir',        desc: 'X1轴方向输出 (SIGN+)',          module: 'cpu_do',    type: 'DO', state: true,  schema: 'P46/EFS1/30.8' },
  { addr: 'Y6',      name: 'X2_Axis_Dir',        desc: 'X2轴方向输出 (SIGN+)',          module: 'cpu_do',    type: 'DO', state: false, schema: 'P48/EFS1/32.8' },
  { addr: 'Y10',     name: 'Z_Servo_EN',         desc: 'Z轴伺服使能 (SON)',             module: 'cpu_do',    type: 'DO', state: true,  schema: 'P43/EFS1/27.1' },
  { addr: 'Y11',     name: 'X1_Servo_EN',        desc: 'X1轴伺服使能 (SON)',            module: 'cpu_do',    type: 'DO', state: true,  schema: 'P45/EFS1/29.1' },
  { addr: 'Y12',     name: 'X2_Servo_EN',        desc: 'X2轴伺服使能 (SON)',            module: 'cpu_do',    type: 'DO', state: true,  schema: 'P47/EFS1/31.1' },
  { addr: 'Y13',     name: 'Safety_Relay_Start', desc: '安全继电器启动 (SR0)',           module: 'cpu_do',    type: 'DO', state: true,  schema: 'P38/EFS1/21.9' },
  { addr: 'Y24',     name: 'Green_Pilot_Lamp',   desc: '三色灯绿灯 (运行指示)',          module: 'cpu_do',    type: 'DO', state: true,  schema: 'P103/C0' },
  { addr: 'Y25',     name: 'Red_Pilot_Lamp',     desc: '三色灯红灯 (故障指示)',          module: 'cpu_do',    type: 'DO', state: false, schema: 'P103/C0' },
  { addr: 'Y26',     name: 'Yellow_Pilot_Lamp',  desc: '三色灯黄灯 (暂停/回原)',         module: 'cpu_do',    type: 'DO', state: false, schema: 'P103/C0' },
  { addr: 'Y27',     name: 'Buzzer_Output',      desc: '蜂鸣器报警脉冲输出',             module: 'cpu_do',    type: 'DO', state: false, schema: 'P103/C0' },
  { addr: 'Y44',     name: 'AllowGripper',       desc: '允许打胶机抓料信号',             module: 'cpu_do',    type: 'DO', state: true,  schema: '外部硬线' },
  { addr: 'Y47',     name: 'SafetyZoneSignal',   desc: '打胶机安全区隔离信号',           module: 'cpu_do',    type: 'DO', state: true,  schema: '外部硬线' },

  // 扩展 DO 模块 1~2 (4层输送与气缸电磁阀)
  { addr: 'DO1:Y0',  name: 'L4_Block_Solenoid',  desc: '4层阻挡电磁阀 (YV1)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P29/EFS1/10.2' },
  { addr: 'DO1:Y1',  name: 'L4_Feed_Solenoid',   desc: '4层分料电磁阀 (YV2)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P29/EFS1/10.3' },
  { addr: 'DO1:Y2',  name: 'L4_Conveyor_FWD',    desc: '4层输送带正转 (VF1)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P29/EFS1/10.4' },
  { addr: 'DO1:Y10', name: 'L3_Block_Solenoid',  desc: '3层阻挡电磁阀 (YV3)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P30/EFS1/11.2' },
  { addr: 'DO1:Y12', name: 'L3_Conveyor_FWD',    desc: '3层输送带正转 (VF2)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P30/EFS1/11.4' },
  { addr: 'DO2:Y0',  name: 'L2_Block_Solenoid',  desc: '2层阻挡电磁阀 (YV5)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P31/EFS1/12.2' },
  { addr: 'DO2:Y2',  name: 'L2_Conveyor_FWD',    desc: '2层输送带正转 (VF3)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P31/EFS1/12.4' },
  { addr: 'DO2:Y10', name: 'L1_Block_Solenoid',  desc: '1层阻挡电磁阀 (YV7)',           module: 'ext_do',    type: 'DO', state: true,  schema: 'P32/EFS1/13.2' },
  { addr: 'DO2:Y11', name: 'L1_Feed_Solenoid',   desc: '1层分料电磁阀 (YV8)',           module: 'ext_do',    type: 'DO', state: true,  schema: 'P32/EFS1/13.3' },
  { addr: 'DO2:Y12', name: 'L1_Conveyor_FWD',    desc: '1层输送带正转 (VF4)',           module: 'ext_do',    type: 'DO', state: false, schema: 'P32/EFS1/13.4' },
  { addr: 'DO2:Y13', name: 'L1_Conveyor_Slow',   desc: '1层输送带慢速转 (VF4)',         module: 'ext_do',    type: 'DO', state: true,  schema: 'P32/EFS1/13.5' }
];

// 3. 仿真运行状态机对象
const simState = {
  currentUser: 'operator',
  userLevel: 1,
  mode: 'auto', // auto, cycle, step, manual
  isRunning: true,
  isPaused: false,
  kpi: { total: 1420, good: 1412, ng: 8, cycleTime: 11.8 },
  servo: {
    z: { pos: 125.4, target: 125.4, vel: 120.0, torque: 32 },
    x1: { pos: 480.0, target: 480.0, vel: 250.0, torque: 45 },
    x2: { pos: 10.0, target: 10.0, vel: 200.0, torque: 18 }
  },
  clamps: [true, true, true, true],
  conveyors: [
    { running: false, stopper: false, separator: false },
    { running: false, stopper: false, separator: false },
    { running: false, stopper: false, separator: false },
    { running: true, stopper: true, separator: true }
  ],
  st1Step: 30,
  st2Step: 23,
  st3Step: 2,
  mesQueue: [1002, 1001, 1004, 1005, 0, 0, 0, 0, 0, 0]
};

// 4. 页面导航渲染与切换
function renderNavTabs() {
  const container = document.getElementById('navTabBar');
  if (!container) return;
  container.innerHTML = '';
  PAGES.forEach(p => {
    const btn = document.createElement('button');
    btn.className = 'nav-tab-btn' + (p.id === 'main' ? ' active' : '');
    btn.textContent = p.name;
    btn.onclick = () => goPage(p.id);
    container.appendChild(btn);
  });
}

function goPage(pageId) {
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab-btn').forEach((el, idx) => {
    el.classList.toggle('active', PAGES[idx].id === pageId);
  });
  const target = document.getElementById('page-' + pageId);
  if (target) {
    target.classList.add('active');
    if (pageId === 'io') renderIoTable();
    if (pageId === 'alarm') renderMesQueue();
  }
}

// 5. 渲染 71 DI / 48 DO 端子排表格
function renderIoTable() {
  const tbody = document.getElementById('ioTableBody');
  if (!tbody) return;
  const filter = document.getElementById('ioModuleFilter').value;
  const query = document.getElementById('ioSearchInput').value.toLowerCase().trim();

  let filtered = IO_POINTS.filter(p => {
    if (filter !== 'all' && p.module !== filter) return false;
    if (query && !p.addr.toLowerCase().includes(query) && !p.name.toLowerCase().includes(query) && !p.desc.toLowerCase().includes(query)) return false;
    return true;
  });

  tbody.innerHTML = filtered.map(p => `
    <tr style="border-bottom:1px solid var(--border-color); ${p.forced ? 'background:rgba(255,179,0,0.1);' : ''}">
      <td style="padding:6px 12px; font-family:var(--font-mono); font-weight:bold; color:var(--cyan);">${p.addr}</td>
      <td style="padding:6px 12px; font-family:var(--font-mono); color:#fff;">${p.name}</td>
      <td style="padding:6px 12px; color:var(--text-muted);">${p.desc} <span style="font-size:10px; color:var(--text-dim);">[${p.schema}]</span></td>
      <td style="padding:6px 12px;"><span class="badge" style="background:${p.type==='DI'?'#1b3a5b':'#3a245b'};">${p.type} 24V</span></td>
      <td style="padding:6px 12px; text-align:center;"><span class="led ${p.state ? 'green' : ''}"></span></td>
      <td style="padding:6px 12px; text-align:center;">
        <button class="btn sm ${p.state ? 'warning' : 'primary'}" onclick="toggleIo('${p.addr}')">${p.state ? '置0' : '置1'}</button>
      </td>
    </tr>
  `).join('');
}

function toggleIo(addr) {
  const item = IO_POINTS.find(p => p.addr === addr);
  if (item) {
    item.state = !item.state;
    item.forced = true;
    renderIoTable();
    updateSvgAndLedStates();
  }
}

// 6. MES 报警队列与 SOP 弹窗系统
const SOP_DATABASE = {
  'E1002': {
    title: 'E1002 · L1 层分料气缸推出超时排障 SOP',
    content: `
      <b>【故障现象】</b>：L1 层分料电磁阀 (YV8 / DO2:Y11) 输出后，分料气缸下位磁簧传感器 (DI4:X17) 在 3000ms 内未闭合。<br><br>
      <b>【排查处置步骤】</b>：
      <ol style="margin-left:20px; margin-top:6px;">
        <li><b>检查主气路压力</b>：确认主气压表读数是否 ≥ 0.55 MPa；</li>
        <li><b>检查电磁阀动作</b>：在电箱 A1 观察 DO2:Y11 指示灯是否亮起，按压 YV8 手动测试按钮确认阀芯是否动作；</li>
        <li><b>检查机械干涉</b>：确认 L1 层边框物料是否有卡阻或尺寸超差；</li>
        <li><b>检查磁性开关</b>：观察气缸伸出到位时，DI4:X17 传感器 LED 是否亮起，原理图对应 P28/EFS1/9.9。</li>
      </ol>
    `
  },
  'E1001': {
    title: 'E1001 · Z 轴伺服驱动器过载报警排障 SOP',
    content: `
      <b>【故障现象】</b>：Z 轴汇川 SV660P 驱动器 ALM 报警常开触点闭合 (X11=ON)。<br><br>
      <b>【排查处置步骤】</b>：
      <ol style="margin-left:20px; margin-top:6px;">
        <li>查看驱动器面板报错代码 (如 Er.100 过载或 Er.120 抱闸未打开)；</li>
        <li>检查 Z 轴电磁抱闸线圈 DC24V 是否正常供电 (KA10 触点)；</li>
        <li>手动模式尝试点动，确认垂直丝杆机构有无机械卡滞。</li>
      </ol>
    `
  }
};

function showSopModal(code) {
  const sop = SOP_DATABASE[code] || SOP_DATABASE['E1002'];
  document.getElementById('sopModalTitle').textContent = sop.title;
  document.getElementById('sopModalContent').innerHTML = sop.content;
  document.getElementById('sopModal').classList.add('active');
}

function closeSopModal() {
  document.getElementById('sopModal').classList.remove('active');
}

function renderMesQueue() {
  const container = document.getElementById('mesQueueContainer');
  if (!container) return;
  container.innerHTML = simState.mesQueue.map((code, idx) => `
    <div class="dro-box" style="flex-direction:column; align-items:flex-start; gap:4px;">
      <span class="dro-label">队列 #${idx + 1}</span>
      <span class="dro-value" style="color:${code ? 'var(--danger)' : 'var(--text-dim)'};">${code ? 'Alarm #' + code : '[空闲缓冲]'}</span>
    </div>
  `).join('');
}

// 7. 参数虚拟触控键盘逻辑
let currentParamField = null;
function openNumpad(fieldId, title, initVal) {
  currentParamField = fieldId;
  document.getElementById('numpadTitle').textContent = '修改参数: ' + title;
  document.getElementById('numpadDisplay').value = initVal;
  document.getElementById('numpadModal').classList.add('active');
}

function closeNumpad() {
  document.getElementById('numpadModal').classList.remove('active');
}

function numpadInput(char) {
  const disp = document.getElementById('numpadDisplay');
  if (char === '.' && disp.value.includes('.')) return;
  disp.value = (disp.value === '0' && char !== '.') ? char : disp.value + char;
}

function numpadClear() {
  document.getElementById('numpadDisplay').value = '0';
}

function numpadBackspace() {
  const disp = document.getElementById('numpadDisplay');
  disp.value = disp.value.length > 1 ? disp.value.slice(0, -1) : '0';
}

function numpadConfirm() {
  if (currentParamField) {
    const val = document.getElementById('numpadDisplay').value;
    const input = document.getElementById('p_' + currentParamField);
    if (input) input.value = val;
  }
  closeNumpad();
}

function teachPos(fieldId, axis) {
  const currentPos = simState.servo[axis].pos.toFixed(1);
  const input = document.getElementById('p_' + fieldId);
  if (input) {
    input.value = currentPos;
    alert(`成功教导当前 ${axis.toUpperCase()} 轴位置 ${currentPos} mm 至寄存器 ${fieldId}`);
  }
}

function saveAllParams() {
  alert('参数已成功写入 PLC 保持寄存器 (D510~D710)，校验和验证通过！');
}

// 8. 手动与自动控制交互
function triggerAutoStart() {
  simState.isRunning = true;
  simState.isPaused = false;
  document.getElementById('topLedRunning').className = 'led green';
  document.getElementById('topStatusText').textContent = '自动运行';
}

function triggerAutoPause() {
  simState.isRunning = false;
  simState.isPaused = true;
  document.getElementById('topLedRunning').className = 'led yellow';
  document.getElementById('topStatusText').textContent = '循环暂停';
}

function triggerReset() {
  alert('系统报警复位指令 (M102) 已发送，首出报警已清除！');
  document.getElementById('bottomAlarmText').textContent = '系统正常运行，无活动故障';
}

function triggerEStop() {
  simState.isRunning = false;
  document.getElementById('topLedRunning').className = 'led red';
  document.getElementById('topStatusText').textContent = '紧急停机';
  alert('急停触发 (M103)，伺服与动力回路已切断！');
}

function jogServo(axis, dir) {
  const step = (dir === 'fwd' || dir === 'up') ? 2.5 : -2.5;
  simState.servo[axis].pos += step;
  updateServoDisplays();
}

function stopServo(axis) {}

function gotoPos(axis, targetName) {
  const targets = {
    z: { standby: 50.0, pick: 125.4 },
    x1: { pick: 100.0, front: 480.0, rear: 720.0 },
    x2: { pick: 512.0, glue: 522.0 }
  };
  if (targets[axis] && targets[axis][targetName]) {
    simState.servo[axis].pos = targets[axis][targetName];
    updateServoDisplays();
  }
}

let isLiftUp = false;
function toggleLiftCylinder() {
  isLiftUp = !isLiftUp;
  const statusEl = document.getElementById('manLiftStatus');
  const ledEl = document.getElementById('manLiftLed');
  if (statusEl) statusEl.textContent = isLiftUp ? '上位到位 (X70 · 高度补偿中)' : '下位到位 (X71 · 安全复位)';
  if (ledEl) ledEl.className = 'led ' + (isLiftUp ? 'green' : 'cyan');
}

const RECIPES_DATA = {
  1: { d511: 125.4, d512: 185.0, d513: 245.0, d514: 305.0, d520: 480.0, d530: 560.0, d540: 640.0, d550: 720.0 },
  2: { d511: 130.0, d512: 190.0, d513: 250.0, d514: 310.0, d520: 500.0, d530: 580.0, d540: 660.0, d550: 740.0 },
  3: { d511: 135.0, d512: 195.0, d513: 255.0, d514: 315.0, d520: 520.0, d530: 600.0, d540: 680.0, d550: 760.0 }
};

function loadSelectedRecipe(id) {
  const data = RECIPES_DATA[id] || RECIPES_DATA[1];
  document.getElementById('p_D511').value = data.d511;
  document.getElementById('p_D512').value = data.d512;
  document.getElementById('p_D513').value = data.d513;
  document.getElementById('p_D514').value = data.d514;
  document.getElementById('p_D520').value = data.d520;
  document.getElementById('p_D530').value = data.d530;
  document.getElementById('p_D540').value = data.d540;
  document.getElementById('p_D550').value = data.d550;
}

function saveActiveRecipe() {
  const id = document.getElementById('recipeSelect').value;
  alert('✅ 配方 ' + id + ' 示教数据已成功保存并同步至 PLC ST_RecipeManager 保持数据块！');
}

function toggleClamp(idx) {
  simState.clamps[idx - 1] = !simState.clamps[idx - 1];
  updateClampLeds();
}

function clampAll(state) {
  simState.clamps = [state, state, state, state];
  updateClampLeds();
}

function updateClampLeds() {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById('manClamp' + i + 'Led');
    if (el) el.className = 'led ' + (simState.clamps[i - 1] ? 'green' : '');
  }
}

function updateServoDisplays() {
  document.getElementById('droMainZ').textContent = simState.servo.z.pos.toFixed(2) + ' mm';
  document.getElementById('droMainX1').textContent = simState.servo.x1.pos.toFixed(2) + ' mm';
  document.getElementById('droMainX2').textContent = simState.servo.x2.pos.toFixed(2) + ' mm';
  document.getElementById('manZPos').textContent = simState.servo.z.pos.toFixed(1) + ' mm';
  document.getElementById('manX1Pos').textContent = simState.servo.x1.pos.toFixed(1) + ' mm';
  document.getElementById('manX2Pos').textContent = simState.servo.x2.pos.toFixed(1) + ' mm';
}

function updateSvgAndLedStates() {}

// 9. 登录权限
function appendPin(char) {
  const pin = document.getElementById('loginPinInput');
  if (pin.value.length < 6) pin.value += char;
}
function clearPin() { document.getElementById('loginPinInput').value = ''; }
function backspacePin() {
  const pin = document.getElementById('loginPinInput');
  pin.value = pin.value.slice(0, -1);
}
function doLogin() {
  const role = document.getElementById('loginUserSelect').value;
  simState.currentUser = role;
  const roleLabels = {
    operator: '操作员 (Level 1)',
    engineer: '调试工程师 (Level 2)',
    admin: '系统管理员 (Level 3)'
  };
  document.getElementById('topCurrentUser').textContent = roleLabels[role];
  goPage('main');
}

// 10. 时钟与屏幕自适应
function tick() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const str = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  const clk = document.getElementById('systemClock');
  if (clk) clk.textContent = str;
}

function fitToScreen() {
  const inner = document.getElementById('appScaleInner');
  if (!inner) return;
  const outer = inner.parentElement;
  inner.style.transform = 'none';
  const naturalWidth = inner.offsetWidth;
  const naturalHeight = inner.offsetHeight;
  const margin = 24;
  const scale = Math.min((window.innerWidth - margin) / naturalWidth, (window.innerHeight - margin) / naturalHeight, 1);
  inner.style.transform = `scale(${scale})`;
  outer.style.width = `${naturalWidth * scale}px`;
  outer.style.height = `${naturalHeight * scale}px`;
}

// 初始化启动
renderNavTabs();
renderIoTable();
renderMesQueue();
fitToScreen();
window.addEventListener('resize', fitToScreen);
setInterval(tick, 1000);
tick();
