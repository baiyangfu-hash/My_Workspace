// 输送线控制FB块 - 基于IEC 61131-3标准
// 功能：双位置检测、气缸伸缩控制、上游进料禁止
// 输入变量：
//   i_Sensor1 - 一号位置传感器（X0）
//   i_Sensor2 - 二号位置传感器（X1）
//   i_AutoMode - 自动模式（X2）
//   i_ManualMode - 手动模式（X3）
//   i_Reset - 复位信号（X4）
//   i_CylinderExtendCmd - 气缸伸出命令（X5）
//   i_CylinderRetractCmd - 气缸缩回命令（X6）
//   i_AllowIn - 允许进料（主控→工位）
//   i_AllowOut - 允许出料（主控→工位）
//   i_SysAutoMode - 系统自动模式（主控→所有设备）
//   i_SysResetRequest - 系统复位请求（操作员→主控）
//   i_Robot_CurrentStation - 机械手当前所在工位
//   i_Robot_Carrying - 机械手是否携带产品
//   i_Robot_TaskAck - 机械手任务完成确认
// 输出变量：
//   q_CylinderExtend - 气缸伸出输出（Y0）
//   q_CylinderRetract - 气缸缩回输出（Y1）
//   q_FeedBlock - 上游进料禁止（Y2）
//   q_IsReady - 工位就绪（Y3）
//   q_HasPart - 有料检测（Y4）
//   q_ErrorActive - 故障报警（Y5）
//   q_ErrorCode - 错误代码（D100）
//   q_RequestPick - 请求取料（工位→主控）
//   q_RequestPlace - 请求放料（工位→主控）
//   q_ProcessDone - 加工完成（工位→主控）
//   q_SysConveyorReady - 输送线就绪（输送线→主控）
//   q_ConveyorReady - 输送线就绪（输送线→主控）
// 内部变量：
//   tmp_nState - 状态机当前状态（D101）
//   tmp_Timer1, tmp_Timer2 - 计时器（T100, T110）
//   tmp_bLastSensor1, tmp_bLastSensor2 - 上一次传感器状态（M100, M101）
//   tmp_bProductID - 产品ID（如 SN20250111A001）
//   tmp_nProcessStep - 当前工艺步骤
//   q_ErrorCode - 错误代码（0=无错）
//   tmp_bSysEmergencyStop - 系统急停信号
// 状态定义：
//   0: 初始化状态
//   1: 等待产品状态
//   2: 一号位置有产品状态
//   3: 二号位置有产品状态
//   4: 两个位置都有产品状态
//FUNCTION_BLOCK FB_ConveyorLineControl
// 程序主体
//BEGIN
// 初始化模块：复位处理
IF i_Reset THEN
	tmp_nState := 0;
	q_CylinderExtend := FALSE;
	q_CylinderRetract := TRUE; // 复位时气缸缩回
	q_FeedBlock := FALSE;
	q_IsReady := FALSE;
	q_HasPart := FALSE;
	q_ErrorActive := FALSE;
	q_ErrorCode := 0;
	tmp_bLastSensor1 := i_Sensor1;
	tmp_bLastSensor2 := i_Sensor2;
	// [2026-01-14] 添加：上下游交互变量初始化
	q_RequestPick := FALSE;
	q_RequestPlace := FALSE;
	q_ProcessDone := FALSE;
	q_SysConveyorReady := FALSE;
	q_ConveyorReady := FALSE;
	tmp_nProcessStep := 0;
	tmp_bProductID := '';
	RETURN;
END_IF;

// 手动控制模块
IF i_ManualMode THEN
	
	// 手动模式下，气缸根据命令直接动作
	IF i_CylinderExtendCmd AND NOT i_CylinderRetractCmd THEN
		q_CylinderExtend := TRUE;
		q_CylinderRetract := FALSE;
		ELSIF i_CylinderRetractCmd AND NOT i_CylinderExtendCmd THEN
		q_CylinderExtend := FALSE;
		q_CylinderRetract := TRUE;
		
	END_IF;
            
	// 手动模式下，进料禁止由两个传感器状态决定
	q_FeedBlock := i_Sensor1 AND i_Sensor2;
            
	// 更新状态输出
	q_IsReady := TRUE;
	q_HasPart := i_Sensor1 OR i_Sensor2;
	q_ErrorActive := FALSE;
	q_ErrorCode := 0;
	
	// [2026-01-14] 添加：上下游交互状态更新
	q_SysConveyorReady := TRUE;
	q_ConveyorReady := TRUE;
	q_RequestPick := FALSE;
	q_RequestPlace := FALSE;
	q_ProcessDone := FALSE;
	
END_IF;

