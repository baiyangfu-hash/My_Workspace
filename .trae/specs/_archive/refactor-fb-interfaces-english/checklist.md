# Checklist - FB接口变量名英文化重构

## Task 1: FB_ExternalDeviceInteraction 验证
- [ ] 文件头版本号已更新为 V5.0.0
- [ ] VAR_INPUT 区域27个变量名全部为英文（无中文残留）
- [ ] VAR_OUTPUT 区域20个变量名全部为英文（无中文残留）
- [ ] 内部实现代码中所有变量引用已同步更新（无TC001错误风险）
- [ ] 内部VAR区域变量名已更新
- [ ] 变更记录文档已创建

## Task 2: FB_1003_PickPlace 验证
- [ ] 文件头版本号已更新为 V5.0.0
- [ ] VAR_INPUT 区域55个变量名全部为英文（无中文残留）
- [ ] VAR_OUTPUT 区域30个变量名全部为英文（无中文残留）
- [ ] 内部实现代码中所有变量引用已同步更新（无TC001错误风险）
- [ ] 内部VAR/VAR_CONSTANT区域变量名已更新
- [ ] 变更记录文档已创建

## Task 3: 全局集成验证
- [ ] OB1.scl 调用 fbExternalDevice 的参数与FB接口100%匹配
- [ ] OB1.scl 调用 fbPickPlace 的参数与FB接口100%匹配
- [ ] GlobalVars.db V3.0.0 变量名与OB1调用参数一致
- [ ] 整个项目Grep搜索：`i_b使能|o_b运行中|i_b组框机|q_b允许抓料|i_bZ轴点动` 等中文模式返回0结果
- [ ] 总变更记录V5.0.0已更新（追加本次修复内容）
