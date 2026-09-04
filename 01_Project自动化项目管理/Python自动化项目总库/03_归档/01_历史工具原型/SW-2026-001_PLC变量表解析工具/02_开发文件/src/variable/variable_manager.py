from .variable import Variable

class VariableManager:
    """
    变量管理器类，用于管理变量列表
    """
    
    def __init__(self):
        """
        初始化变量管理器
        """
        self.variables = []
    
    def add_variable(self, variable):
        """
        添加变量
        
        Args:
            variable (Variable): 变量对象
            
        Returns:
            bool: 是否添加成功
        """
        if not isinstance(variable, Variable):
            raise TypeError("参数必须是Variable类型")
        
        if not variable.validate():
            return False
        
        # 检查变量名是否重复
        if any(v.name == variable.name for v in self.variables):
            return False
        
        self.variables.append(variable)
        return True
    
    def delete_variable(self, index):
        """
        删除变量
        
        Args:
            index (int): 变量索引
            
        Returns:
            bool: 是否删除成功
        """
        if 0 <= index < len(self.variables):
            self.variables.pop(index)
            return True
        return False
    
    def edit_variable(self, index, variable):
        """
        编辑变量
        
        Args:
            index (int): 变量索引
            variable (Variable): 新变量对象
            
        Returns:
            bool: 是否编辑成功
        """
        if not isinstance(variable, Variable):
            raise TypeError("参数必须是Variable类型")
        
        if not variable.validate():
            return False
        
        if 0 <= index < len(self.variables):
            # 检查变量名是否与其他变量重复
            if any(v.name == variable.name for i, v in enumerate(self.variables) if i != index):
                return False
            
            self.variables[index] = variable
            return True
        return False
    
    def get_variable(self, index):
        """
        获取变量
        
        Args:
            index (int): 变量索引
            
        Returns:
            Variable: 变量对象
        """
        if 0 <= index < len(self.variables):
            return self.variables[index]
        return None
    
    def get_variables(self):
        """
        获取所有变量
        
        Returns:
            list: 变量列表
        """
        return self.variables
    
    def set_variables(self, variables):
        """
        设置变量列表
        
        Args:
            variables (list): 变量列表
        """
        for var in variables:
            if not isinstance(var, Variable):
                raise TypeError("列表中的元素必须是Variable类型")
        self.variables = variables
    
    def clear(self):
        """
        清空变量列表
        """
        self.variables.clear()
    
    def sort_variables(self, key="name", reverse=False):
        """
        排序变量
        
        Args:
            key (str): 排序键
            reverse (bool): 是否倒序
        """
        if key in ["name", "address", "type", "scope"]:
            self.variables.sort(key=lambda v: getattr(v, key), reverse=reverse)
    
    def filter_variables(self, key, value):
        """
        筛选变量
        
        Args:
            key (str): 筛选键
            value (str): 筛选值
            
        Returns:
            list: 筛选后的变量列表
        """
        if key in ["name", "address", "type", "comment", "scope"]:
            return [v for v in self.variables if value.lower() in str(getattr(v, key)).lower()]
        return self.variables
