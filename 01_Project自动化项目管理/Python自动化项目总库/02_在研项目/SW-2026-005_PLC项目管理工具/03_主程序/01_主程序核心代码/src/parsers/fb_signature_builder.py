# -*- coding: utf-8 -*-
"""
FB接口签名构建器

从FB的SCL源码中提取完整的接口定义(VAR_INPUT/VAR_OUTPUT/VAR_IN_OUT/VAR)，
构建结构化的FBInterfaceSignature对象供检查器使用。

能力:
- 解析FUNCTION_BLOCK/FUNCTION声明
- 按类别提取变量: VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR(局部)
- 识别默认值、RETAIN属性、行内注释
- 批量扫描项目目录构建签名字典
"""
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.parsers.st_parser import STParser, VarCategory, VariableInfo, POUType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class VarDef:
    """FB接口中的单个变量定义"""

    name: str
    data_type: str
    has_default: bool = False
    default_value: Optional[str] = None
    is_retain: bool = False
    comment: str = ""
    line_number: int = 0


@dataclass
class FBInterfaceSignature:
    """FB完整接口签名"""

    fb_name: str
    fb_type: str = "FUNCTION_BLOCK"
    inputs: List[VarDef] = field(default_factory=list)
    outputs: List[VarDef] = field(default_factory=list)
    in_outs: List[VarDef] = field(default_factory=list)
    vars: List[VarDef] = field(default_factory=list)
    source_file: str = ""

    @property
    def input_names(self) -> List[str]:
        return [v.name for v in self.inputs]

    @property
    def output_names(self) -> List[str]:
        return [v.name for v in self.outputs]

    @property
    def inout_names(self) -> List[str]:
        return [v.name for v in self.in_outs]

    @property
    def all_param_names(self) -> List[str]:
        return self.input_names + self.inout_names + self.output_names

    def get_var_def(self, name: str) -> Optional[VarDef]:
        lower = name.lower()
        for v in self.inputs + self.outputs + self.in_outs + self.vars:
            if v.name.lower() == lower:
                return v
        return None

    def get_input_by_name(self, name: str) -> Optional[VarDef]:
        lower = name.lower()
        for v in self.inputs:
            if v.name.lower() == lower:
                return v
        return None

    def get_output_by_name(self, name: str) -> Optional[VarDef]:
        lower = name.lower()
        for v in self.outputs:
            if v.name.lower() == lower:
                return v
        return None

    def get_inout_by_name(self, name: str) -> Optional[VarDef]:
        lower = name.lower()
        for v in self.in_outs:
            if v.name.lower() == lower:
                return v
        return None

    @property
    def total_pin_count(self) -> int:
        return len(self.inputs) + len(self.outputs) + len(self.in_outs)


