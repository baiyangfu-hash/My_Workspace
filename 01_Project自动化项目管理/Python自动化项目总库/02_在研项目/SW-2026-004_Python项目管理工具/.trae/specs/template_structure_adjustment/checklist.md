# Checklist

- [x] TPL-SINGLE-PLC-001 的 structure 一级目录为 00_项目管理 ~ 07_工具与配置 连续编号，无跳号
- [x] TPL-SINGLE-PLC-001 的所有 templates[].path 文件名中不含 `{` 占位符字符
- [x] TPL-SINGLE-PLC-001 的 templates[].content 内容中保留 {project_name} 等占位符（用于内容替换）
- [x] TPL-SINGLE-PLC-001 的 02_PLC程序/ 下含 主程序/功能块/变量表/模块配置/程序文档 子目录
- [x] TPL-SINGLE-PLC-001 的每个二级子目录有对应的说明性 .md 文件
- [x] TPL-FULLLINE-AUTO-001 文件名无占位符、目录编号连续（修复07回退）
- [x] TPL-SINGLE-ROBOT-001 文件名无占位符、目录编号连续（修复07回退+扩展机器人子目录）
- [x] TPL-UPGRADE-STD-001 文件名无占位符、5处已清除
- [x] template_editor.py 添加文件对话框提示"文件名不需要加占位符"
- [x] constants.py 无 Python 语法错误 (LSP检查通过，0诊断)
- [x] 5个模板的 structure 路径与 templates 路径前缀一致（目录树能正确加载）
