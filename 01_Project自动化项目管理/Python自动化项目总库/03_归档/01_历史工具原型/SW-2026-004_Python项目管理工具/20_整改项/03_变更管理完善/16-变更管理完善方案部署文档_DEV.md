# 变更管理完善方案 - 部署文档

## 1. 部署概述

**文档版本**: V1.0.0
**部署日期**: 2026-03-15
**部署人员**: 智能体技术负责人

## 2. 部署前准备

### 2.1 环境检查
- [ ] Python环境已安装（建议3.8+）
- [ ] 数据库服务正常运行
- [ ] 现有系统已备份
- [ ] 部署权限已获取

### 2.2 依赖检查
- [ ] PyQt5已安装
- [ ] SQLAlchemy已安装
- [ ] 其他依赖包已安装

### 2.3 数据备份
```bash
# 备份数据库
mysqldump -u username -p database_name > backup_$(date +%Y%m%d).sql

# 备份代码
tar -czf code_backup_$(date +%Y%m%d).tar.gz /path/to/project
```

## 3. 部署步骤

### 3.1 数据库迁移

1. **执行迁移脚本**
```bash
cd /path/to/project/03_主程序/01_主程序核心代码
python migrations/migrate_approval_history_and_impact.py
```

2. **验证表创建**
```sql
-- 检查审批历史表
SHOW TABLES LIKE 'approval_histories';

-- 检查影响评估表
SHOW TABLES LIKE 'impact_assessments';

-- 查看表结构
DESC approval_histories;
DESC impact_assessments;
```

3. **验证外键约束**
```sql
-- 检查外键是否正确创建
SELECT 
    TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE 
    TABLE_SCHEMA = 'your_database'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    AND TABLE_NAME IN ('approval_histories', 'impact_assessments');
```

### 3.2 代码部署

1. **部署新增文件**
```
新增文件:
- src/services/approval_service.py
- src/dao/approval_dao.py
- tests/test_approval_history_and_impact.py
- tests/verify_new_code.py
- migrations/migrate_approval_history_and_impact.py
```

2. **部署修改文件**
```
修改文件:
- src/services/change_service.py
- src/ui/widgets/change_manager.py
```

3. **部署规范文档**
```
更新文档:
- 01_全局规范/04_监控和控制/01_变更管理/变更管理规范/042_通用变更管理流程规范_PM-V1.1.0.md
- 01_全局规范/04_监控和控制/01_变更管理/变更管理规范/045_变更管理流程执行指南_PM-V1.0.0.md
- 01_全局规范/04_监控和控制/01_变更管理/变更管理规范/043_通用变更管理目录结构说明_PM-V1.1.0.md
```

### 3.3 配置更新

无需额外配置，新功能自动启用。

## 4. 部署验证

### 4.1 功能验证

#### 4.1.1 审批历史功能
- [ ] 创建变更单
- [ ] 提交审批
- [ ] 审批通过
- [ ] 查看审批历史标签页
- [ ] 验证审批历史记录正确

#### 4.1.2 影响分析功能
- [ ] 创建变更单
- [ ] 查看影响分析标签页
- [ ] 验证风险等级显示
- [ ] 验证受影响组件显示
- [ ] 验证缓解措施显示

#### 4.1.3 集成测试
- [ ] 完整的变更流程测试
- [ ] 审批历史和影响分析同时验证
- [ ] UI响应速度测试

### 4.2 数据验证

```sql
-- 验证审批历史数据
SELECT COUNT(*) FROM approval_histories;

-- 验证影响评估数据
SELECT COUNT(*) FROM impact_assessments;

-- 验证数据关联
SELECT 
    c.change_id,
    c.title,
    COUNT(DISTINCT ah.history_id) as approval_count,
    COUNT(DISTINCT ia.assessment_id) as impact_count
FROM 
    changes c
LEFT JOIN 
    approval_histories ah ON c.change_id = ah.change_id
LEFT JOIN 
    impact_assessments ia ON c.change_id = ia.change_id
GROUP BY 
    c.change_id, c.title;
```

### 4.3 性能验证

