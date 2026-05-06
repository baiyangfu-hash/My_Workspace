class Variable:
    """
    变量类，用于存储PLC变量的信息
    """
    
    def __init__(self, name, address, type_, comment="", scope="Global", array_size=1, struct_members=None):
        """
        初始化变量
        
        Args:
            name (str): 变量名称
            address (str): 变量地址
            type_ (str): 变量类型
            comment (str): 变量注释
            scope (str): 变量作用域
            array_size (int): 数组大小，非数组为1
            struct_members (list): 结构体成员，非结构体为None
        """
        if not name:
            raise ValueError("变量名称不能为空")
        if not address:
            raise ValueError("变量地址不能为空")
        if not type_:
            raise ValueError("变量类型不能为空")
        
        self.name = name
        self.address = address
        self.type = type_
        self.comment = comment
        self.scope = scope
        self.array_size = array_size
        self.struct_members = struct_members
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 变量信息字典
        """
        return {
            "name": self.name,
            "address": self.address,
            "type": self.type,
            "comment": self.comment,
            "scope": self.scope,
            "array_size": self.array_size,
            "struct_members": self.struct_members
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        从字典创建变量
        
        Args:
            data (dict): 变量信息字典
            
        Returns:
            Variable: 变量对象
        """
        return cls(
            name=data.get("name"),
            address=data.get("address"),
            type_=data.get("type"),
            comment=data.get("comment", ""),
            scope=data.get("scope", "Global"),
            array_size=data.get("array_size", 1),
            struct_members=data.get("struct_members")
        )
    
    def validate(self):
        """
        验证变量有效性
        
        Returns:
            bool: 是否有效
        """
        if not self.name or not self.address or not self.type:
            return False
        if self.array_size < 1:
            return False
        return True
    
    def __str__(self):
        """
        字符串表示
        
        Returns:
            str: 变量字符串表示
        """
        return f"{self.name} ({self.type}) - {self.address} - {self.comment}"
    
    def __repr__(self):
        """
        repr表示
        
        Returns:
            str: 变量repr表示
        """
        return f"Variable(name='{self.name}', address='{self.address}', type='{self.type}')"
