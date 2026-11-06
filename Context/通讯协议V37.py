AFM_protocol_V37 = {
  "registers": {
    "REG01": {
      "address": "00000001",
      "name_zh": "复位所有寄存器",
      "description": "将该寄存器赋为1时，则所有寄存器恢复默认值",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "无操作",
        "1": "执行复位"
      }
	  },
	  "REG02": {
      "address": "00000002",
      "name": "纳米台X方向位置",
      "description": "该电压值为作为dac输出的数值，代表了纳米台的X坐标。该坐标作为：扫描模式的起始位置X坐标；其他模式下X坐标。",
      "type": "parameter", 
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG03": {
      "address": "00000003",
      "name": "纳米台Y方向位置",
      "description": "该电压值为作为dac输出的数值，代表了纳米台的Y坐标。该坐标作为：扫描模式的起始位置Y坐标；其他模式下Y坐标",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG04": {
      "address": "00000004",
      "name_zh": "AO1_L电压范围选择,X",
      "description": "设置dac输出电压范围:设置为0：±10V；设置为1：±5V；设置为2：±1V",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "±10V",
        "1": "±5V",
		    "2": "±1V"
      }
	  },
	  "REG05": {
      "address": "00000005",
      "name_zh": "AO2_L电压范围选择,Y",
      "description": "设置dac输出电压范围:设置为0：±10V；设置为1：±5V；设置为2：±1V",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "±10V",
        "1": "±5V",
		    "2": "±1V"
      }
	  },
	  "REG06": {
      "address": "00000006",
      "name_zh": "AO3_L电压范围选择,Z",
      "description": "设置dac输出电压范围:设置为0：±10V；设置为1：±5V；设置为2：±1V",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "±10V",
        "1": "±5V",
		    "2": "±1V"
      }
	  },
	  "REG07": {
      "address": "00000007",
      "name_zh": "AO4_L电压范围选择",
      "description": "设置dac输出电压范围:设置为0：±10V；设置为1：±5V；设置为2：±1V",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "±10V",
        "1": "±5V",
		    "2": "±1V"
      }
	  },
	  "REG08": {
      "address": "00000008",
      "name": "正弦波振幅",
      "description": "该寄存器作为：正弦波输出模式振幅；扫频模式振幅；力曲线测试振幅；探针轻敲情况下的扫描模式的正弦波振幅；探针轻敲情况下的自动进针模式的正弦波振幅",
      "type": "parameter",  
      "range": [0, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG09": {
      "address": "00000009",
      "name": "探针轻敲模式下的停止阈值",
      "description": "作为使用探针轻敲模式的以下模式的停止阈值：力曲线测试模式；自动进针模式",
      "type": "parameter",  
      "range": [0, 10],
      "default": 9.9999,
      "step": 0.0001
    },
	  "REG0A": {
      "address": "0000000A",
      "name": "探针接触模式下的停止阈值",
      "description": "使用接触模式下的阈值：力曲线测试模式，采用相对阈值；自动进针模式，采用相对阈值",
      "type": "parameter",  
      "range": [0, 10],
      "default": 9.9999,
      "step": 0.0001
    },
	  "REG0B": {
      "address": "0000000B",
      "name_zh": "探针模式选择",
      "description": "模式列表：1：接触；3：PFM；0：轻敲；4：MFM；8：EFM；10：KPFM-AM；15：STM。注：各种模式被FPGA主控识别时为二进制，因此模式编号已说明此种模式是基于那种扫描方式，转为二进制最低位为0的表示基于轻敲模式，为1的表示基于接触模式",
      "type": "switch",
      "default": 0,
      "options": {       
        "1": "接触模式",
        "3": "PFM模式",
		    "0": "轻敲模式",
		    "4": "MFM模式",
		    "8": "EFM模式",
		    "10": "KPFM-AM模式",
		    "15": "STM模式"
      }
	  },
	  "REG0C": {
      "address": "0000000C",
      "name": "Z电压V1",
      "description": "功能：复位时，z方向电压；定点PID模式下z方向的起始电压",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG0D": {
      "address": "0000000D",
      "name": "正弦波频率设置",
      "description": "用于设置以下模式的正弦波频率，单位赫兹：正弦波输出模式；采用探针轻敲模式的力曲线测试模式；采用探针轻敲模式的定点PID模式；采用探针轻敲模式的扫描模式；采用探针轻敲模式的自动进针模式。在探针轻敲模式时，只有扫频模式时候，正弦波频率是变动的，探针轻敲模式的其他情况下，探针的频率都是按照该寄存器设置进行波动。",
      "type": "parameter",  
      "range": [0, 1000000],
      "default": 0,
      "step": 0.0001
    },
	  "REG0E": {
      "address": "0000000E",
      "name": "状态包间隔设置",
      "description": "设置两个状态包之间的时间间隔,单位20纳秒",
      "type": "parameter",  
      "range": [1, 2147483647],
      "default": 1000000,
      "step": 1
    },
	  "REG0F": {
      "address": "0000000F",
      "name": "探针STM模式下的停止阈值",
      "description": "使用STM模式下的阈值:曲线测试模式中，采用相对阈值；自动进针模式中，采用相对阈值",
      "type": "parameter",  
      "range": [0, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG11": {
      "address": "00010001",
      "name_zh": "开始位移台单独控制",
      "description": "设置为0：无操作；设置为1：将Z方向电压设置为REG12；配置此寄存器前需提前配置REG12",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "无操作",
        "1": "将Z方向电压设置为REG12；配置此寄存器前需提前配置REG12"
      }
	  },
	  "REG12": {
      "address": "00010002",
      "name": "位移台单独控制模式-Z方向控制电压",
      "description": "位移台单独控制模式-Z方向控制电压",
      "type": "parameter", 
      "range": [-524288, 524287],
      "default": 0,
      "step": 1
    },
	  "REG14": {
      "address": "00010004",
      "name": "通道1发生时相位偏置",
      "description": "通道1发生时相位偏置",
      "type": "parameter", 
      "range": [-180, 180],
      "default": 0,
      "step": 1
    },
	  "REG15": {
      "address": "00010005",
      "name": "通道1解调时相位偏置",
      "description": "通道1解调时相位偏置",
      "type": "parameter",  
      "range": [-180, 180],
      "default": 0,
      "step": 1
    },
	  "REG16": {
      "address": "00010006",
      "name": "通道2发生时相位偏置",
      "description": "通道2发生时相位偏置",
      "type": "parameter",  
      "range": [-180, 180],
      "default": 0,
      "step": 1
    },
	  "REG17": {
      "address": "00010007",
      "name": "通道2解调时相位偏置",
      "description": "通道2解调时相位偏置",
      "type": "parameter",  
      "range": [-180, 180],
      "default": 0,
      "step": 1
    },
	  "REG19": {
      "address": "00010009",
      "name": "通道1滤波器增益系数选择",
      "description": "通道1滤波器增益系数选择",
      "type": "parameter",  
      "range": [0, 6],
      "default": 0,
      "step": 1
    },
	  "REG1A": {
      "address": "0001000A",
      "name": "通道2滤波器增益系数选择",
      "description": "通道2滤波器增益系数选择",
      "type": "parameter",  
      "range": [0, 6],
      "default": 0,
      "step": 1
    },
	  "REG1B": {
      "address": "0001000B",
      "name": "通道1累积计数",
      "description": "通道1累积计数",
      "type": "parameter",  
      "range": [0, 63],
      "default": 0,
      "step": 1
    },
	  "REG1C": {
      "address": "0001000C",
      "name": "通道2累积计数",
      "description": "通道2累积计数",
      "type": "parameter",  
      "value_type": "int32",
      "default": 0,
      "step": 1
    },
	  "REG21": {
      "address": "00020001",
      "name_zh": "传输原始数据模式",
      "description": "设置为0 ：停止传输原始数据;设置为1 ：开始传输原始数据。需先设置REG24和REG25。",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止传输原始数据",
        "1": "开始传输原始数据"
      }
	  },
	  "REG22": {
      "address": "00020002",
      "name": "Z电压最小值",
      "description": "全局使用",
      "type": "parameter",  
      "range": [-10, 10],
      "default": -10,
      "step": 0.0001
    },
	  "REG23": {
      "address": "00020003",
      "name": "Z电压最大值",
      "description": "全局使用",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 10,
      "step": 0.0001
    },
	  "REG24": {
      "address": "00020004",
      "name_zh": "传输原始数据模式-通道选择",
      "description": "0：选择高精度通道--PSD_X采集通道；1：选择高精度通道--PSD_Y采集通道；2：选择高精度通道--z实际电压通道；3：选择高精度通道--PSD_SUM采集通道；4: 选择高速通道--PSD_Y采集通道",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "选择高精度通道--PSD_X采集通道",
        "1": "选择高精度通道--PSD_Y采集通道",
		    "2": "选择高精度通道--z实际电压通道",
		    "3": "选择高精度通道--PSD_SUM采集通道",
		    "4": "选择高速通道--PSD_Y采集通道"
      }
	  },
	  "REG26": {
      "address": "00020006",
      "name": "原始数据传输速度",
      "description": "每点原始数据传输的间隔时间，单位20纳秒",
      "type": "parameter",  
      "range": [1, 1048575],
      "default": 1,
      "step": 1
    },
	  "REG31": {
      "address": "00030001",
      "name_zh": "开始轻敲扫频",
      "description": "设置为0：停止扫频；设置为1：开始扫频。配置此寄存器前需提前配置REG32至REG35，此模式的z方向电压不用处理。XY坐标为REG02,REG03",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止扫频",
        "1": "开始扫频"
      }
	  },
	  "REG32": {
      "address": "00030002",
      "name": "轻敲扫频模式-起始频率",
      "description": "轻敲扫频模式-起始频率，单位赫兹",
      "type": "parameter",  
      "range": [0, 1000000],
      "default": 0,
      "step": 0.0001
    },
	  "REG33": {
      "address": "00030003",
      "name": "轻敲扫频模式-步进频率",
      "description": "轻敲扫频模式-步进频率，单位赫兹",
      "type": "parameter",  
      "range": [0, 1000000],
      "default": 10,
      "step": 0.0001
    },
	  "REG34": {
      "address": "00030004",
      "name": "轻敲扫频模式-频率步数",
      "description": "轻敲扫频模式-频率步数",
      "type": "parameter",  
      "range": [0, 65535],
      "default": 100,
      "step": 1
    },
	  "REG35": {
      "address": "00030005",
      "name": "轻敲扫频模式-单频点固定时间",
      "description": "每一个频点保持时间，单位毫秒",
      "type": "parameter",  
      "range": [1, 1000],
      "default": 20,
      "step": 1
    },
	  "REG41": {
      "address": "00040001",
      "name_zh": "开始力曲线测试",
      "description": "设置为0：停止力曲线测试；设置为1：开始力曲线测试。配置此寄存器前需提前配置REG42 ~ REG45。纳米位移台Z方向的控制电压从z电压最小值(REG42)开始，每隔单点等待时间(REG45)时间，z电压增加z电压步进值(REG43),如果采集信号一直没有达到阈值，步数到达最大步数(REG44)之后开始回退。超过阈值是指：当前点采集到的Y信号值和初始点REG42采集到的Y信号值的差大于设置的值。Y信号值在接触模式下为光电探测器Y信号的大小REG0A，在轻敲模式下为Y信号的振动幅值REG09。如果采集信号超过阈值，则开始回退。",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止力曲线测试",
        "1": "开始力曲线测试"
      }
	  },
	  "REG42": {
      "address": "00040002",
      "name": "力曲线测试-z电压最小值",
      "description": "力曲线测试-z电压最小值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG43": {
      "address": "00040003",
      "name": "力曲线测试-z电压步进值",
      "description": "力曲线测试-z电压步进值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0.01,
      "step": 0.0001
    },
	  "REG44": {
      "address": "00040004",
      "name": "力曲线测试-最大步数",
      "description": "纳米位移台Z方向的控制电压的最大步数",
      "type": "parameter",  
      "range": [1, 65535],
      "default": 900,
      "step": 1
    },    
	  "REG45": {
      "address": "00040005",
      "name": "力曲线测试-单点等待时间",
      "description": "纳米位移台Z方向的控制电压在每一个电压点保持时间，单位微秒。由于位移台控制通道采样率为100000赫兹，该时间需要最小值为10微秒。",
      "type": "parameter",  
      "range": [10, 20000],
      "default": 100,
      "step": 10
    },
	  "REG51": {
      "address": "00050001",
      "name_zh": "开始定点PID",
      "description": "开始定点PID",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止定点PID",
        "1": "开始定点PID"
      }
	  },
	  "REG52": {
      "address": "00050002",
      "name": "PID参数-比例常数P",
      "description": "PID参数-比例常数P",
      "type": "parameter",  
      "range": [-1, 1],
      "default": -0.005,
      "step": 0.0001
    },
	  "REG53": {
      "address": "00050003",
      "name": "PID参数-积分常数I",
      "description": "PID参数-积分常数I",
      "type": "parameter",  
      "range": [-1, 1],
      "default": -0.003,
      "step": 0.0001
    },
	  "REG54": {
      "address": "00050004",
      "name": "PID参数-微分常数D",
      "description": "PID参数-微分常数D",
      "type": "parameter",  
      "range": [-1, 1],
      "default": 0,
      "step": 0.0001
    },
	  "REG55": {
      "address": "00050005",
      "name": "PID参数-限制Limit",
      "description": "增量式PID单次变化值的绝对值的最大限制",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0.05,
      "step": 0.0001
    },
	  "REG56": {
      "address": "00050006",
      "name": "PID参数-反馈目标值Setpoint",
      "description": "PID参数-反馈目标值Setpoint",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG57": {
      "address": "00050007",
      "name": "PID参数-PID反馈时间",
      "description": "PID参数-PID反馈时间，单位微秒。由于位移台控制通道采样率为100000赫兹，该时间需要最小值为10微秒。",
      "type": "parameter",  
      "range": [10, 20000],
      "default": 300,
      "step": 10
    },
	  "REG58": {
      "address": "00050008",
      "name": "单次升降时间间隔",
      "description": "单次升降时间间隔，单位20纳秒",
      "type": "parameter",  
      "range": [1, 1000000],
      "default": 5000,
      "step": 1
    },
	  "REG59": {
      "address": "00050009",
      "name_zh": "STM是否取对数",
      "description": "1为取对数，0不取",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "不取对数",
        "1": "取对数"
      }
	  },
	  "REG61": {
      "address": "00060001",
      "name_zh": "扫描模式-使能",
      "description": "设置为0：停止扫描；设置为1：开始扫描。配置此寄存器前需提前配置REG52~REG57，REG62~REG68。",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止扫描",
        "1": "开始扫描"
      }
	  },
	  "REG62": {
      "address": "00060002",
      "name": "扫描模式-扫描前进针等待时间",
      "description": "扫描模式-扫描前进针等待时间，单位毫秒",
      "type": "parameter",  
      "range": [1, 10000],
      "default": 300,
      "step": 1
    },
	  "REG63": {
      "address": "00060003",
      "name": "扫描模式-X方向扫描电压范围",
      "description": "扫描模式-X方向扫描电压范围，单位伏特，5um的扫描长度对应1V的电压变化",
      "type": "parameter",  
      "range": [0, 10],
      "default": 2,
      "step": 0.001
    },
	  "REG64": {
      "address": "00060004",
      "name": "扫描模式-Y方向扫描电压范围",
      "description": "扫描模式-Y方向扫描电压范围，单位伏特，5um的扫描长度对应1V的电压变化",
      "type": "parameter",  
      "range": [0, 10],
      "default": 2,
      "step": 0.001
    },
	  "REG65": {
      "address": "00060005",
      "name": "扫描模式-X方向移动次数",
      "description": "扫描模式-X方向移动次数",
      "type": "parameter",  
      "range": [1, 65535],
      "default": 512,
      "step": 1
    },
	  "REG66": {
      "address": "00060006",
      "name": "扫描模式-Y方向移动次数",
      "description": "扫描模式-Y方向移动次数",
      "type": "parameter",  
      "range": [1, 65535],
      "default": 512,
      "step": 1
    },
	  "REG67": {
      "address": "00060007",
      "name": "每点PID次数",
      "description": "每点PID次数",
      "type": "parameter",  
      "range": [1, 65535],
      "default": 4,
      "step": 1
    },
	  "REG68": {
      "address": "00060008",
      "name": "二次扫描抬起高度",
      "description": "二次扫描抬起高度,为电压值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0.035,
      "step": 0.0001
    },
	  "REG69": {
      "address": "00060009",
      "name": "二次扫描抬起单点时间",
      "description": "二次扫描抬起单点时间,单位微秒",
      "type": "parameter",  
      "range": [1, 10000],
      "default": 500,
      "step": 1
    },
	  "REG6A": {
      "address": "0006000A",
      "name": "DC偏压大小",
      "description": "DC偏压大小",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG6B": {
      "address": "0006000B",
      "name": "二次扫描抬起单点次数",
      "description": "二次扫描抬起单点次数",
      "type": "parameter",  
      "range": [1, 32767],
      "default": 15,
      "step": 1
    },
	  "REG6C": {
      "address": "0006000C",
      "name": "二次扫描抬起升降速度",
      "description": "二次扫描抬起升降速度，单位纳米/次",
      "type": "parameter",  
      "range": [1, 100000],
      "default": 800,
      "step": 1
    },
	  "REG6D": {
      "address": "0006000D",
      "name": "二次抬起扫描完成后，落下后等待时间",
      "description": "二次抬起扫描完成后，落下后等待时间,单位微秒",
      "type": "parameter",  
      "range": [1, 10000],
      "default": 100,
      "step": 1
    },
	  "REG6E": {
      "address": "0006000E",
      "name": "二次抬起扫描完成前，抬起后等待时间",
      "description": "二次抬起扫描完成前，抬起后等待时间,单位微秒",
      "type": "parameter",  
      "range": [1, 10000],
      "default": 100,
      "step": 1
    },
	  "REG6F": {
      "address": "0006000F",
      "name_zh": "扫描顺逆时针切换",
      "description": "0为逆时针，1为顺时针",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "逆时针",
        "1": "顺时针"
      }
	  },
	  "REG71": {
      "address": "00070001",
      "name_zh": "自动进针-使能",
      "description": "设置为0：停止自动进针；设置为1：开始自动进针。配置此寄存器前需提前配置REG72。自动进针过程中，只有开始设置初始电压REG73，以及反馈超过阈值时z方向电压设置成REG72,其他时候FPGA只负责反馈，并不对z电压进行改变。",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止自动进针",
        "1": "开始自动进针"
      }
	  },
	  "REG72": {
      "address": "00070002",
      "name": "自动进针-V2",
      "description": "单位伏特，探针轻敲模式下，当光电探测器Y信号的振幅变化量超过停止阈值时，将纳米位移台z方向的控制电压设为V2。探针接触模式下，当光电探测器Y信号的变化量超过停止阈值时，将纳米位移台z方向的控制电压设为V2。",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG73": {
      "address": "00070003",
      "name": "自动进针-V3",
      "description": "V3:自动进针模式下z方向的起始电压",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 2,
      "step": 0.0001
    },
	  "REG74": {
      "address": "00070004",
      "name": "信号稳定时间",
      "description": "信号稳定该时间后，判断为进上了针，单位20纳秒",
      "type": "parameter",  
      "range": [50, 50000],
      "default": 500,
      "step": 1
    },
	  "REG81": {
      "address": "00080001",
      "name": "蝴蝶曲线DC偏压起始值",
      "description": "蝴蝶曲线的DC电压起始值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG82": {
      "address": "00080001",
      "name": "蝴蝶曲线DC偏压步长",
      "description": "蝴蝶曲线DC电压步长",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0,
      "step": 0.0001
    },
	  "REG83": {
      "address": "00080003",
      "name": "蝴蝶曲线单点次数",
      "description": "蝴蝶曲线单点次数。单点时间=单点次数*PID时间。蝴蝶曲线和PFM扫频都复用了PID的计数",
      "type": "parameter",  
      "range": [1, 32767],
      "default": 5,
      "step": 1
    },
	  "REG84": {
      "address": "00080004",
      "name": "蝴蝶曲线步数",
      "description": "蝴蝶曲线步数",
      "type": "parameter",  
      "range": [1, 32767],
      "default": 20,
      "step": 1
    },
	  "REG85": {
      "address": "00080005",
      "name_zh": "开始蝴蝶曲线",
      "description": "设置为1时开始扫描，设置为0时终止扫描（必须在定点pid反馈模式下）",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止扫描蝴蝶曲线",
        "1": "开始扫描蝴蝶曲线"
      }
	  },
	  "REG86": {
      "address": "00080005",
      "name_zh": "开始PFM扫频",
      "description": "置为1时开始扫描，设置为0时终止扫描（必须在pid反馈模式下，扫频参数复用REG32-REG35）",
      "type": "switch",
      "default": 0,
      "options": {       
        "0": "停止PFM扫频",
        "1": "开始PFM扫频"
      }
	  },    
	  "REG87": {
      "address": "00080007",
      "name": "AC-PID参数-比例常数P",
      "description": "AM-KPFM的P参数",
      "type": "parameter",  
      "range": [-1, 1],
      "default": 0.05,
      "step": 0.0001
    },
	  "REG88": {
      "address": "00080008",
      "name": "AC-PID参数-积分常数I",
      "description": "AM-KPFM的I参数",
      "type": "parameter",  
      "range": [-1, 1],
      "default": 0.03,
      "step": 0.0001
    },
	  "REG89": {
      "address": "00080009",
      "name": "AC-PID参数-微分常数D",
      "description": "AM-KPFM的D参数",
      "type": "parameter",  
      "range": [-1, 1],
      "default": 0,
      "step": 0.0001
    },
	  "REG8A": {
      "address": "0008000A",
      "name": "AC-PID参数-限制Limit",
      "description": "AM-KPFM的增量式PID单次变化值的绝对值的最大限制",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 0.03,
      "step": 0.0001
    },
	  "REG8B": {
      "address": "0008000B",
      "name": "DC最小值",
      "description": "DC输出的最小值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": -10,
      "step": 0.0001
    },
	  "REG8C": {
      "address": "0008000C",
      "name": "DC最大值",
      "description": "DC输出的最大值",
      "type": "parameter",  
      "range": [-10, 10],
      "default": 10,
      "step": 0.0001
    },
	  "REG8E": {
      "address": "0008000E",
      "name": "AC频率&抬起后",
      "description": "PFM的振动频率，KPFM-AM、MFM、EFM抬起时使用的频率，处理方式与REG0D相同",
      "type": "parameter",  
      "range": [0, 1000000],
      "default": 0,
      "step": 0.0001
    },
	  "REG8F": {
      "address": "0008000F",
      "name": "AC振幅&抬起后",
      "description": "PFM的电压振幅，KPFM-AM、MFM、EFM抬起时使用的电压振幅，处理方式与REG08相同",
      "type": "parameter",  
      "range": [0, 10],
      "default": 0,
      "step": 0.0001
    }  
  }
}