- [ ] 数据库查询响应时间 < 1秒
- [ ] UI页面加载时间 < 2秒
- [ ] 审批操作响应时间 < 1秒
- [ ] 影响分析执行时间 < 3秒

### 4.4 日志验证

```bash
# 检查应用日志
tail -f logs/app.log | grep -E "审批历史|影响分析"

# 检查错误日志
tail -f logs/error.log

# 检查数据库日志
tail -f /var/log/mysql/error.log
```

## 5. 回滚方案

### 5.1 数据库回滚
```sql
-- 删除新增的表
DROP TABLE IF EXISTS approval_histories;
DROP TABLE IF EXISTS impact_assessments;
```

### 5.2 代码回滚
```bash
# 恢复代码备份
tar -xzf code_backup_YYYYMMDD.tar.gz -C /path/to/project

# 恢复数据库
mysql -u username -p database_name < backup_YYYYMMDD.sql
```

### 5.3 回滚触发条件
- 数据库迁移失败
- 功能验证失败
- 性能严重下降
- 出现严重Bug

## 6. 监控指标

### 6.1 关键指标

| 指标 | 目标值 | 监控方法 |
|------|--------|----------|
| 数据库查询时间 | < 1秒 | 应用日志 |
| UI响应时间 | < 2秒 | 性能监控 |
| 审批操作成功率 | > 99% | 业务日志 |
| 影响分析成功率 | > 99% | 业务日志 |
| 系统可用性 | > 99.9% | 监控系统 |

### 6.2 告警规则

- 数据库连接失败 → 立即告警
- 审批历史记录失败 → 立即告警
- 影响分析执行失败 → 立即告警
- 查询响应时间 > 3秒 → 警告告警
- 系统错误率 > 1% → 警告告警

## 7. 部署后检查清单

- [ ] 数据库迁移成功
- [ ] 所有文件已部署
- [ ] 功能验证通过
- [ ] 数据验证通过
- [ ] 性能验证通过
- [ ] 日志验证通过
- [ ] 监控系统已配置
- [ ] 回滚方案已准备
- [ ] 用户已通知
- [ ] 文档已更新

## 8. 常见问题处理

### 8.1 数据库迁移失败
**问题**: 表创建失败
**解决**: 
1. 检查数据库权限
2. 检查表是否已存在
3. 检查外键约束是否正确

### 8.2 审批历史不显示
**问题**: 审批历史标签页为空
**解决**:
1. 检查数据库连接
2. 检查approval_histories表数据
3. 检查UI代码是否正确部署

### 8.3 影响分析失败
**问题**: 影响分析显示错误
**解决**:
1. 检查impact_assessments表
2. 检查ImpactService代码
3. 检查日志中的错误信息

### 8.4 性能下降
**问题**: 系统响应变慢
**解决**:
1. 检查数据库索引
2. 检查查询语句
3. 考虑添加缓存

## 9. 联系方式

| 角色 | 姓名 | 邮箱 | 电话 |
|------|------|------|------|
| 技术负责人 | [姓名] | [邮箱] | [电话] |
| 数据库管理员 | [姓名] | [邮箱] | [电话] |
| 运维负责人 | [姓名] | [邮箱] | [电话] |

## 10. 附录

### 10.1 部署时间估算

| 阶段 | 预估时间 | 实际时间 |
|------|----------|----------|
| 环境准备 | 30分钟 | |
| 数据库迁移 | 15分钟 | |
| 代码部署 | 30分钟 | |
| 功能验证 | 60分钟 | |
| 性能验证 | 30分钟 | |
| 总计 | 165分钟 | |

### 10.2 部署检查清单

部署前:
- [ ] 备份完成
- [ ] 环境检查完成
- [ ] 依赖检查完成
- [ ] 回滚方案准备完成

部署中:
- [ ] 数据库迁移成功
- [ ] 代码部署成功
- [ ] 配置更新成功

部署后:
- [ ] 功能验证通过
- [ ] 数据验证通过
- [ ] 性能验证通过
- [ ] 监控配置完成

---

**文档版本**: V1.0.0
**部署日期**: 2026-03-15
**部署人员**: 智能体技术负责人
