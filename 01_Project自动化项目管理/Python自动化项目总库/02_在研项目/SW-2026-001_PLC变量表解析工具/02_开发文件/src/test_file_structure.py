import csv

file_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\02_在研项目\ZD-2026-001_自动搬运输送机\02_各工作流模块\WF-01_物料输送_皮带输送机_变频调速控制\01_FB组件库\FB_1010_PositioningProcessing（产品定位加工）\产品定位加工变量表-10测试 - 修改前.csv'

# 检测文件编码
import chardet
with open(file_path, 'rb') as f:
    content = f.read()
    result = chardet.detect(content)
    encoding = result['encoding']
    print(f'文件编码: {encoding}')

# 读取文件内容
with open(file_path, 'r', encoding=encoding, newline='') as f:
    reader = csv.DictReader(f)
    print(f'字段名: {reader.fieldnames}')
    print('\n前5行数据:')
    for i, row in enumerate(reader):
        if i >= 5:
            break
        print(row)
