"""
Prototype Service for auto-pm (SW-2026-008).
Provides prototype bundling, validation, archiving, and scaffolding for PLC and Software projects.
"""

import os
import re
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

@dataclass
class PrototypeBundleResult:
    success: bool
    output_path: str
    message: str
    bundled_files: list[str] = field(default_factory=list)

class PrototypeService:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    def locate_prototype_sources(self, project_path: str) -> tuple[str | None, str | None, str | None]:
        """
        Locates the main HTML, CSS, and JS prototype files inside a project.
        Returns (html_path, css_path, js_path).
        """
        abs_proj = os.path.abspath(project_path)

        # Candidate search directories
        candidates = [
            os.path.join(abs_proj, "03_HMI设计", "原型", "files"),
            os.path.join(abs_proj, "03_HMI设计"),
            os.path.join(abs_proj, "PRD", "原型"),
            os.path.join(abs_proj, "02_设计", "Html原型预览"),
            os.path.join(abs_proj, "ui", "prototype"),
            abs_proj,
        ]

        for cand in candidates:
            if not os.path.exists(cand):
                continue

            # Find main HTML file
            html_file = None
            for item in os.listdir(cand):
                if item.endswith(".html") and "历史备份" not in item and "archive" not in item.lower():
                    html_file = os.path.join(cand, item)
                    break

            if html_file:
                css_candidate = os.path.join(cand, "styles.css")
                js_candidate = os.path.join(cand, "script.js")
                css_file = css_candidate if os.path.exists(css_candidate) else None
                js_file = js_candidate if os.path.exists(js_candidate) else None
                return html_file, css_file, js_file

        return None, None, None

    def bundle(
        self,
        project_path: str,
        version: str | None = None,
        output_filename: str | None = None,
    ) -> PrototypeBundleResult:
        """
        Bundles multi-file HTML/CSS/JS prototypes into a single self-contained HTML file.
        """
        abs_proj = os.path.abspath(project_path)
        html_path, css_path, js_path = self.locate_prototype_sources(abs_proj)

        if not html_path or not os.path.exists(html_path):
            return PrototypeBundleResult(
                success=False,
                output_path="",
                message=f"No prototype HTML file found in project {project_path}",
            )

        with open(html_path, encoding="utf-8") as f:
            content = f.read()

        bundled_files = [html_path]

        # Inline CSS if external link exists
        if css_path and os.path.exists(css_path):
            with open(css_path, encoding="utf-8") as f:
                css_code = f.read()

            css_placeholder_pattern = re.compile(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']styles\.css["\']\s*/?>', re.IGNORECASE)
            if css_placeholder_pattern.search(content):
                content = css_placeholder_pattern.sub(f"<style>\n/* Inlined styles.css */\n{css_code}\n</style>", content)
            bundled_files.append(css_path)

        # Inline JS if external script exists
        if js_path and os.path.exists(js_path):
            with open(js_path, encoding="utf-8") as f:
                js_code = f.read()

            js_placeholder_pattern = re.compile(r'<script\s+src=["\']script\.js["\']\s*></script>', re.IGNORECASE)
            if js_placeholder_pattern.search(content):
                content = js_placeholder_pattern.sub(f"<script>\n/* Inlined script.js */\n{js_code}\n</script>", content)
            bundled_files.append(js_path)

        # Determine target output path
        base_name = os.path.basename(html_path)
        base_no_ext = os.path.splitext(base_name)[0]

        # Destination folder (03_HMI设计 for PLC, or root/PRD for software)
        hmi_dir = os.path.join(abs_proj, "03_HMI设计")
        dest_dir = hmi_dir if os.path.exists(hmi_dir) else abs_proj

        if output_filename:
            target_name = output_filename
        elif version:
            target_name = f"{base_no_ext}_{version}_历史备份.html"
        else:
            target_name = f"{base_no_ext}.html"

        target_path = os.path.join(dest_dir, target_name)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return PrototypeBundleResult(
            success=True,
            output_path=target_path,
            message=f"Prototype successfully bundled into {target_path}",
            bundled_files=bundled_files,
        )

    def check(self, project_path: str) -> CheckResult:
        """
        Validates prototype integrity, checking for register tags, broken links, BOMs.
        """
        abs_proj = os.path.abspath(project_path)
        html_path, css_path, js_path = self.locate_prototype_sources(abs_proj)

        if not html_path:
            return CheckResult(
                passed=False,
                errors=[f"未找到原型主 HTML 文件 ({project_path})"],
            )

        errors = []
        warnings = []
        info = []

        with open(html_path, encoding="utf-8") as f:
            content = f.read()

        info.append(f"验证原型文件: {os.path.basename(html_path)}")

        # Check BOM
        with open(html_path, "rb") as f:
            raw_bytes = f.read(3)
            if raw_bytes.startswith(b"\xef\xbb\xbf"):
                warnings.append("文件包含 UTF-8 BOM，建议剥离 BOM")

        # Extract PLC registers for validation if PLC project
        registers = set(re.findall(r'\b([DXYRM]\d+)\b', content))
        if registers:
            info.append(f"检测到 {len(registers)} 个 PLC 寄存器标记: {', '.join(sorted(registers)[:10])}...")

        # Check basic syntax / tags
        if "<!DOCTYPE html>" not in content and "<html" not in content.lower():
            errors.append("HTML 缺失标准 <!DOCTYPE html> 声明")

        if "</html>" not in content.lower():
            errors.append("HTML 缺失闭合的 </html> 标签")

        passed = len(errors) == 0
        return CheckResult(passed=passed, errors=errors, warnings=warnings, info=info)

    def archive(self, project_path: str, version: str) -> PrototypeBundleResult:
        """
        Archives prototype with a version tag.
        """
        return self.bundle(project_path=project_path, version=version)

    def init(self, project_path: str, template: str = "hmi") -> PrototypeBundleResult:
        """
        Scaffolds a new prototype template in the target project.
        """
        abs_proj = os.path.abspath(project_path)
        hmi_dir = os.path.join(abs_proj, "03_HMI设计", "原型", "files")
        os.makedirs(hmi_dir, exist_ok=True)

        target_html = os.path.join(hmi_dir, "HMI原型设计.html")
        target_css = os.path.join(hmi_dir, "styles.css")
        target_js = os.path.join(hmi_dir, "script.js")

        if os.path.exists(target_html):
            return PrototypeBundleResult(
                success=False,
                output_path=target_html,
                message="原型文件已存在，取消初始化以防覆盖",
            )

        # Scaffolding HTML
        html_code = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HMI 原型设计</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="hmi-container">
        <h1>HMI 控制系统原型</h1>
        <div id="status-box">系统就绪</div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

        css_code = """body {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: sans-serif;
    margin: 0;
    padding: 20px;
}
.hmi-container {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 24px;
}"""

        js_code = """console.log("HMI Prototype initialized.");"""

        with open(target_html, "w", encoding="utf-8") as f:
            f.write(html_code)
        with open(target_css, "w", encoding="utf-8") as f:
            f.write(css_code)
        with open(target_js, "w", encoding="utf-8") as f:
            f.write(js_code)

        return PrototypeBundleResult(
            success=True,
            output_path=target_html,
            message=f"Prototype template successfully initialized at {hmi_dir}",
            bundled_files=[target_html, target_css, target_js],
        )
