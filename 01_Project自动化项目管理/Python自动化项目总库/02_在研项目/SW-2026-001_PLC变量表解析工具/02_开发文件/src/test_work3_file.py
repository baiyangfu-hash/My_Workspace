import csv

file_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3.csv'

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
