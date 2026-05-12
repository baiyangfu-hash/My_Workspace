# -*- coding: utf-8 -*-
"""
自定义异常模块
定义应用级别的所有自定义异常类
"""


class AppException(Exception):
    """应用基础异常类"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "status_code": self.status_code
        }


# ==================== 认证相关异常 ====================

class AuthenticationError(AppException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code="AUTHENTICATION_ERROR", status_code=401)


class AuthorizationError(AppException):
    """授权错误（权限不足）"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code="AUTHORIZATION_ERROR", status_code=403)


class TokenExpiredError(AuthenticationError):
    """Token已过期"""
    
    def __init__(self, message: str = "登录已过期，请重新登录"):
        super().__init__(message)
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """无效的Token"""
    
    def __init__(self, message: str = "无效的认证信息"):
        super().__init__(message)
        self.code = "INVALID_TOKEN"


# ==================== 验证相关异常 ====================

class ValidationError(AppException):
    """参数验证错误"""
    
    def __init__(self, message: str = "参数验证失败", field: str = None):
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)
    
    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.field:
            result["field"] = self.field
        return result


class BusinessValidationError(ValidationError):
    """业务逻辑验证错误"""
    
    def __init__(self, message: str = "业务验证失败"):
        super().__init__(message)
        self.code = "BUSINESS_VALIDATION_ERROR"


# ==================== 资源相关异常 ====================

class NotFoundError(AppException):
    """资源不存在错误"""
    
    def __init__(self, message: str = "资源不存在", resource_type: str = None):
        self.resource_type = resource_type
        super().__init__(message, code="NOT_FOUND", status_code=404)


class ProjectNotFoundError(NotFoundError):
    """项目不存在"""
    
    def __init__(self, project_id: str = None):
        message = f"项目不存在" + (f": {project_id}" if project_id else "")
        super().__init__(message, resource_type="project")


class TemplateNotFoundError(NotFoundError):
    """模板不存在"""
    
    def __init__(self, template_id: str = None):
        message = f"模板不存在" + (f": {template_id}" if template_id else "")
        super().__init__(message, resource_type="template")


class DuplicateResourceError(AppException):
    """资源重复错误"""
    
    def __init__(self, message: str = "资源已存在"):
        super().__init__(message, code="DUPLICATE_RESOURCE", status_code=409)


# ==================== 数据库相关异常 ====================

class DatabaseError(AppException):
    """数据库操作错误"""
    
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, code="DATABASE_ERROR", status_code=500)


class ConnectionError(DatabaseError):
    """数据库连接错误"""
    
    def __init__(self, message: str = "数据库连接失败"):
        super().__init__(message)
        self.code = "CONNECTION_ERROR"


class TransactionError(DatabaseError):
    """事务错误"""
    
    def __init__(self, message: str = "事务执行失败"):
        super().__init__(message)
        self.code = "TRANSACTION_ERROR"


# ==================== 文件操作相关异常 ====================

class FileOperationError(AppException):
    """文件操作错误"""
    
    def __init__(self, message: str = "文件操作失败"):
        super().__init__(message, code="FILE_OPERATION_ERROR", status_code=500)


class ResourceNotFoundError(FileOperationError):
    """文件/资源不存在"""
    
    def __init__(self, file_path: str = None):
        message = f"文件不存在" + (f": {file_path}" if file_path else "")
        super().__init__(message)
        self.code = "FILE_NOT_FOUND"
        self.status_code = 404


class PermissionDeniedError(FileOperationError):
    """权限不足"""
    
    def __init__(self, message: str = "没有操作权限"):
        super().__init__(message)
        self.code = "PERMISSION_DENIED"
        self.status_code = 403


# ==================== 配置相关异常 ====================

class ConfigError(AppException):
    """配置错误"""
    
    def __init__(self, message: str = "配置错误"):
        super().__init__(message, code="CONFIG_ERROR", status_code=500)


class MissingConfigError(ConfigError):
    """缺少必要配置"""
    
    def __init__(self, config_key: str = None):
        message = f"缺少必要配置" + (f": {config_key}" if config_key else "")
        super().__init__(message)
        self.code = "MISSING_CONFIG"


# ==================== 外部服务相关异常 ====================

class ExternalServiceError(AppException):
    """外部服务调用错误"""
    
    def __init__(self, message: str = "外部服务调用失败", service_name: str = None):
        self.service_name = service_name
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", status_code=502)


class TimeoutError(ExternalServiceError):
    """超时错误"""
    
    def __init__(self, message: str = "请求超时"):
        super().__init__(message)
        self.code = "TIMEOUT_ERROR"
        self.status_code = 504


# ==================== 导出所有异常 ====================

__all__ = [
    # 基础异常
    "AppException",
    
    # 认证相关
    "AuthenticationError",
    "AuthorizationError",
    "TokenExpiredError",
    "InvalidTokenError",
    
    # 验证相关
    "ValidationError",
    "BusinessValidationError",
    
    # 资源相关
    "NotFoundError",
    "ProjectNotFoundError",
    "TemplateNotFoundError",
    "DuplicateResourceError",
    
    # 数据库相关
    "DatabaseError",
    "ConnectionError",
    "TransactionError",
    
    # 文件操作相关
    "FileOperationError",
    "ResourceNotFoundError",
    "PermissionDeniedError",
    
    # 配置相关
    "ConfigError",
    "MissingConfigError",
    
    # 外部服务相关
    "ExternalServiceError",
    "TimeoutError",
]
