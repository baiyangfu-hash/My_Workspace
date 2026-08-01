import sys
sys.path.insert(0, '01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具')
from auto_pm.utils.file_utils import read_file
c = read_file('c:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化/DJ-2026-005/04_监控/01_变更管理/01_变更单/CHG-DOCU/CHG-DOCU-2026-002.md')
lines = c.splitlines()
for i,l in enumerate(lines):
    s = l.strip()
    if s.startswith('### 10.') or s.startswith('| # |') or s.startswith('|---') or s.startswith('| | ') or s.startswith('| 1') or s.startswith('| 2') or s.startswith('| 3'):
        print(f'{i}: {s}')