// 自动运行模块：状态机控制
IF i_AutoMode THEN
	CASE tmp_nState OF
		// 初始化状态
		0:
		q_CylinderExtend := FALSE;
		q_CylinderRetract := TRUE;
		q_FeedBlock := FALSE;
		q_IsReady := FALSE;
		q_HasPart := FALSE;
		q_SysConveyorReady := TRUE;
		q_ConveyorReady := TRUE;
		
		// [2026-01-14] 添加：初始化上下游交互状态
		q_RequestPick := FALSE;
		q_RequestPlace := FALSE;
		
		// 检查传感器状态，进入相应状态
		IF i_Sensor1 AND i_Sensor2 THEN
			tmp_nState := 4; // 两个位置都有产品
			ELSIF i_Sensor1 THEN
			tmp_nState := 2; // 一号位置有产品
			ELSIF i_Sensor2 THEN
			tmp_nState := 3; // 二号位置有产品
			ELSE
			tmp_nState := 1; // 进入等待产品状态
		END_IF;
                
		// 等待产品状态
		1:
		q_IsReady := TRUE;
		q_HasPart := FALSE;
		q_SysConveyorReady := TRUE;
		q_ConveyorReady := TRUE;
		
		// [2026-01-14] 添加：初始化上下游交互状态
		q_RequestPick := FALSE;
		q_RequestPlace := FALSE;
		
		// 当一号位置有产品时
		IF i_Sensor1 THEN
			tmp_nState := 2;
			// 当二号位置有产品时
			ELSIF i_Sensor2 THEN
			tmp_nState := 3;
			ELSE
			// 两个位置都没有产品，气缸伸出
			q_CylinderExtend := TRUE;
			q_CylinderRetract := FALSE;
			// [2026-01-14] 添加：根据主控允许进料信号控制
			q_FeedBlock := NOT i_AllowIn;
		END_IF;
                
		// 一号位置有产品状态
		2:
		// 气缸收回
		q_CylinderExtend := FALSE;
		q_CylinderRetract := TRUE;
		q_HasPart := TRUE;
		q_SysConveyorReady := TRUE;
		q_ConveyorReady := TRUE;
		
		// [2026-01-14] 添加：请求机械手取料
		q_RequestPick := TRUE;
		q_RequestPlace := FALSE;
		
		// 检查二号位置是否有产品
		IF i_Sensor2 THEN
			tmp_nState := 4;  // 进入两个位置都有产品状态
			// 如果一号位置产品离开
			ELSIF NOT i_Sensor1 THEN
			tmp_nState := 1;  // 回到等待产品状态
			// [2026-01-14] 添加：机械手取料完成后状态更新
			ELSIF i_Robot_CurrentStation = 1 AND i_Robot_Carrying AND i_Robot_TaskAck THEN
			tmp_nState := 1;  // 回到等待产品状态
			q_RequestPick := FALSE;
		END_IF;
                
		// 二号位置有产品状态
		3:
		q_HasPart := TRUE;
		q_SysConveyorReady := TRUE;
		q_ConveyorReady := TRUE;
		
		// [2026-01-14] 添加：请求机械手取料
		q_RequestPick := TRUE;
		q_RequestPlace := FALSE;
		
		// 检查一号位置是否有产品
		IF i_Sensor1 THEN
			tmp_nState := 4;  // 进入两个位置都有产品状态
			// 如果二号位置产品离开
			ELSIF NOT i_Sensor2 THEN
			tmp_nState := 1;  // 回到等待产品状态
			// [2026-01-14] 添加：机械手取料完成后状态更新
			ELSIF i_Robot_CurrentStation = 2 AND i_Robot_Carrying AND i_Robot_TaskAck THEN
			tmp_nState := 1;  // 回到等待产品状态
			q_RequestPick := FALSE;
		END_IF;
                
		// 两个位置都有产品状态
		4:
		// 气缸收回
		q_CylinderExtend := FALSE;
		q_CylinderRetract := TRUE;
		// 禁止上游进料
		q_FeedBlock := TRUE;
		q_HasPart := TRUE;
		q_SysConveyorReady := TRUE;
		q_ConveyorReady := TRUE;
		
		// [2026-01-14] 添加：请求机械手取料
		q_RequestPick := TRUE;
		q_RequestPlace := FALSE;
		
		// 检查是否有产品离开
		IF NOT i_Sensor1 THEN
			tmp_nState := 3;  // 回到只有二号位置有产品状态
			// [2026-01-14] 添加：更新取料请求
			q_RequestPick := TRUE;
			ELSIF NOT i_Sensor2 THEN
			tmp_nState := 2;  // 回到只有一号位置有产品状态
			// [2026-01-14] 添加：更新取料请求
			q_RequestPick := TRUE;
		END_IF;
	END_CASE;
	ELSE
	// 非自动非手动模式，默认状态
	q_CylinderExtend := FALSE;
	q_CylinderRetract := TRUE;
	q_FeedBlock := FALSE;
	q_IsReady := FALSE;
	q_HasPart := i_Sensor1 OR i_Sensor2;
	// [2026-01-14] 添加：非自动非手动模式下的上下游交互状态
	q_SysConveyorReady := FALSE;
	q_ConveyorReady := FALSE;
	q_RequestPick := FALSE;
	q_RequestPlace := FALSE;
	q_ProcessDone := FALSE;
END_IF;

