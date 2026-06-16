# 计划：解析欧姆龙 Sysmac Studio .smc2 文件并尝试恢复 FB 块密码

## 摘要

用户有一个欧姆龙 Sysmac Studio 项目文件 `模板_1.smc2`，其中 12 个 FB（功能块）设置了 Know-How 密码保护，用户忘记了密码，希望解析该文件并尝试恢复密码。

## 现状分析

### 文件格式确认
- `.smc2` 本质是 **ZIP 压缩包**，可用 Python `zipfile` 直接解析
- 内部结构：`{GUID目录}/{GUID}.xml`，每个 XML 代表一个项目对象
- 项目名称：`模板_1`，作者：`xrmiracle`，PLC 型号：NX102-1200

### FB 密码保护机制（已确认）
1. **12 个 FB 块设置了密码保护**（PartialProtectPasswordAuthenticationSchemaName）：
   - 双向电磁阀、单向电磁阀、单向真空吸、伺服定位、功能选择电磁阀、双向真空吸
   - Robot_SON、Robot_SPEED、Robot_JOG、Robot_READ、Robot_WRITE
   - 单模组寸动

2. **密码存储方式**：
   - 密码哈希存储在 `.oem` 文件的 `<AuthenticationScheme>` 节点中
   - 11 个 FB 使用同一密码哈希：`52f5c67f46e5c9765ae9c976`（Base64: `NTJmNWM2N2Y0NmU1Yzk3NjVhZTljOTc2`）
   - 1 个 FB（单模组寸动）使用不同密码哈希：`58f4c66352f5c67f`（Base64: `NThmNGM2NjM1MmY1YzY3Zg==`）

3. **源代码加密**：
   - 12 个 XML 文件包含 `<EncryptedFile>` 标签
   - 每个 EncryptedFile 包含：`<EncryptionLock>`（密钥标识）、`<Body>`（加密的源代码，Base64 编码）、`<Checksum>`（校验和）
   - 加密算法疑似 AES 或类似的对称加密，密钥由密码派生

4. **密码破解尝试结果**：
   - 已尝试 MD5/SHA1/SHA256（含截断）+ 常见密码 → 无匹配
   - 已尝试 UTF-16LE/UTF-8 BOM 编码 → 无匹配
   - 哈希长度异常（12 字节 / 8 字节），非标准哈希算法
   - **结论：欧姆龙使用了专有的密码哈希算法，无法通过简单哈希比对破解**

### 可行方案评估

| 方案 | 可行性 | 说明 |
|------|--------|------|
| A. 暴力破解密码哈希 | 低 | 专有哈希算法，无法确认算法细节 |
| B. 移除密码保护（保留加密源码） | 中 | 移除 .oem 中的认证信息，但源码仍加密无法读取 |
| C. 移除密码保护 + 清除加密源码 | 中 | FB 变为空壳（仅保留接口，丢失实现代码） |
| D. 开发 .smc2 解析工具 | 高 | 可完整解析项目结构、变量、程序列表等 |
| E. 从 PLC 上传 | 高 | 如果 FB 已下载到 PLC，可从 PLC 上传获取编译后代码 |

## 提议方案

开发一个 Python 命令行工具 `smc2_tool.py`，提供以下功能：

### 功能 1：解析 .smc2 文件结构
- 列出项目信息（名称、作者、PLC 型号、创建时间）
- 列出所有程序和 FB 块（名称、类型、是否有密码保护）
- 提取变量声明（从 SLWD 格式文件）
- 提取 FB 接口定义（输入/输出/InOut 变量）

### 功能 2：密码信息提取
- 显示所有受密码保护的 FB 列表
- 显示密码哈希值
- 尝试常见密码字典破解

### 功能 3：密码保护移除（需用户确认）
- **方案 B**：仅移除 .oem 中的认证信息（源码仍加密，Sysmac Studio 可能仍无法打开）
- **方案 C**：移除认证信息 + 将 EncryptedFile 替换为空 FB 模板（丢失实现代码，但 FB 可在 Sysmac Studio 中打开编辑）
- 操作前自动备份原文件

### 实现细节

**文件**：`c:\Users\fubai\Desktop\My_Workspace\smc2_tool.py`

**核心逻辑**：
1. 使用 `zipfile` 打开 .smc2
2. 解析 `.oem` 文件获取项目树结构（Entity 层级）
3. 解析 `.manifest` 获取项目元数据
4. 解析 XML 文件获取变量声明和程序内容
5. 解析 SLWD 格式文件获取变量定义
6. 解析 JSON 格式文件（`{"CLs":...}`）获取梯形图逻辑
7. 修改 .oem 文件移除认证信息
8. 替换 EncryptedFile 为空模板
9. 重新打包为 .smc2

**依赖**：仅 Python 标准库（zipfile, xml.etree.ElementTree, json, hashlib, base64, re, argparse, shutil, tempfile）

## 假设与决策

1. **假设**：用户拥有该项目的合法权限（自己是作者或获得授权）
2. **决策**：密码移除操作必须先备份，且需用户二次确认
3. **决策**：优先实现解析功能，密码移除作为可选功能
4. **假设**：移除密码后 Sysmac Studio 能正常打开修改后的项目（需实际验证）
5. **风险**：修改 .smc2 内部文件后，Sysmac Studio 可能因校验和不匹配而拒绝打开

## 验证步骤

1. 运行工具解析 `模板_1.smc2`，确认能正确列出所有 FB 和程序
2. 确认密码保护信息正确提取
3. 执行密码移除操作后，用 Sysmac Studio 打开修改后的文件验证
4. 确认备份文件完整
