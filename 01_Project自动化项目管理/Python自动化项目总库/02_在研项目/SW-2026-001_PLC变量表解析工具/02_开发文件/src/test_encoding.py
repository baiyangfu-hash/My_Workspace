import csv

file_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\02_在研项目\ZD-2026-001_自动搬运输送机\02_各工作流模块\WF-01_物料输送_皮带输送机_变频调速控制\01_FB组件库\FB_1010_PositioningProcessing（产品定位加工）\产品定位加工变量表.csv'

# 尝试用GBK读取
try:
    with open(file_path, 'r', encoding='gbk', newline='') as f:
        reader = csv.DictReader(f)
        print('用GBK读取的前3行:')
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(row)
except Exception as e:
    print(f'GBK读取失败: {e}')

# 尝试用UTF-8读取
try:
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        print('\n用UTF-8读取的前3行:')
        for i, row in enumerate(reader):
            if i >= 3:
                break
            print(row)
except Exception as e:
    print(f'UTF-8读取失败: {e}')
