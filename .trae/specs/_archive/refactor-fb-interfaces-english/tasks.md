# Tasks - FB接口变量名英文化重构

## 任务概览
- **任务1**: 重写 FB_ExternalDeviceInteraction 接口 + 内部代码 (V4.1.0 → V5.0.0)
- **任务2**: 重写 FB_1003_PickPlace 接口 + 内部代码 (V4.2.0 → V5.0.0)
- **任务3**: 集成验证 + 文档更新

---

## Task 1: 重写 FB_ExternalDeviceInteraction (V4.1.0 → V5.0.0)

- [ ] 1.1 更新文件头版本信息为 V5.0.0，添加变更记录条目
- [ ] 1.2 替换 VAR_INPUT 区域的27个中文变量名为英文（按spec.md映射表）
- [ ] 1.3 替换 VAR_OUTPUT 区域的20个中文变量名为英文（按spec.md映射表）
- [ ] 1.4 替换内部实现代码中所有引用旧变量名的地方（约50+处）
- [ ] 1.5 替换内部VAR区域的变量名（如 `i外部设备报警码` → `iExternalDeviceAlarmCode`）
- [ ] 1.6 验证：Grep搜索确认无残留中文变量名

**影响文件**: `external/FB_ExternalDeviceInteraction.scl`
**产出文档**: `external/变更记录_CHG-FBExternal-V5.0.0.md`

---

## Task 2: 重写 FB_1003_PickPlace (V4.2.0 → V5.0.0)

- [ ] 2.1 更新文件头版本信息为 V5.0.0，添加变更记录条目
- [ ] 2.2 替换 VAR_INPUT 区域的55个中文变量名为英文（按spec.md映射表）
- [ ] 2.3 替换 VAR_OUTPUT 区域的30个中文变量名为英文（按spec.md映射表）
- [ ] 2.4 替换内部实现代码中所有引用旧变量名的地方（预计100+处）
- [ ] 2.5 替换内部VAR/VAR_CONSTANT区域的变量名
- [ ] 2.6 验证：Grep搜索确认无残留中文变量名

**影响文件**: `pickplace/FB_1003_PickPlace_BufferFraming.scl`
**产出文档**: `pickplace/变更记录_CHG-FB1003-PickPlace-V5.0.0.md`

---

## Task 3: 集成验证与文档更新

- [ ] 3.1 全局一致性验证：确认 OB1.scl 调用参数与两个FB接口100%匹配
- [ ] 3.2 全局Grep验证：确认整个项目无残留中文接口变量名
- [ ] 3.3 创建/更新总变更记录 V5.0.0（追加本次修复内容）

**依赖关系**:
- Task 3 依赖 Task 1 和 Task 2 完成
- Task 1 和 Task 2 可并行执行（互相独立）