// 报警处理模块
// [2026-01-14] 添加：更新报警处理逻辑
q_ErrorActive := FALSE;
q_ErrorCode := 0;

// 检查系统急停
IF tmp_bSysEmergencyStop THEN
	q_ErrorActive := TRUE;
	q_ErrorCode := 1001; // 系统急停错误代码
END_IF;

// 更新上一次传感器状态
tmp_bLastSensor1 := i_Sensor1;
tmp_bLastSensor2 := i_Sensor2;

// 定时器更新（单独模块）
// 计时器1：未使用，保持默认状态
tmp_Timer1(IN:=In_tTimer1, PT:=PT_tTimer1, Q=> Q_tTimer1, ET=> ET_tTimer1);
// 计时器2：未使用，保持默认状态
tmp_Timer2(IN:=In_tTimer2, PT:=PT_tTimer2, Q=> Q_tTimer2, ET=> ET_tTimer2);

// [2026-01-14] 添加：上下游交互逻辑模块
// 1. 主控→工位信号处理
// 系统自动模式使能
IF i_SysAutoMode THEN
	// 自动模式下的额外处理
	q_SysConveyorReady := TRUE;
	ELSE
	q_SysConveyorReady := FALSE;
END_IF;

// 系统复位请求处理
IF i_SysResetRequest THEN
	// 系统复位逻辑
	q_ErrorActive := FALSE;
	q_ErrorCode := 0;
	q_ProcessDone := FALSE;
END_IF;

// 2. 工位→主控信号处理
// 更新工位就绪状态
q_IsReady := (i_Sensor1 OR i_Sensor2) AND NOT q_ErrorActive;

// 更新加工完成状态
// 当产品在工位上且没有错误时，加工完成
IF q_HasPart AND NOT q_ErrorActive THEN
	q_ProcessDone := TRUE;
	ELSE
	q_ProcessDone := FALSE;
END_IF;

// 3. 机械手交互逻辑
// 当机械手到达当前工位且携带产品时，请求放料
IF i_Robot_CurrentStation = 1 AND i_Robot_Carrying AND NOT i_Sensor1 THEN
	q_RequestPlace := TRUE;
	q_RequestPick := FALSE;
	ELSIF i_Robot_CurrentStation = 2 AND i_Robot_Carrying AND NOT i_Sensor2 THEN
	q_RequestPlace := TRUE;
	q_RequestPick := FALSE;
END_IF;

// 4. 产品ID和工艺步骤更新
// 当有新的产品进入工位时，更新产品ID和工艺步骤
IF (i_Sensor1 AND NOT tmp_bLastSensor1) OR (i_Sensor2 AND NOT tmp_bLastSensor2) THEN
	// 模拟产品ID更新（实际应从主控获取）
	tmp_bProductID := 'SN20250114A001';
	// 模拟工艺步骤更新（实际应从主控获取）
	tmp_nProcessStep := 1; // 1=点胶, 2=压合...
END_IF;

//END_FUNCTION_BLOCK

// FB块实例化示例
// VAR
//     fbConveyor : FB_ConveyorLineControl;
// END_VAR

// // 调用示例
// fbConveyor(
//     i_Sensor1 := X0,                    // 一号位置传感器
//     i_Sensor2 := X1,                    // 二号位置传感器
//     i_AutoMode := X2,                   // 自动模式
//     i_ManualMode := X3,                 // 手动模式
//     i_Reset := X4,                      // 复位信号
//     i_CylinderExtendCmd := X5,          // 气缸伸出命令
//     i_CylinderRetractCmd := X6,         // 气缸缩回命令
//     // [2026-01-14] 添加：上下游交互输入
//     i_AllowIn := M20,                   // 允许进料（主控→工位）
//     i_AllowOut := M21,                  // 允许出料（主控→工位）
//     i_SysAutoMode := M100,              // 系统自动模式（主控→所有设备）
//     i_SysResetRequest := X1,            // 系统复位请求（操作员→主控）
//     i_Robot_CurrentStation := D101,     // 机械手当前所在工位
//     i_Robot_Carrying := M200,           // 机械手是否携带产品
//     i_Robot_TaskAck := M201,            // 机械手任务完成确认
//     // 输出变量
//     q_CylinderExtend => Y0,             // 气缸伸出输出
//     q_CylinderRetract => Y1,            // 气缸缩回输出
//     q_FeedBlock => Y2,                  // 上游进料禁止
//     q_IsReady => Y3,                    // 工位就绪
//     q_HasPart => Y4,                    // 有料检测
//     q_ErrorActive => Y5,                // 故障报警
//     q_ErrorCode => D100,                // 错误代码
//     // [2026-01-14] 添加：上下游交互输出
//     q_RequestPick => M30,               // 请求取料（工位→主控）
//     q_RequestPlace => M31,              // 请求放料（工位→主控）
//     q_ProcessDone => M32,               // 加工完成（工位→主控）
//     q_SysConveyorReady => M201,         // 输送线就绪（输送线→主控）
//     q_ConveyorReady => M202             // 输送线就绪（输送线→主控）
// );
;