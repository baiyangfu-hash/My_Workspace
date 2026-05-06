# Dynamic Siemens LSP 插件适配修订计划

## 一、目标

按照 **Dynamic Siemens Language Support (v2.5.0)** 插件的格式要求，修订DJ-2026-005项目的PLC程序文件，使其能够正确激活LSP语言服务器，实现"转到定义"、智能提示、悬停信息、诊断检查等完整功能。

---

## 二、当前问题诊断

### 2.1 文件扩展名混乱 ⚠️ 严重

| 扩展名 | 数量 | 示例 |
|--------|------|------|
| `.st` | 16个 | FB_xxx.st, PRG_xxx.st |
| `.scl` | 1个 | PRG_HMI_Interface_V4.2.0.scl |

**问题**：Dynamic Siemens LSP 同时支持 `.scl` 和 `.st`，但混合使用可能导致索引不一致。

### 2.2 中文变量名 ⚠️ 可能导致LSP解析失败

当前项目中大量使用中文+英文混合变量名：

```
(* 输入变量示例 *)
i_b使能               : BOOL;
i_b自动模式           : BOOL;
i_b手动模式           : BOOL;
i_b阻挡下降           : ARRAY[1..4] OF BOOL;
i_b分料前感应器         : ARRAY[1..4] OF BOOL;

(* 输出变量示例 *)
o_b阻挡电磁阀           : ARRAY[1..4] OF BOOL;
o_b放料完成            : ARRAY[1..4] OF BOOL;

(* 结构体字段 *)
bEmergencyStopButton   : BOOL;    (* 英文 *)
bGlueMachine_AllowFeed : BOOL;    (* 英文 *)
```

**风险**：Go语言实现的LSP后端对Unicode/中文字符的支持程度未知，可能导致符号表建立失败。

### 2.3 缺少 .plc.json 配置文件 ❌ 必须修复

Dynamic Siemens LSP **必须**检测到 `.plc.json` 文件才会激活语言服务器。

> 官方文档："Place a `.plc.json` file in each PLC project folder to give it an isolated type scope."

### 2.4 #region 标记非标准 ℹ️ 低风险

使用了C#风格的折叠标记：
```st
//#region 100_VAR_INPUT
//#endregion 100_VAR_INPUT
```

这不是IEC 61131-3标准语法，但TextMate语法高亮通常忽略未知标记，不影响LSP解析。

---

## 三、修订方案

### 方案原则

1. **最小化变更**：只修改影响LSP工作的必要内容，不改变业务逻辑
2. **向后兼容**：确保PLC编译不受影响
3. **渐进式**：先创建配置文件测试基础功能，再考虑其他调整

---

## 四、执行步骤

### Step 1: 创建 .plc.json 配置文件 ✅ 必须

**位置**: `02_PLC程序\通用ST程序及变量表\.plc.json`

```json
{
    "name": "DJ-2026-005_边框缓存机",
    "description": "边框缓存机PLC主控程序 - 四层输送机/取放料机构/打胶机送料",
    "libraries": []
}
```

**作用**：告诉Dynamic Siemens LSP这是一个PLC项目根目录，该目录及其所有子目录中的`.st`/`.scl`文件都会被索引。

---

### Step 2: 统一文件扩展名 ✅ 推荐

将所有文件统一为 `.scl` 扩展名（Siemens SCL标准）：

#### 四层输送机目录（2个文件）

| 序号 | 当前文件名 | 目标文件名 |
|------|-----------|-----------|
| 01 | `FB_1001_Conveyor4Layer_BufferFraming.st` | `FB_1001_Conveyor4Layer_BufferFraming.scl` |
| 02 | `FB_1002_SingleLayerConveyor_BufferFraming_V4.1.0.st` | `FB_1002_SingleLayerConveyor_BufferFraming_V4.1.0.scl` |

#### 主控目录（10个文件）