class FBSignatureBuilder:
    """
    FB签名构建器

    基于STParser提取POU信息后，按VAR类别重组为FBInterfaceSignature。
    支持单文件解析和项目级批量构建。
    """

    RE_SCL_FILE = re.compile(r"\.scl$", re.IGNORECASE)
    RE_RETAIN_MARKER = re.compile(
        r"VAR(?:_\w+)?\s+(RETAIN|PERSISTENT)",
        re.IGNORECASE,
    )

    @classmethod
    def build_from_scl(cls, scl_source: str, source_file: str = "") -> FBInterfaceSignature:
        """
        从SCL源码文本构建FB签名

        Args:
            scl_source: FB的.scl文件完整内容
            source_file: 来源文件路径（可选）

        Returns:
            FBInterfaceSignature: 结构化FB签名，解析失败时返回空签名
        """
        parser = STParser()

        try:
            pous, _global_vars = parser.parse(scl_source)
        except Exception as e:
            logger.warning(f"SCL解析异常 ({source_file}): {e}")
            return cls._empty_signature(source_file)

        if not pous:
            logger.warning(f"未找到POU定义: {source_file}")
            return cls._empty_signature(source_file)

        pou = pous[0]
        signature = FBInterfaceSignature(
            fb_name=pou.name,
            fb_type=pou.pou_type.value,
            source_file=source_file,
        )

        retain_vars = cls._find_retain_vars(scl_source)

        for var in pou.variables:
            var_def = VarDef(
                name=var.name,
                data_type=var.data_type,
                has_default=var.initial_value is not None,
                default_value=var.initial_value,
                is_retain=var.name.lower() in {v.lower() for v in retain_vars},
                comment=var.comment,
                line_number=var.line_number,
            )

            category = var.category
            if category == VarCategory.VAR_INPUT:
                signature.inputs.append(var_def)
            elif category == VarCategory.VAR_OUTPUT:
                signature.outputs.append(var_def)
            elif category == VarCategory.VAR_IN_OUT:
                signature.in_outs.append(var_def)
            else:
                signature.vars.append(var_def)

        logger.debug(
            f"签名构建完成: {pou.name} "
            f"(IN={len(signature.inputs)}, "
            f"OUT={len(signature.outputs)}, "
            f"IN_OUT={len(signature.in_outs)}, "
            f"VAR={len(signature.vars)})"
        )
        return signature

    @classmethod
    def build_from_file(cls, scl_file_path: str) -> FBInterfaceSignature:
        """
        从.scl文件路径构建FB签名

        Args:
            scl_file_path: .scl文件的绝对/相对路径

        Returns:
            FBInterfaceSignature: FB签名
        """
        with open(scl_file_path, "r", encoding="utf-8") as f:
            source = f.read()

        return cls.build_from_scl(source, source_file=str(scl_file_path))

    @classmethod
    def build_project_signatures(
        cls,
        project_path: str,
        syslib_path: Optional[str] = None,
    ) -> Dict[str, FBInterfaceSignature]:
        """
        扫描项目目录中所有.scl文件，批量构建FB签名字典

        Args:
            project_path: 项目根目录路径
            syslib_path: SysLib库路径（可选，会额外扫描）

        Returns:
            Dict[str, FBInterfaceSignature]: {fb_name_lower: signature}
        """
        signatures: Dict[str, FBInterfaceSignature] = {}
        search_paths = [project_path]

        if syslib_path and os.path.isdir(syslib_path):
            search_paths.append(syslib_path)

        for base_path in search_paths:
            if not os.path.isdir(base_path):
                continue

            for root, _dirs, files in os.walk(base_path):
                for fname in files:
                    if not cls.RE_SCL_FILE.search(fname):
                        continue

                    fpath = os.path.join(root, fname)
                    try:
                        sig = cls.build_from_file(fpath)
                        key = sig.fb_name.lower()
                        if key and key not in signatures:
                            signatures[key] = sig
                            logger.debug(f"注册签名: {sig.fb_name} <- {fpath}")
                    except Exception as e:
                        logger.warning(f"跳过无法解析的文件 {fpath}: {e}")

        logger.info(f"项目签名构建完成: 共{len(signatures)}个FB签名")
        return signatures

    @staticmethod
    def _empty_signature(source_file: str = "") -> FBInterfaceSignature:
        return FBInterfaceSignature(fb_name="", source_file=source_file)

    @staticmethod
    def _find_retain_vars(scl_source: str) -> List[str]:
        """从源码中提取带RETAIN/PERSISTENT属性的变量名"""
        results: List[str] = []
        pattern = re.compile(
            r"VAR(?:_\w+)?\s+(?:RETAIN|PERSISTENT|NON_RETAIN)\s*",
            re.IGNORECASE,
        )
        var_decl_pattern = re.compile(
            r"(?P<names>[\w\s,]+?)\s*:\s*(?P<type>\w+)"
            r"(?:\s*:=\s*(?P<init>[^;]*?))?\s*;",
            re.IGNORECASE,
        )

        for match in pattern.finditer(scl_source):
            pos = match.start()
            var_block_start = scl_source.rfind("VAR", 0, pos)
            var_block_end = scl_source.find("END_VAR", pos)
            if var_block_start == -1 or var_block_end == -1:
                continue
            block = scl_source[var_block_start:var_block_end]
            for decl in var_decl_pattern.finditer(block):
                names_str = decl.group("names").strip()
                for name in [n.strip() for n in names_str.split(",")]:
                    name_upper = name.strip().upper()
                    if name_upper and name_upper not in (
                        "VAR", "END_VAR", "RETAIN",
                        "PERSISTENT", "NON_RETAIN",
                    ):
                        results.append(name.strip())

        return results
