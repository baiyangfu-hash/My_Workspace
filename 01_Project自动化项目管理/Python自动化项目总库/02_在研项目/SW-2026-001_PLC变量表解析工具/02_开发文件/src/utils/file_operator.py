import csv
import json
import os

class FileOperator:
    """
    文件操作工具类，用于文件读写操作
    """
    
    @staticmethod
    def read_file(file_path, encoding='utf-8'):
        """
        读取文件
        
        Args:
            file_path (str): 文件路径
            encoding (str): 编码
            
        Returns:
            str: 文件内容
        """
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(file_path, content, encoding='utf-8'):
        """
        写入文件
        
        Args:
            file_path (str): 文件路径
            content (str): 文件内容
            encoding (str): 编码
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def read_csv(file_path, encoding='utf-8'):
        """
        读取CSV文件
        
        Args:
            file_path (str): 文件路径
            encoding (str): 编码
            
        Returns:
            list: CSV数据
        """
        data = []
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def write_csv(file_path, data, encoding='utf-8'):
        """
        写入CSV文件
        
        Args:
            file_path (str): 文件路径
            data (list): 数据列表
            encoding (str): 编码
            
        Returns:
            bool: 是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if not data:
                return False
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def read_json(file_path, encoding='utf-8'):
        """
        读取JSON文件
        
        Args:
            file_path (str): 文件路径
            encoding (str): 编码
            
        Returns:
            dict: JSON数据
        """
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    
    @staticmethod
    def write_json(file_path, data, encoding='utf-8', indent=2):
        """
        写入JSON文件
        
        Args:
            file_path (str): 文件路径
            data (dict): 数据
            encoding (str): 编码
            indent (int): 缩进
            
        Returns:
            bool: 是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception:
            return False
