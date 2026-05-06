from utils.encoding_detector import EncodingDetector

file_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\02_在研项目\ZD-2026-001_自动搬运输送机\02_各工作流模块\WF-01_物料输送_皮带输送机_变频调速控制\01_FB组件库\FB_1010_PositioningProcessing（产品定位加工）\产品定位加工变量表-10测试 - 修改前.csv'

# 测试编码检测器
encoding = EncodingDetector.detect_encoding(file_path)
print(f'编码检测器检测结果: {encoding}')

# 直接使用chardet检测
import chardet
with open(file_path, 'rb') as f:
    content = f.read()
    result = chardet.detect(content)
    print(f'直接chardet检测结果: {result}')