| 序号 | 当前文件名 | 目标文件名 |
|------|-----------|-----------|
| 03 | `PRG_MainControl_DJ2026005_V4.2.0.st` | `PRG_MainControl_DJ2026005_V4.2.0.scl` |
| 04 | `PRG_IO_Mapping_V4.2.0.st` | `PRG_IO_Mapping_V4.2.0.scl` |
| 05 | `PRG_IO_InputMapping_V4.2.0.st` | `PRG_IO_InputMapping_V4.2.0.scl` |
| 06 | `PRG_IO_OutputMapping_V4.2.0.st` | `PRG_IO_OutputMapping_V4.2.0.scl` |
| 07 | `PRG_IO_OutputMapping_V4.2.1.st` | `PRG_IO_OutputMapping_V4.2.1.scl` |
| 08 | `PRG_StationCoordinator_V4.2.1.st` | `PRG_StationCoordinator_V4.2.1.scl` |
| 09 | `PRG_HMI_InputInterface_V4.2.0.st` | `PRG_HMI_InputInterface_V4.2.0.scl` |
| 10 | `PRG_HMI_OutputInterface_V4.2.0.st` | `PRG_HMI_OutputInterface_V4.2.0.scl` |
| 11 | `GVL_HMI_Variables_V4.2.0.st` | `GVL_HMI_Variables_V4.2.0.scl` |
| 12 | `TypeDefinitions_V4.2.1.st` | `TypeDefinitions_V4.2.1.scl` |
| 13 | `PRG_HMI_Interface_V4.2.0.scl` | 保持不变（已是.scl） |

#### 其他工站目录（5个文件）

| 序号 | 当前文件名 | 目标文件名 |
|------|-----------|-----------|
| 14 | `取放料机构\FB_1003_PickPlace_BufferFraming_V4.1.0.st` | `...V4.1.0.scl` |
| 15 | `打胶机送料机构\FB_1004_GlueMachineFeeder_BufferFraming_V4.1.0.st` | `...V4.1.0.scl` |
| 16 | `外部设备交互\FB_外部设备交互_V4.1.0.st` | `...V4.1.0.scl` |
| 17 | `公共服务\FB_公共报警_V4.0.0.st` | `...V4.0.0.scl` |
| 18 | `公共服务\FB_2001_CommonAlarm_AllStation_V4.1.0.st` | `...V4.1.0.scl` |

**总计**：17个文件需要重命名（.st → .scl）

---

### Step 3: 测试验证 ✅ 必须

完成Step 1和Step 2后，执行以下测试：

1. **重启VS Code**
2. **打开输出面板** → 选择 "Siemens Language Server"
3. **确认LSP启动日志**：
   ```
   [INFO] PLC scope detected: DJ-2026-005_边框缓存机
   [INFO] Indexing files... (18 files)
   [INFO] Ready
   ```
4. **打开 `PRG_MainControl_DJ2026005_V4.2.0.scl`**
5. **测试转到定义（F12）**：
   - 光标放在 `fbConveyor4Layer` 上 → 按F12 → 应跳转到 `FB_1001_Conveyor4Layer_BufferFraming.scl`
   - 光标放在 `fbPickPlace` 上 → 按F12 → 应跳转到 `FB_1003_PickPlace_BufferFraming_V4.1.0.scl`
   - 光标放在 `ST_IO_InputData` 上 → 按F12 → 应跳转到 `TypeDefinitions_V4.2.1.scl`
6. **测试智能提示（Ctrl+Space）**
7. **测试悬停信息（鼠标悬停在类型上）**

---

## 五、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| 中文变量名导致LSP解析失败 | 中 | 高 | 先测试，如果失败再考虑英文化 |
| .scl扩展名导致PLC IDE不识别 | 低 | 中 | PLC IDE按内容编译，不看扩展名 |
| #region标记导致语法错误 | 极低 | 无 | LSP会忽略无法解析的pragma |
| LSP索引超时（18个文件较大） | 低 | 低 | 等待索引完成即可 |

---

## 六、后续优化（可选）

如果基础功能正常工作，可考虑进一步优化：

1. **变量名英文化**：将中文变量名改为纯英文（工作量巨大，需评估）
2. **移除#region标记**：改用标准的 `(* --- Section --- *)` 分隔符
3. **添加更多.plc.json配置**：如libraries路径、描述等

---

## 七、预期结果

完成后应实现：

```
✅ VS Code状态栏显示 "Siemens Language Server: Ready"
✅ F12 转到定义 正常工作
✅ Ctrl+Space 智能提示 正常工作
✅ 鼠标悬停显示类型信息
✅ 问题面板显示实时诊断错误/警告
✅ Ctrl+Shift+F 全局搜索符号引用
```
