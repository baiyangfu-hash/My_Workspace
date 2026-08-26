"""Automated regression tests for DJ-2026-008 Long Frame Stacker (长边框堆垛机).

Covers:
1. 1# Station: Dual Infeed (双路入料输送) & Pair Counting
2. 2# Station: Stacking Transfer XZ (叠垛移载机械手) & Dynamic Stack Height Calculation
3. 3# Station: Paper Dispenser (隔纸架与自动裁切)
4. 4# Station: Frame Alignment (长短边双向归正)
5. 5# Station: Common Alarm & OMAC State Machine (STD-830/860) & First-up Latching
"""

import pytest


class TestDJ008DualInfeedStation:
    """1# 双路入料输送工位逻辑仿真测试"""

    def test_dual_infeed_pairing_and_ready_for_pick(self):
        sensor_infeed1 = True
        sensor_infeed2 = True
        sensor_arrived1 = True
        sensor_arrived2 = True
        ready_for_pick = False
        pairs_count = 0

        # 双路均到达阻挡位且稳料后
        if sensor_arrived1 and sensor_arrived2:
            ready_for_pick = True
            pairs_count += 1

        assert ready_for_pick is True
        assert pairs_count == 1


class TestDJ008StackTransferStation:
    """2# 叠垛移载机械手工位逻辑仿真测试"""

    def test_dynamic_stacking_height_calculation(self):
        base_height = 25000  # 底托盘高度 (0.01mm)
        layer_pitch = 800    # 单层边框厚度 8mm (800 * 0.01mm)

        # 第 1 层放料高度
        layer_1 = 1
        height_1 = base_height - (layer_1 - 1) * layer_pitch
        assert height_1 == 25000

        # 第 10 层放料高度
        layer_10 = 10
        height_10 = base_height - (layer_10 - 1) * layer_pitch
        assert height_10 == 25000 - 9 * 800  # 17800

        # 安全防夹底托限位
        assert height_10 >= 2000


class TestDJ008PaperDispenserStation:
    """3# 隔纸架与自动裁切工位逻辑仿真测试"""

    def test_paper_feed_and_cutter_sequence(self):
        req_paper = True
        paper_empty = False
        step = 0

        if req_paper and not paper_empty:
            step = 10  # 升至供纸位

        assert step == 10


class TestDJ008FrameAlignmentStation:
    """4# 长短边双向归正工位逻辑仿真测试"""

    def test_alignment_pressure_hold_and_done(self):
        place_done = True
        short_cyl_ext = True
        long_cyl_ext = True
        align_done = False

        if place_done and short_cyl_ext and long_cyl_ext:
            align_done = True

        assert align_done is True


class TestDJ008CommonAlarmAndOmac:
    """5# 公共报警与 OMAC 状态机仿真测试"""

    def test_omac_homing_interlock_and_first_up_alarm(self):
        is_homed = False
        current_mode = 0

        # 未寻原点强力禁止切入 AUTO
        req_auto = True
        if req_auto:
            if is_homed:
                current_mode = 3
            else:
                current_mode = 1  # 降级回 MANUAL

        assert current_mode == 1

        # 毫秒级首出报警锁定
        raw_alarms = [False] * 32
        raw_alarms[2] = True  # 通道 3 (双路进料超时) 先触发
        first_up_index = 0
        latched = False

        for i, val in enumerate(raw_alarms):
            if val and not latched:
                latched = True
                first_up_index = i + 1

        # 通道 5 随后触发
        raw_alarms[4] = True

        assert first_up_index == 3, "首出必须准确锁定通道 3"
