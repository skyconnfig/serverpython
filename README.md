# Ollama 压力测试工具

一个专业的 Ollama 模型性能压力测试工具，支持多线程并发测试、实时监控和详细的性能报告生成。

## 功能特性

- 🚀 **多线程并发测试** - 支持自定义并发线程数进行压力测试
- 📊 **实时性能监控** - 实时显示 TPS、RPS、延迟等关键指标
- 🖥️ **系统资源监控** - 监控 CPU、内存、GPU 使用率和温度
- 📈 **可视化报告** - 自动生成图表和详细的测试报告
- 🎯 **自定义测试参数** - 灵活配置模型、测试时长、并发数等参数
- 📝 **多样化提示词** - 支持自定义提示词文件进行测试

## 项目结构

```
├── debug/
│   ├── ollama_stress_test.py    # 主要的压力测试脚本
│   ├── 准备启动.py               # 环境准备和依赖安装脚本
│   ├── 运行脚本.py               # 快速启动脚本
│   └── prompts.txt              # 测试用提示词文件
├── .vscode/
│   └── settings.json            # VSCode 配置文件
└── README.md                    # 项目说明文档
```

## 安装依赖

运行准备脚本安装所需依赖：

```bash
python debug/准备启动.py
```

或手动安装依赖：

```bash
pip install ollama pandas matplotlib psutil pynvml
```

## 使用方法

### 1. 基础使用

```bash
python debug/ollama_stress_test.py
```

### 2. 自定义参数测试

```bash
# 设置环境变量进行自定义测试
MODEL_NAME="deepseek-r1:32b" \
TEST_DURATION=300 \
CONCURRENT_THREADS=12 \
python debug/ollama_stress_test.py
```

### 3. 使用快速启动脚本

```bash
python debug/运行脚本.py
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MODEL_NAME` | `deepseek-r1:32b` | 要测试的 Ollama 模型名称 |
| `TEST_DURATION` | `600` | 测试持续时间（秒） |
| `CONCURRENT_THREADS` | `8` | 并发线程数 |
| `TEMPERATURE` | `0.7` | 模型生成温度 |
| `MAX_TOKENS` | `512` | 最大生成 token 数 |
| `PROMPT_FILE` | `prompts.txt` | 提示词文件路径 |

## 测试指标

### 性能指标
- **TPS (Tokens Per Second)** - 每秒生成的 token 数
- **RPS (Requests Per Second)** - 每秒处理的请求数
- **平均延迟** - 单个请求的平均响应时间
- **成功率** - 请求成功的百分比

### 系统监控
- **CPU 使用率** - 处理器使用情况
- **内存使用率** - 系统内存占用
- **GPU 利用率** - 显卡计算资源使用
- **GPU 温度** - 显卡温度监控
- **显存使用率** - 显存占用情况

## 输出文件

测试完成后会生成以下文件：

- `ollama_stress_test_YYYYMMDD_HHMMSS_requests.csv` - 详细的请求记录
- `ollama_stress_test_YYYYMMDD_HHMMSS_system.csv` - 系统资源使用记录
- `ollama_stress_test_YYYYMMDD_HHMMSS_report.json` - 测试摘要报告
- `ollama_stress_test_YYYYMMDD_HHMMSS_report.png` - 可视化性能图表

## 自定义提示词

编辑 `debug/prompts.txt` 文件添加自定义测试提示词：

```
解释量子计算的基本原理
用Python实现快速排序算法
写一篇关于人工智能未来发展的短文
如何优化深度学习模型的训练速度?
比较RESTful API和GraphQL的优缺点
```

## 系统要求

- Python 3.7+
- Ollama 服务已安装并运行
- NVIDIA GPU（用于 GPU 监控功能）
- 足够的系统内存和显存

## 注意事项

1. 确保 Ollama 服务正在运行：`ollama serve`
2. 测试前确认目标模型已下载：`ollama pull model_name`
3. 高并发测试可能消耗大量系统资源，请根据硬件配置调整参数
4. GPU 温度监控需要 NVIDIA 显卡和相应驱动

## 故障排除

### 常见问题

1. **连接错误** - 确保 Ollama 服务正在运行
2. **模型未找到** - 使用 `ollama list` 检查已安装的模型
3. **GPU 监控失败** - 检查 NVIDIA 驱动和 pynvml 安装
4. **内存不足** - 降低并发线程数或选择较小的模型

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

## 许可证

MIT License